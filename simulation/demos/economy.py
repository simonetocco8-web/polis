import numpy as np

from .randomness import choose, uniform
from .state import FIRMS

CAPACITY = (9, 49, 249, 499)
CLASSES = ("Micro", "Piccole", "Medie", "Grandi")


def initial_firms(state):
    ids = np.arange(state.config["firms"])
    firms = np.zeros(len(ids), dtype=FIRMS)
    firms["id"] = ids
    firms["active"] = True
    firms["owner"] = -1
    firms["territory"] = choose(state.config["territory_weights"], uniform(state.seed, "firm-territory", 0, ids))
    firms["sector"] = choose(state.config["sector_weights"], uniform(state.seed, "firm-sector", 0, ids))
    firms["size"] = choose(state.config["firm_class_weights"], uniform(state.seed, "firm-size", 0, ids))
    firms["capacity"] = np.asarray(CAPACITY)[firms["size"]]
    return firms


def assign_work(state):
    people, firms, ages = state.people, state.firms, state.ages
    ids = np.flatnonzero((ages >= 216) & (ages < 65 * 12))
    likelihood = .79 - .10 * people["limitations"][ids] + .035 * (people["education"][ids].astype(int) - 1)
    labor = ids[uniform(state.seed, "workforce", 0, ids) < likelihood]
    labor = labor[np.argsort(uniform(state.seed, "employment", 0, labor), kind="stable")]
    unemployed = round(len(labor) * state.config["macro_targets"]["unemployment_percent"] / 100)
    people["job"][labor[:unemployed]] = 1
    workers = labor[unemployed:]
    mix = uniform(state.seed, "job-kind", 0, workers)
    people["job"][workers] = np.where(mix < .14, 4, np.where(mix < .24, 3, 2))
    private = workers[people["job"][workers] == 2]
    self_employed = workers[people["job"][workers] == 3]
    for location in range(3):
        local = np.flatnonzero(firms["territory"] == location)
        local_workers = private[state.households["territory"][people["household"][private]] == location]
        # Round-robin per company with class-specific capacity limits.
        slots = np.nonzero(np.arange(max(CAPACITY))[:, None] < firms["capacity"][local])[1]
        used = min(len(slots), len(local_workers))
        people["firm"][local_workers[:used]] = local[slots[:used]]
        people["job"][local_workers[used:]] = 3
        owners = self_employed[state.households["territory"][people["household"][self_employed]] == location]
        owner_count = min(len(local), len(owners))
        firms["owner"][local[:owner_count]] = owners[:owner_count]
        people["firm"][owners[:owner_count]] = local[:owner_count]
    earners = np.flatnonzero(people["job"] >= 2)
    people["occupation"][earners] = 1 + people["education"][earners]
    people["income_work"][earners] = 10500 + people["education"][earners].astype(int) * 6500 + (
        8500 * uniform(state.seed, "wages", 0, earners)).astype(int)
    adults = np.flatnonzero(ages >= 216)
    people["income_other"][adults] = np.where(ages[adults] >= 780, 14000, 0)
    people["savings"][adults] = (people["income_work"][adults] * uniform(state.seed, "savings", 0, adults) * .8).astype(int)
    people["assets"][adults] = people["savings"][adults] * 2
    people["debt"][adults] = (people["assets"][adults] * .25).astype(int)


def leave_work(state, indices):
    for field in ("job", "occupation", "income_work"):
        state.people[field][indices] = 0
    state.people["firm"][indices] = -1
    state.firms["owner"][np.isin(state.firms["owner"], indices)] = -1
