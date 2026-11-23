import fcntl
import os
from contextlib import contextmanager

from .contracts import canonical, digest, parse, require

GENESIS = "0" * 64


class Archive:
    def __init__(self, file):
        self.file = file
        self.events = []
        for raw in file:
            row = parse(raw)
            signature = row.pop("hash")
            require(row["seq"] == len(self.events) + 1 and row["previous"] == self.anchor and digest(row) == signature,
                    "archive_integrity")
            self.events.append(dict(row, hash=signature))

    @property
    def anchor(self):
        return self.events[-1]["hash"] if self.events else GENESIS

    def append(self, kind, **data):
        row = {"seq": len(self.events) + 1, "previous": self.anchor, "kind": kind, "data": data}
        row["hash"] = digest(row)
        self.file.write(canonical(row))
        self.file.flush()
        os.fsync(self.file.fileno())
        self.events.append(row)
        return row


@contextmanager
def locked(path, writable=True):
    mode = "a+b" if writable else "rb"
    with path.open(mode) as file:
        fcntl.flock(file, fcntl.LOCK_EX if writable else fcntl.LOCK_SH)
        file.seek(0)
        yield Archive(file)


def replay(archive, expected):
    from .contracts import inspect_decision, proposal
    require(archive.anchor == expected and archive.events[0]["kind"] == "manifest", "archive_anchor")
    prepared = {}
    reserved = {}
    completed = set()
    decisions = []
    initial = archive.events[0]["data"]
    for event in archive.events[1:]:
        row, kind = event["data"], event["kind"]
        key = row["key"]
        if kind == "reserved":
            obs = row["observation"]
            require(digest(obs) == row["observation_sha256"] and key not in reserved
                    and obs["universe"] == initial["universe"] and obs["mandate"] == initial["mandate"],
                    "invalid_reservation")
            reserved[key] = obs
        elif kind == "prepared":
            require(key in reserved and key not in prepared and key not in completed, "invalid_preparation")
            if row["choice"] is not None:
                obs = reserved[key]
                choice = inspect_decision(canonical(row["choice"]).decode(), obs)
                expected_proposal = proposal(choice, obs, key) if choice["outcome"] == "PROPOSE" else None
                require(row["payload"] == expected_proposal and row["outcome"] == choice["outcome"], "invalid_replay")
            else:
                require(row["outcome"] == "PROVIDER_FAILURE" and row["payload"] is None, "invalid_failure")
            prepared[key] = row
        elif kind == "decision":
            require(key in prepared and key not in completed, "invalid_decision_history")
            require(row["outcome"] == prepared[key]["outcome"], "invalid_outcome_history")
            completed.add(key)
            decisions.append(row)
        else:
            raise ValueError("invalid_event")
    return {"anchor": archive.anchor, "decisions": decisions, "incomplete": sorted(reserved.keys() - completed)}
