import copy
import json

from demos.config import canonical, sha

from .institutions import Institutions
from .registry import VERSION, provenance, require

GENESIS = "0" * 64


def strict_json(raw):
    def object_pairs(pairs):
        data = dict(pairs)
        require(len(data) == len(pairs), "Chiavi JSON duplicate")
        return data

    def reject_constant(value):
        raise ValueError("Valore JSON non finito")

    return json.loads(raw, object_pairs_hook=object_pairs, parse_constant=reject_constant)


class Journal:
    def __init__(self, universe, regime):
        self.state = Institutions(universe, regime)
        self.events = []
        self._record("operator", "init", {"sources": provenance()}, {"state": "initialized"})

    @property
    def anchor(self):
        return self.events[-1]["hash"] if self.events else GENESIS

    def _record(self, role, operation, data, result):
        row = {"id": f"nomos-{len(self.events) + 1:06}", "version": VERSION, "universe": self.state.universe,
               "regime": self.state.regime, "day": self.state.day.isoformat(), "period": self.state.period,
               "role": role, "operation": operation, "data": data, "result": result, "previous": self.anchor}
        row["hash"] = sha(canonical(row))
        self.events.append(row)
        return copy.deepcopy(result)

    def apply(self, role, operation, data):
        data = copy.deepcopy(data)
        # Read operations leave history unchanged.
        if operation in ("observe", "docket", "casefile", "integrity"):
            return self.state.dispatch(role, operation, data)
        # Work on a copy so an invalid command cannot leave partial changes.
        state = copy.deepcopy(self.state)
        try:
            result = state.dispatch(role, operation, data)
        except (TypeError, KeyError):
            raise ValueError("Argomenti o riferimenti non validi") from None
        canonical({"data": data, "result": result})
        self.state = state
        return self._record(role, operation, data, result)

    def government_view(self):
        return {"universe": self.state.universe, "period": self.state.period,
                "last_economy": {key: self.state.effects[-1][key] for key in ("period", "public_revenue", "public_spending")}
                if self.state.effects else None,
                "continuity": self.state.governor is None}

    @classmethod
    def replay(cls, events, expected=None):
        require(bool(events), "Registro privo di origine")
        first = events[0]
        journal = cls(first["universe"], first["regime"])
        require(canonical(journal.events[0]) == canonical(first), "Origine del registro non verificata")
        for row in events[1:]:
            journal.apply(row["role"], row["operation"], row["data"])
            require(canonical(journal.events[-1]) == canonical(row), "Catena o replay non verificati")
        require(expected is None or journal.anchor == expected, "Testa del registro inattesa")
        return journal
