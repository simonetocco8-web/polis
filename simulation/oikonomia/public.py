import numpy as np

from .labor import regroup
from .ledger import apportion


def obligations(state):
    a, c, d = state.accounts, state.config, state.demographics
    jobs = a["jobs"]
    resident = d.people["status"] == 0
    pensioners = resident & (d.ages >= 780)
    wages = regroup((jobs == 4) * c["public_wage"], d.people["household"], len(a["house_deposit"]))
    transfers = regroup(pensioners * c["pension"] + (jobs == 1) * c["unemployment_benefit"],
                        d.people["household"], len(a["house_deposit"]))
    return wages, transfers


def pay(state, journal):
    a = state.accounts
    wages, transfers = obligations(state)
    result = []
    for name, payable in (("public-wages", wages), ("transfers", transfers)):
        paid = apportion(min(int(a["government"][0]), int(payable.sum())), payable)
        journal.transfer(name, a["government"], a["house_deposit"], np.array([paid.sum()]), paid, "treasury", "households")
        result.append(paid)
    return result


def tax(state, journal, wages):
    a = state.accounts
    levy = wages * state.config["income_tax_bp"] // 10000
    journal.transfer("income-tax", a["house_deposit"], a["government"], levy, np.array([levy.sum()]), "households", "treasury")
    return levy
