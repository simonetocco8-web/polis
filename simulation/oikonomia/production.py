import numpy as np

from .labor import regroup
from .markets import clear


def produce(state, journal, shock, diagnostics=None):
    a, c, d = state.accounts, state.config, state.demographics
    workers = np.flatnonzero(a["jobs"] == 2)
    linked = a["employer"][workers]
    skills = regroup(65 + d.people["skills"][workers].astype(int), linked, len(a["active"]))
    sector = np.array([105, 90, 85, 115, 100])[d.firms["sector"]]
    skill_capacity = skills * c["productivity"] * sector // 10000
    capital_capacity = a["capital"] // 2
    planned = np.minimum(skill_capacity, capital_capacity)
    if shock:
        planned //= 2
    planned *= a["active"]
    # At most one intermediate good for ten units produced, with strict
    # resource rationing. Opening stocks are the only intermediate supply.
    used, _, _, intermediate = clear(journal, "intermediate", a["inventory"], (planned + 9) // 10,
                                    a["firm_deposit"], a["firm_deposit"], state.price, "firms")
    output = np.minimum(planned, used * 10)
    a["inventory"] += output
    journal.record("material-use", used * state.price, used * state.price, "firm/intermediate-expense", "firm/inventory")
    journal.record("produced-inventory", output * state.price, output * state.price, "firm/inventory", "firm/output")
    if diagnostics is not None:
        diagnostics.update(
            planned_units=int(planned.sum()), requested_intermediates=int(((planned + 9) // 10).sum()),
            used_intermediates=intermediate, labor_capacity_units=int((skill_capacity * a["active"]).sum()),
            capital_capacity_units=int((capital_capacity * a["active"]).sum()),
            sector_output=[int(output[d.firms["sector"] == index].sum()) for index in range(5)],
        )
    return output, intermediate
