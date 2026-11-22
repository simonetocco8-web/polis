import numpy as np

from .economy import CAPACITY
from .state import FIRMS, HOUSEHOLDS, PEOPLE, PREFERENCES, TERRITORY


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(state):
    p, h, f, t, ages = state.people, state.households, state.firms, state.territories, state.ages
    for values, schema in ((p, PEOPLE), (h, HOUSEHOLDS), (f, FIRMS), (t, TERRITORY)):
        require(values.dtype == schema and values.ndim == 1, "Invalid state schema")
        require(np.array_equal(values["id"], np.arange(len(values))), "Invalid IDs")
    require(0 <= state.month <= state.config["months"], "Invalid period")
    require(len(f) == state.config["firms"] and len(t) == 3, "Invalid firm/territory count")
    if state.month == 0:
        require(len(p) == state.config["population"] and np.all(p["status"] == 0), "Invalid initial population")
    require(np.all(ages >= 0) and np.all(p["sex"] < 2) and np.all(p["status"] <= 2), "Invalid demographic values")
    require(np.all((p["household"] >= 0) & (p["household"] < len(h))), "Invalid household link")
    require(np.all(h["territory"] < len(t)) and np.all(f["territory"] < len(t)), "Invalid territory link")
    require(np.all(t["dwelling_capacity"] >= 0), "Invalid dwelling capacity")
    for field, size in (("parent", len(p)), ("partner", len(p)), ("firm", len(f))):
        require(np.all((p[field] >= -1) & (p[field] < size)), f"Invalid {field} link")
    children = np.flatnonzero(p["parent"] >= 0)
    require(np.all(p["born"][children] - p["born"][p["parent"][children]] >= 216), "Invalid genealogy")
    married = np.flatnonzero(p["partner"] >= 0)
    partners = p["partner"][married]
    require(np.all(partners != married) and np.array_equal(p["partner"][partners], married)
            and np.array_equal(p["household"][partners], p["household"][married])
            and np.all(ages[married] >= 216) and np.all(p["status"][married] == 0), "Invalid partnership")
    working = p["job"] > 0
    require(np.all(p["job"] <= 4) and np.all((ages[working] >= 216) & (ages[working] < 780))
            and np.all(p["status"][working] == 0), "Invalid labor force")
    private = p["job"] == 2
    require(np.all(p["firm"][private] >= 0) and np.all(np.isin(p["job"][p["firm"] >= 0], [2, 3])), "Invalid job link")
    require(np.all((f["owner"] >= -1) & (f["owner"] < len(p))) and np.all(f["size"] < len(CAPACITY)), "Invalid firm data")
    owned = f[f["owner"] >= 0]
    require(np.all(p["job"][owned["owner"]] == 3) and np.array_equal(p["firm"][owned["owner"]], owned["id"]), "Invalid ownership")
    headcount = np.bincount(p["firm"][p["firm"] >= 0], minlength=len(f))
    require(np.all(headcount <= f["capacity"] + (f["owner"] >= 0)), "Firm capacity exceeded")
    require(all(np.all(p[field] <= 100) for field in (*PREFERENCES, "skills", "autonomy")), "Invalid bounded trait")
