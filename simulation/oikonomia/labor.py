import numpy as np

from demos.randomness import uniform


def regroup(values, groups, size):
    result = np.zeros(size, dtype="<i8")
    np.add.at(result, groups, values)
    return result


def plan(state, recession):
    a, c, d = state.accounts, state.config, state.demographics
    p, jobs, employer = d.people, a["jobs"], a["employer"]
    wages = np.maximum(c["employee_wage_floor"], (p["income_work"].astype(np.int64) * 100 + 6) // 12)
    staff = np.bincount(employer[employer >= 0], minlength=len(a["active"]))
    capacity = d.firms["capacity"].astype(np.int64)
    cash_capacity = a["firm_deposit"] // max(1, c["employee_wage_floor"])
    if d.month:
        reference_stock = np.maximum(1, staff) * c["productivity"]
        target = staff + np.where(a["inventory"] > 2 * reference_stock, -1, 1)
        target = np.where(a["firm_deposit"] >= c["employee_wage_floor"] * 6, np.maximum(target, 1), target)
        target = np.minimum(capacity, np.minimum(np.maximum(target, 0), cash_capacity))
        if recession:
            target = target * 3 // 4
    else:
        target = np.minimum(staff, cash_capacity)
    target *= a["active"]
    a["staff_target"][:] = target
    private = np.flatnonzero(employer >= 0)
    ordered = private[np.argsort(employer[private], kind="stable")]
    group = employer[ordered]
    offset = np.repeat(np.cumsum(staff) - staff, staff)
    rejected = ordered[np.arange(len(ordered)) - offset >= target[group]]
    jobs[rejected], employer[rejected] = 1, -1
    staff = np.bincount(employer[employer >= 0], minlength=len(target))
    # Self-employed Demos endowments enter the regular search pool at opening.
    jobs[jobs == 3] = 1
    search = np.flatnonzero(jobs == 1)
    if d.month == 0:
        search = search[:0]
    location = d.households["territory"][p["household"]]
    for place in range(3):
        bidders = search[location[search] == place]
        priority = uniform(d.seed, "oikonomia/labor", d.month + 1, bidders) + p["skills"][bidders] / 100
        candidates = bidders[np.argsort(-priority, kind="stable")]
        firms = np.flatnonzero(d.firms["territory"] == place)
        slots = np.repeat(firms, np.maximum(0, target[firms] - staff[firms]))
        matched = min(len(candidates), len(slots))
        jobs[candidates[:matched]], employer[candidates[:matched]] = 2, slots[:matched]
    return wages


def pay_private(state, journal, wages):
    a, d = state.accounts, state.demographics
    workers = np.flatnonzero(a["jobs"] == 2)
    firm = a["employer"][workers]
    ordered = workers[np.argsort(firm, kind="stable")]
    linked = a["employer"][ordered]
    if len(ordered):
        cumulative = wages[ordered].cumsum()
        first = np.r_[True, linked[1:] != linked[:-1]]
        offsets = np.maximum.accumulate(np.where(first, cumulative - wages[ordered], 0))
        denied = ordered[cumulative - offsets > a["firm_deposit"][linked]]
        a["jobs"][denied], a["employer"][denied] = 1, -1
    workers = np.flatnonzero(a["jobs"] == 2)
    firm = a["employer"][workers]
    pay = wages[workers]
    payments = regroup(pay, firm, len(a["active"]))
    households = regroup(pay, d.people["household"][workers], len(a["house_deposit"]))
    journal.transfer("private-wages", a["firm_deposit"], a["house_deposit"], payments, households, "firms", "households")
    return households, int(pay.sum())


def advance_demographics(state, event):
    a, d = state.accounts, state.demographics
    extra = len(d.people) - len(a["jobs"])
    a["jobs"] = np.pad(a["jobs"], (0, extra))
    a["employer"] = np.pad(a["employer"], (0, extra), constant_values=-1)
    stop = (d.people["status"] != 0) | (d.ages >= 780)
    a["jobs"][stop], a["employer"][stop] = 0, -1
    birthday = np.flatnonzero((d.ages == 216) & ~stop)
    entering = np.r_[birthday, event["immigrants"]].astype(int)
    choice = uniform(d.seed, "oikonomia/work-entry", d.month, entering) < .7
    a["jobs"][entering[choice]] = 1
    n = len(d.households) - len(a["house_deposit"])
    for name in ("house_deposit", "house_debt", "income_history"):
        a[name] = np.pad(a[name], (0, n))
