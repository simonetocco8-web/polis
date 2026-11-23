from archon.contracts import digest, require
from demos.config import load_config
from demos.engine import generate
from oikonomia.engine import step
from oikonomia.snapshot import digest as state_digest, restore, save
from oikonomia.state import attach
from stabilitas.policy import Policy

from .protocol import INDICATORS, REGIMES, VERSION, readiness, sources, transition, validate
from .statistics import describe

GENESIS = "0" * 64


def shock_window(seed, horizon):
    # This domain has no dependency on engine RNG state or policy calls.
    stream = digest(["experimentum-production-window-v1", seed, horizon])
    start = 2 + int(stream[:16], 16) % (horizon - 1)
    return {"kind": "production-shock", "start": start, "end": start, "commitment": stream}


def execute(opening, shock, months):
    state = opening.clone(opening.demographics.replica)
    state.variant = shock["kind"]
    state.config.update(shock_start_month=shock["start"], shock_end_month=shock["end"])
    previous, series = GENESIS, []
    policy = Policy("R")
    for month in range(1, months + 1):
        result, details = step(state, policy=policy)
        require(result["month"] == month, "Periodo economico incoerente")
        row = {"month": month, **{key: result[key] for key in INDICATORS}, "ledger_sha256": details["journal"],
               "previous": previous}
        previous = digest(row)
        series.append(dict(row, hash=previous))
    return series, state_digest(state)


def run(protocol, directory):
    validate(protocol)
    directory.mkdir(mode=0o700)
    replicas = []
    for i, seed in enumerate(protocol["replicas"], 1):
        replica = {"id": f"replica-{i}", "status": "INVALIDATED", "error": None, "series": [],
                   "checkpoint_sha256": None, "replay_checkpoint_sha256": None, "final_sha256": None,
                   "replay_final_sha256": None, "anchor": None, "replay_anchor": None,
                   "shock": shock_window(seed, protocol["months"])}
        try:
            original = attach(generate(load_config("smoke", "eu27"), seed, f"pilot-{i}"))
            checkpoint = directory / f"replica-{i}"
            meta = save(original, checkpoint)
            opening = restore(checkpoint)
            replica["checkpoint_sha256"] = meta["snapshot_sha256"]
            replica["replay_checkpoint_sha256"] = state_digest(opening)
            require(replica["checkpoint_sha256"] == replica["replay_checkpoint_sha256"], "checkpoint-mismatch")
            replica["series"], replica["final_sha256"] = execute(original, replica["shock"], protocol["months"])
            replica["anchor"] = replica["series"][-1]["hash"]
            replay, replica["replay_final_sha256"] = execute(opening, replica["shock"], protocol["months"])
            replica["replay_anchor"] = replay[-1]["hash"]
            require(replay == replica["series"] and replica["final_sha256"] == replica["replay_final_sha256"], "replay-mismatch")
            replica["status"] = "REPRODUCED"
        except (KeyError, ValueError, OSError, ArithmeticError, RuntimeError) as error:
            replica["error"] = ("replay-mismatch" if str(error) == "replay-mismatch" else
                                "missing-aggregate" if isinstance(error, KeyError) else "engine-error")
        replicas.append(replica)
    history = ["NOT_READY"]
    for state in ("PREREGISTERED", "TECHNICAL_VALIDATION", "COMPLETED",
                  "REPRODUCED" if all(x["status"] == "REPRODUCED" for x in replicas) else "INVALIDATED"):
        history.append(transition(history[-1], state))
    return {"version": VERSION, "mode": "offline-technical", "protocol": protocol, "protocol_sha256": digest(protocol),
            "sources": sources(), "state": history[-1], "state_history": history, "readiness": readiness(list(REGIMES)),
            "regimes": REGIMES, "indicators": INDICATORS, "replicas": replicas, "exclusions": [],
            "aggregates": describe(replicas, protocol["months"]), "calibration": "hypothesized", "api_calls": 0}
