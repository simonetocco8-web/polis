import numpy as np

from .randomness import choose, uniform
from .state import HOUSEHOLDS, TERRITORY


def new_households(state, indices, territory=None):
    first = len(state.households)
    ids = np.arange(first, first + len(indices), dtype=np.int64)
    records = np.zeros(len(ids), dtype=HOUSEHOLDS)
    records["id"] = ids
    records["territory"] = territory if territory is not None else choose(
        state.config["territory_weights"], uniform(state.seed, "household-territory", 0, ids))
    records["tenure"] = (uniform(state.seed, "tenure", 0, ids) > .55)
    state.households = np.concatenate((state.households, records))
    state.people["household"][indices] = ids


def settle(state):
    people, ages = state.people, state.ages
    adults = np.flatnonzero(ages >= 216)
    adults = adults[np.argsort(ages[adults] + uniform(state.seed, "household-match", 0, adults) * 84, kind="stable")]
    sizes = np.asarray(state.config["family_adult_slots"])[choose(
        state.config["family_weights"], uniform(state.seed, "household-size", 0, adults))]
    starts = np.r_[0, np.cumsum(sizes)]
    starts = starts[starts < len(adults)]
    heads = adults[starts]
    new_households(state, heads)
    for index, (start, stop) in enumerate(zip(starts, np.r_[starts[1:], len(adults)])):
        members = adults[start:stop]
        people["household"][members] = index
        if len(members) >= 2:
            a, b = members[:2]
            people["partner"][[a, b]] = [b, a]
    # Move some older unpaired adults in with a younger adult household. These
    # are co-residence links; adult kinship is recorded only if explicitly modeled.
    elders = heads[(ages[heads] >= 65 * 12) & (people["partner"][heads] < 0)]
    younger = heads[(ages[heads] >= 26 * 12) & (ages[heads] < 53 * 12)]
    if younger.size:
        movers = elders[uniform(state.seed, "multi-generation", 0, elders) < .35]
        people["household"][movers] = people["household"][younger[np.arange(len(movers)) % len(younger)]]
    minors = np.flatnonzero(ages < 216)
    for year in range(18):
        children = minors[(ages[minors] // 12) == year]
        eligible = heads[(ages[heads] >= (year + 19) * 12) & (ages[heads] < 61 * 12)]
        if not len(eligible):
            new_households(state, children)
            continue
        picks = eligible[(uniform(state.seed, "guardian", 0, children) * len(eligible)).astype(int)]
        people["parent"][children] = picks
        people["household"][children] = people["household"][picks]
    ids = np.arange(3)
    state.territories = np.zeros(3, dtype=TERRITORY)
    state.territories["id"] = ids
    population = np.bincount(state.households["territory"][people["household"]], minlength=3)
    state.territories["dwelling_capacity"] = np.ceil(population * state.config["dwelling_capacity_per_initial_resident"])


def form_partnerships(state):
    people, ages, month = state.people, state.ages, state.month
    residents = people["status"] == 0
    membership = np.bincount(people["household"][residents], minlength=len(state.households))
    eligible = np.flatnonzero(residents & (people["partner"] < 0) & (ages >= 216) &
                              (membership[people["household"]] == 1))
    probability = -np.expm1(np.log1p(-state.config["annual_partner_probability"]) / 12)
    selected = eligible[uniform(state.seed, "partnership", month, eligible) < probability]
    selected = selected[np.argsort(ages[selected], kind="stable")]
    a, b = selected[:len(selected) // 2 * 2].reshape(-1, 2).T
    valid = (ages[b] - ages[a] <= 180) & (people["parent"][a] != b) & (people["parent"][b] != a)
    a, b = a[valid], b[valid]
    people["partner"][a], people["partner"][b] = b, a
    people["household"][b] = people["household"][a]
    return np.stack((a, b), axis=1).tolist()
