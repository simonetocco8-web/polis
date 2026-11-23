import copy
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from demos.config import canonical, sha
from demos.snapshot import digest as demographic_hash
from demos.validation import require

from .ledger import LIMIT

CONFIG = Path(__file__).resolve().parents[1] / "config/oikonomia-1.json"
FIELDS = ("house_deposit", "firm_deposit", "government", "bank_deposit", "house_debt", "firm_debt",
          "public_debt", "bank_loans", "bank_equity", "capital", "public_capital", "inventory",
          "arrears", "active", "jobs", "employer", "staff_target", "income_history")


@dataclass
class Economy:
    demographics: object
    config: dict
    origin: str
    accounts: dict
    price: int
    journal: str
    variant: str = "baseline"

    def clone(self, name):
        return Economy(self.demographics.clone(name), copy.deepcopy(self.config), self.origin,
                       {key: value.copy() for key, value in self.accounts.items()}, self.price, self.journal, self.variant)


def zeros(n):
    return np.zeros(n, dtype="<i8")


def attach(demos, variant="baseline"):
    require(demos.month == 0, "Migration requires initial Demos snapshot")
    origin = demographic_hash(demos)
    config = json.loads(CONFIG.read_bytes())
    n, f = len(demos.households), len(demos.firms)
    p = demos.people
    # Only documented savings become opening deposits. Earnings are a wage offer
    # reference; Demos asset, debt and other income amounts are not posted.
    cash = zeros(n)
    np.add.at(cash, p["household"], p["savings"].astype(np.int64) * 100)
    capacity = demos.firms["capacity"].astype(np.int64)
    accounts = dict(house_deposit=cash, firm_deposit=zeros(f) + config["opening_firm_deposit"],
                    government=zeros(1) + config["opening_treasury_deposit"], bank_deposit=zeros(1),
                    house_debt=zeros(n), firm_debt=zeros(f), public_debt=zeros(1), bank_loans=zeros(1),
                    bank_equity=zeros(1), capital=capacity * config["opening_capital"], public_capital=zeros(1),
                    inventory=capacity * config["opening_inventory"], arrears=zeros(f),
                    active=demos.firms["active"].astype("<i8"), jobs=p["job"].astype("<i8"),
                    employer=np.where(p["job"] == 2, p["firm"], -1).astype("<i8"), staff_target=capacity.copy(), income_history=zeros(n))
    # The reserve asset includes the disclosed opening deposit counterpart.
    config["opening_reserves"] = config["bank_reserves"] + deposit_total(accounts)
    accounts["bank_equity"][0] = config["bank_reserves"]
    return Economy(demos.clone(demos.replica), config, origin, accounts, config["base_price"],
                   sha(canonical({"opening": origin, "config": config})), variant)


def deposit_total(a):
    return sum(int(a[k].sum()) for k in ("house_deposit", "firm_deposit", "government", "bank_deposit"))


def reconcile(state):
    a = state.accounts
    require(set(a) == set(FIELDS), "Unexpected economic account")
    for key, value in a.items():
        require(value.dtype == np.dtype("<i8") and value.ndim == 1 and np.all(np.abs(value.astype(np.float64)) <= LIMIT),
                f"Invalid account: {key}")
        if key not in {"employer", "bank_equity"}:
            require(np.all(value >= 0), f"Negative account: {key}")
    require(int(a["bank_loans"][0]) == sum(int(a[k].sum()) for k in ("house_debt", "firm_debt", "public_debt")), "Loan mismatch")
    require(state.config["opening_reserves"] + int(a["bank_loans"][0]) ==
            deposit_total(a) - int(a["bank_deposit"][0]) + int(a["bank_equity"][0]), "Bank balance mismatch")
    jobs, employer = a["jobs"], a["employer"]
    require(len(jobs) == len(state.demographics.people) and len(employer) == len(jobs)
            and np.all((jobs >= 0) & (jobs <= 4)), "Invalid occupations")
    require(np.all(employer[jobs == 2] >= 0) and np.all(employer[jobs != 2] == -1)
            and np.all(employer < len(a["active"])), "Invalid employers")
    linked = employer[jobs == 2]
    headcount = np.bincount(linked, minlength=len(a["active"]))
    require(np.all(a["active"][linked] == 1) and np.all(headcount <= state.demographics.firms["capacity"]), "Overstaffed or closed firm")
