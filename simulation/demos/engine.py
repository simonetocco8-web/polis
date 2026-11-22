import numpy as np

from .economy import assign_work, initial_firms, leave_work
from .households import form_partnerships, new_households, settle
from .people import citizens, initial_people, update_health
from .randomness import uniform
from .state import FIRMS, HOUSEHOLDS, TERRITORY, State
from .validation import require, validate


def generate(config, seed, replica="baseline"):
    state = State(config, seed, initial_people(config, seed), np.zeros(0, dtype=HOUSEHOLDS),
                  np.zeros(0, dtype=FIRMS), np.zeros(0, dtype=TERRITORY), replica=replica)
    settle(state)
    state.firms = initial_firms(state)
    assign_work(state)
    validate(state)
    return state


def monthly_probability(annual):
    return 1 - np.power(1 - annual, 1 / 12)


def step(state):
    require(state.month < state.config["months"], "End of configured horizon")
    state.month += 1
    people, ages, month = state.people, state.ages, state.month
    resident = people["status"] == 0
    initial = int(resident.sum())
    ids = np.flatnonzero(resident)
    age = np.minimum(ages[ids] // 12, 94)
    empirical = state.config.get("empirical")
    if empirical:
        annual = np.asarray(empirical["annual_mortality"])[people["sex"][ids], age]
    else:
        annual = np.minimum(.7, .0002 + .00001 * np.exp(age / 8.2))
    dead = ids[uniform(state.seed, "mortality", month, ids) < monthly_probability(annual)]
    people["status"][dead] = 1
    candidates = np.flatnonzero((people["status"] == 0) & (ages >= 216))
    emigrants = candidates[uniform(state.seed, "emigration", month, candidates) <
                           monthly_probability(state.config["annual_emigration_probability"])]
    people["status"][emigrants] = 2
    departed = np.r_[dead, emigrants]
    partners = people["partner"][departed]
    people["partner"][partners[partners >= 0]] = -1
    people["partner"][departed] = -1
    retirees = np.flatnonzero((ages >= 780) & (people["job"] > 0))
    leave_work(state, np.r_[departed, retirees])
    residents = np.flatnonzero(people["status"] == 0)
    affected = people[residents].copy()
    update_health(affected, state.seed, month)
    people[residents] = affected
    parents = np.flatnonzero((people["status"] == 0) & (people["sex"] == 0) & (ages >= 216) & (ages < 45 * 12))
    parents = parents[uniform(state.seed, "birth", month, parents) <
                      monthly_probability(state.config["annual_birth_probability"])]
    expected = initial * state.config["annual_immigration_rate"] / 12
    count = int(expected) + int(uniform(state.seed, "immigration-volume", month, [0])[0] < expected % 1)
    start = len(people)
    baby_ids = np.arange(start, start + len(parents))
    migrant_ids = np.arange(start + len(parents), start + len(parents) + count)
    incoming = np.r_[baby_ids, migrant_ids]
    migrant_ages = 216 + (uniform(state.seed, "migrant-age", month, migrant_ids) * (47 * 12)).astype(int)
    new = citizens(incoming, month - np.r_[np.zeros(len(baby_ids), dtype=int), migrant_ages],
                   uniform(state.seed, "new-sex", month, incoming) > .5, state.seed, month)
    new["parent"][:len(parents)] = parents
    new["household"][:len(parents)] = people["household"][parents]
    new["immigrant"][len(parents):] = True
    state.people = np.concatenate((people, new))
    new_households(state, migrant_ids)
    partnerships = form_partnerships(state)
    final = int((state.people["status"] == 0).sum())
    require(final == initial + len(baby_ids) - len(dead) + count - len(emigrants), "Population identity mismatch")
    return {"month": month, "initial": initial, "final": final, "births": baby_ids.tolist(),
            "parents": parents.tolist(), "deaths": dead.tolist(), "immigrants": migrant_ids.tolist(),
            "emigrants": emigrants.tolist(), "partnerships": partnerships}
