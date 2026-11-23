import numpy as np

from .labor import regroup


def demand(state, disposable, recession):
    a, c, d = state.accounts, state.config, state.demographics
    live = d.people[d.people["status"] == 0]
    group = live["household"]
    size = np.bincount(group, minlength=len(a["house_deposit"]))
    propensity = regroup(live["saving"].astype(int), group, len(size)) // np.maximum(size, 1)
    bp = np.clip(c["consumption_bp"] + (50 - propensity) * 18, 4000, 9000)
    if recession:
        bp = bp * 3 // 4
    essentials = size * c["essential_units_per_resident"]
    desired = (disposable * bp // 10000 + a["house_deposit"] // 70) // state.price
    return np.where(size > 0, np.maximum(essentials, desired), 0), essentials, size
