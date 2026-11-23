import json
from pathlib import Path

import numpy as np

from demos.config import canonical, sha
from demos.validation import require
from oikonomia.ledger import apportion

CONFIG = Path(__file__).resolve().parents[1] / "config/stabilitas-1.json"


def configuration():
    return json.loads(CONFIG.read_bytes())


def symmetric_price(price, supply, desired, config):
    difference = desired - supply
    magnitude = config["price_response_bp"] * abs(difference) // max(1, supply, desired)
    step = -magnitude if difference < 0 else magnitude
    cents = (price * abs(step) + 5000) // 10000
    return min(config["price_max"], max(config["price_min"], price + (-cents if step < 0 else cents)))


class Policy:
    def __init__(self, factors="control", overrides=None):
        catalog = configuration()
        codes = tuple(factors.split("+")) if factors != "control" else ()
        require(len(set(codes)) == len(codes) and all(code in catalog["factor_rules"] for code in codes), "Invalid factors")
        self.factors = list(codes)
        self.params = {key: value for code in codes for key, value in catalog["factor_rules"][code].items()}
        if overrides:
            require(set(overrides) <= set(self.params), "Invalid override")
            for key, value in overrides.items():
                require(type(value) is int and value > 0 and value <= self.params[key], f"Invalid sensitivity parameter: {key}")
                self.params[key] = value
        self.entries = []
        self.first_month = None
        self.rows = []

    def opening(self, state, journal):
        a, d = state.accounts, state.demographics
        self.opening_deposits = sum(int(a[key].sum()) for key in ("house_deposit", "firm_deposit", "government"))
        self.opening_equity = int(a["bank_equity"][0])
        if d.month == 0:
            before = a["jobs"].copy()
            if "A" in self.factors:
                owners = d.firms["owner"]
                firms = np.flatnonzero(owners >= 0)
                people = owners[firms]
                staff = np.bincount(a["employer"][a["employer"] >= 0], minlength=len(owners))
                valid = ((a["jobs"][people] == 3) & (a["active"][firms] == 1)
                         & (staff[firms] < d.firms["capacity"][firms])
                         & (d.households["territory"][d.people["household"][people]] == d.firms["territory"][firms]))
                a["jobs"][people[valid]], a["employer"][people[valid]] = 2, firms[valid]
            self.first_month = {"opening_jobs": before, "autonomous_continuity": int(((before == 3) & (a["jobs"] == 2)).sum()),
                                "after_plan": None, "after_payroll": None, "cash_capacity": 0, "filled": 0}
        return self.enter(state, journal) if "B" in self.factors else 0

    def enter(self, state, journal):
        a, d, p = state.accounts, state.demographics, self.params
        if (d.month + 1) % p["entry_months"]:
            return 0
        place = d.firms["territory"]
        workers = np.bincount(d.households["territory"][d.people["household"][a["jobs"] == 1]], minlength=3)
        pairs = []
        for area in range(3):
            sponsors = np.flatnonzero((place == area) & (a["active"] == 1) &
                                       (a["firm_deposit"] >= 3 * p["entry_deposit_cents"]) &
                                       (a["capital"] >= 2 * p["entry_capital_units"]))
            slots = np.flatnonzero((place == area) & (a["active"] == 0) & (a["firm_deposit"] == 0) &
                                    (a["firm_debt"] == 0) & (a["inventory"] == 0))
            pairs.extend(zip(sponsors[:workers[area]], slots[:workers[area]]))
        pairs = pairs[:p["max_entries_per_period"]]
        if not pairs:
            return 0
        sources, targets = np.asarray(pairs).T
        payments, receipts = np.zeros_like(a["firm_deposit"]), np.zeros_like(a["firm_deposit"])
        payments[sources], receipts[targets] = p["entry_deposit_cents"], p["entry_deposit_cents"]
        journal.transfer("enterprise-entry-deposit", a["firm_deposit"], a["firm_deposit"],
                         payments, receipts, "sponsors", "successor-enterprises")
        # An inactive slot's stranded old capital stays stranded. An entrant
        # takes only capital moved by the investor.
        stranding = int(a["capital"][targets].sum())
        moved = len(targets) * p["entry_capital_units"]
        journal.record("enterprise-entry-capital", [moved * state.price], [moved * state.price],
                       "successor/capital", "sponsor/capital")
        journal.record("enterprise-stranded-capital", [stranding * state.price], [stranding * state.price],
                       "stranded/real-loss", "old-enterprise/capital")
        a["capital"][sources] -= p["entry_capital_units"]
        a["capital"][targets] = p["entry_capital_units"]
        a["active"][targets] = 1
        a["arrears"][targets] = 0
        self.entries.extend({"month": d.month + 1, "enterprise_id": f"{slot}:{d.month + 1}", "sector": int(d.firms["sector"][slot])}
                            for slot in targets.tolist())
        return len(targets)

    def distribute(self, state, journal, interest):
        if "C" not in self.factors:
            return 0
        a, d = state.accounts, state.demographics
        budget = min(interest * self.params["interest_distribution_bp"] // 10000, max(0, int(a["bank_equity"][0])))
        ids = d.people["household"][d.people["status"] == 0]
        weights = np.bincount(ids, minlength=len(a["house_deposit"]))
        receipts = apportion(budget, weights)
        paid = int(receipts.sum())
        journal.record("bank-distribution-bank", [paid], [paid], "bank/equity", "bank/deposit-liability")
        journal.record("bank-distribution-house", receipts, receipts, "house/deposit", "house/property-income")
        a["house_deposit"] += receipts
        a["bank_equity"][0] -= paid
        return paid

    def provenance(self):
        return sha(canonical({"catalog": configuration(), "factors": self.factors, "parameters": self.params}))

    def observe(self, state, journal, stats, physical, entitlements, public_service_due, entries, distributed, budget):
        cash = {row["id"].split(":", 1)[1]: row["total_cents"] for row in journal.entries}
        sectors = ("house", "firm", "public")
        origins = {sector: cash[f"origination-{sector}-bank"] for sector in sectors}
        principal = {sector: cash[f"principal-{sector}-bank"] for sector in sectors}
        interest = {sector: cash[f"interest-{sector}-bank"] for sector in sectors}
        transfers_due = int(entitlements[1].sum())
        wages_due = int(entitlements[0].sum())
        # Rebuild expenditure from the separately recorded cash movements.
        spending = (cash["household-consumption"] + cash["sales-tax"] + cash["public-wages"] + cash["public-goods"]
                    + cash["private-investment"] + cash["public-investment"] + stats["stock_change"])
        require(spending == stats["gdp"], "Journal expenditure differs from production GDP")
        active_by_sector = [int(state.accounts["active"][state.demographics.firms["sector"] == i].sum()) for i in range(5)]
        if stats["month"] == 1:
            jobs = self.first_month.pop("opening_jobs")
            planned = self.first_month.pop("after_plan")
            paid = self.first_month.pop("after_payroll")
            end = state.accounts["jobs"][:len(jobs)]
            self.first_month.update(opening_unemployed=int((jobs == 1).sum()), opening_autonomous=int((jobs == 3).sum()),
                                    autonomous_to_unemployment=int(((jobs == 3) & (end == 1)).sum()),
                                    excess_private_before_payroll=int(((jobs == 2) & (planned != 2)).sum()),
                                    unaffordable_private=int(((planned == 2) & (paid != 2)).sum()),
                                    hires_from_search=int(((jobs == 1) & (paid == 2)).sum()),
                                    end_unemployed=stats["unemployed"])
        row = dict(stats, **physical, entries=entries, active_by_sector=active_by_sector, origination=origins, principal=principal,
                   interest=interest, bank_distribution=distributed, transfers_paid=cash["transfers"], transfers_due=transfers_due,
                   public_wages_paid=cash["public-wages"], public_wages_due=wages_due,
                   public_goods_paid=cash["public-goods"], public_investment_paid=cash["public-investment"],
                   income_tax=cash["income-tax"], sales_tax=cash["sales-tax"], public_service_due=public_service_due,
                   public_service_shortfall=public_service_due - interest["public"] - principal["public"],
                   public_credit_cap=self.params.get("treasury_credit_limit_cents", state.config["public_credit_limit"]),
                   intended_public_cash=budget, journal_expenditure=spending,
                   firms_at_credit_limit=int((state.accounts["firm_debt"] >= state.config["firm_credit_limit"]).sum()),
                   households_at_credit_limit=int((state.accounts["house_debt"] >= state.config["household_credit_limit"]).sum()),
                   nonbank_net_financial=stats["bank_deposits"] - stats["bank_loans"],
                   real_median_income=(round(stats["median_person_income"] * 100 / stats["cpi"])
                                       if stats["median_person_income"] is not None else None))
        require(row["bank_deposits"] - self.opening_deposits ==
                sum(origins.values()) - sum(principal.values()) - sum(interest.values()) + distributed,
                "Sector deposit flow mismatch")
        require(row["bank_equity"] - self.opening_equity ==
                sum(interest.values()) - row["bank_credit_losses"] - distributed, "Bank equity flow mismatch")
        self.rows.append(row)
