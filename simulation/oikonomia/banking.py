import numpy as np

from demos.validation import require


def lend(state, journal, sector, request, ceiling, halted=False):
    a = state.accounts
    debt = a[f"{sector}_debt"]
    deposits = a["government" if sector == "public" else f"{sector}_deposit"]
    amount = np.minimum(np.maximum(request, 0), np.maximum(ceiling - debt, 0))
    if halted or a["bank_equity"][0] <= 0:
        amount[:] = 0
    total = int(amount.sum())
    journal.record(f"origination-{sector}-bank", [total], [total], "bank/loans", "bank/deposit-liability")
    journal.record(f"origination-{sector}-debtor", amount, amount, sector + "/deposit", sector + "/debt")
    deposits += amount
    debt += amount
    a["bank_loans"][0] += total


def service(state, journal, sector):
    a, c = state.accounts, state.config
    debt = a[f"{sector}_debt"]
    deposits = a["government" if sector == "public" else f"{sector}_deposit"]
    interest_due = debt * c["loan_rate_monthly_bp"] // 10000
    interest = np.minimum(interest_due, deposits)
    received = np.array([interest.sum()], dtype="<i8")
    # Bank receipt is a cancellation of deposit liability and an increase in equity.
    journal.record(f"interest-{sector}-debtor", interest, interest, sector + "/interest-expense", sector + "/deposit")
    journal.record(f"interest-{sector}-bank", received, received, "bank/deposit-liability", "bank/interest-income")
    deposits -= interest
    a["bank_equity"] += received
    due = (debt + c["loan_term_months"] - 1) // c["loan_term_months"]
    paid = np.minimum(due, deposits)
    principal = int(paid.sum())
    journal.record(f"principal-{sector}-bank", [principal], [principal], "bank/deposit-liability", "bank/loans")
    journal.record(f"principal-{sector}-debtor", paid, paid, sector + "/debt", sector + "/deposit")
    deposits -= paid
    debt -= paid
    a["bank_loans"][0] -= principal
    return int(interest.sum()), (interest < interest_due) | (paid < due)


def write_off(state, journal, failed):
    a = state.accounts
    losses = np.where(failed, a["firm_debt"], 0)
    total = int(losses.sum())
    journal.record("writeoff-bank", [total], [total], "bank/equity", "bank/loans")
    journal.record("writeoff-firm", losses, losses, "firm/debt", "firm/extraordinary-gain")
    a["firm_debt"] -= losses
    a["bank_loans"][0] -= total
    a["bank_equity"][0] -= total
    require(a["bank_loans"][0] >= 0, "Bank loans below zero")
    return total
