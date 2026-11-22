"""Columnar individual, household, firm and territory schemas."""
from dataclasses import dataclass

import numpy as np

PREFERENCES = ("risk", "saving", "cooperation", "environment", "services", "taxation", "liberty", "trust", "participation")
PEOPLE = np.dtype([
    ("id", "<i8"), ("born", "<i4"), ("sex", "u1"), ("status", "u1"), ("immigrant", "?"),
    ("household", "<i8"), ("parent", "<i8"), ("partner", "<i8"),
    ("education", "u1"), ("skills", "u1"), ("job", "u1"), ("firm", "<i4"),
    ("occupation", "u1"), ("income_work", "<i4"), ("income_other", "<i4"), ("savings", "<i4"),
    ("assets", "<i4"), ("debt", "<i4"), ("health", "u1"), ("limitations", "?"), ("care", "?"), ("autonomy", "u1"),
    *((field, "u1") for field in PREFERENCES),
])
HOUSEHOLDS = np.dtype([("id", "<i8"), ("territory", "u1"), ("tenure", "u1")])
FIRMS = np.dtype([("id", "<i4"), ("territory", "u1"), ("sector", "u1"), ("size", "u1"),
                  ("active", "?"), ("owner", "<i8"), ("capacity", "<i4")])
TERRITORY = np.dtype([("id", "u1"), ("dwelling_capacity", "<i4")])
# status: 0 resident, 1 deceased, 2 emigrated; job: 0 outside LF, 1 unemployed, 2 private,
# 3 self employed, 4 public. ID/link -1 means absent. Ages derive from month minus born.


@dataclass
class State:
    config: dict
    seed: int
    people: np.ndarray
    households: np.ndarray
    firms: np.ndarray
    territories: np.ndarray
    month: int = 0
    replica: str = "baseline"

    def clone(self, replica):
        import copy
        return State(copy.deepcopy(self.config), self.seed, self.people.copy(), self.households.copy(),
                     self.firms.copy(), self.territories.copy(), self.month, replica)

    @property
    def ages(self):
        return self.month - self.people["born"]
