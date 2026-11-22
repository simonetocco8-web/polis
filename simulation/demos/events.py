"""Hash chained monthly event logs and technical replay."""
import json

from .config import canonical, sha
from .engine import step
from .snapshot import digest
from .validation import require, validate


def run(state, months, path):
    require(0 <= months <= state.config["months"] - state.month, "Invalid run length")
    anchor = digest(state)
    with path.open("x", encoding="utf-8") as output:
        output.write(canonical({"start": anchor, "months": months}).decode())
        for _ in range(months):
            event = step(state)
            validate(state)
            linked = {"previous": anchor, "event": event}
            anchor = sha(canonical(linked))
            output.write(canonical(dict(linked, hash=anchor)).decode())
        output.write(canonical({"final": digest(state), "last": anchor}).decode())


def replay(state, path):
    with path.open(encoding="utf-8") as log:
        start = json.loads(next(log))
        anchor = digest(state)
        require(start["start"] == anchor, "Replay starting snapshot mismatch")
        require(type(start["months"]) is int and 0 <= start["months"] <= state.config["months"] - state.month,
                "Invalid event horizon")
        for _ in range(start["months"]):
            record = json.loads(next(log))
            event = step(state)
            validate(state)
            linked = {"previous": anchor, "event": event}
            anchor = sha(canonical(linked))
            require(record == dict(linked, hash=anchor), f"Replay mismatch at month {state.month}")
        require(json.loads(next(log)) == {"final": digest(state), "last": anchor}, "Replay final checksum mismatch")
        require(not log.read(), "Unexpected trailing events")
