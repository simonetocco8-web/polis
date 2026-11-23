"""Single-bank settlement, integer cents and hash-linked posting batches."""
import hashlib

import numpy as np

from demos.config import canonical, sha
from demos.validation import require

LIMIT = 10**14


def apportion(total, weights):
    """Integer proportional rationing, with exact additive reconciliation."""
    weights = np.asarray(weights, dtype=np.int64)
    size = int(weights.sum())
    require(0 <= total <= LIMIT and size >= 0 and np.all(weights >= 0), "Invalid allocation")
    if total == 0 or size == 0:
        return np.zeros_like(weights)
    cumulative = weights.cumsum()
    if total * size >= 2**62:
        allocated = np.fromiter((int(x) * total // size for x in cumulative), dtype=np.int64, count=len(weights))
    else:
        allocated = cumulative * total // size
    return np.diff(allocated, prepend=0)


class Journal:
    def __init__(self, month, anchor, detail=None):
        self.month, self.anchor, self.detail = month, anchor, detail
        self.entries = []
        self.codes = set()

    def record(self, label, debit, credit, debit_accounts="", credit_accounts=""):
        require(label not in self.codes, f"Duplicate posting: {label}")
        debit = np.ascontiguousarray(debit, dtype="<i8")
        credit = np.ascontiguousarray(credit, dtype="<i8")
        def bounded_total(legs):
            require(np.all((legs >= 0) & (legs <= LIMIT)), "Invalid posting amount")
            if len(legs) * int(legs.max(initial=0)) > np.iinfo(np.int64).max:
                total = sum(map(int, legs))
            else:
                total = int(legs.sum())
            require(total <= LIMIT, "Posting limit exceeded")
            return total

        total = bounded_total(debit)
        require(total == bounded_total(credit), "Unbalanced or invalid posting")
        key = f"{self.month}:{label}"
        posting = {"id": key, "total_cents": total, "previous": self.anchor,
                   "debit_accounts": debit_accounts, "credit_accounts": credit_accounts,
                   "debit_sha256": hashlib.sha256(debit.tobytes()).hexdigest(),
                   "credit_sha256": hashlib.sha256(credit.tobytes()).hexdigest()}
        anchor = sha(canonical(posting))
        if self.detail is not None:
            self.detail.write(canonical(dict(posting, hash=anchor, debit=debit.tolist(), credit=credit.tolist())))
        self.anchor = anchor
        self.entries.append(dict(posting, hash=anchor))
        self.codes.add(label)

    def transfer(self, label, source, target, paid, received, source_account, target_account):
        require(source.shape == paid.shape and target.shape == received.shape and np.all(paid <= source),
                f"Insufficient funds: {label}")
        require(np.all(target <= LIMIT - received), "Deposit limit exceeded")
        self.record(label, received, paid, target_account + "/deposit", source_account + "/deposit")
        source -= paid
        target += received
