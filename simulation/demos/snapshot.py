import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from . import VERSION
from .config import canonical, sha
from .state import State
from .validation import require, validate

TABLES = ("people", "households", "firms", "territories")


def header(state):
    return {"schema": "demos-state-1", "generator": VERSION, "config": state.config,
            "seed": state.seed, "month": state.month}


def digest(state):
    result = hashlib.sha256(canonical(header(state)))
    for name in TABLES:
        table = getattr(state, name)
        result.update(canonical([name, table.dtype.descr, len(table)]))
        result.update(memoryview(table).cast("B"))
    return result.hexdigest()


def save(state, directory: Path):
    validate(state)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = dict(header(state), replica=state.replica, snapshot_sha256=digest(state),
                    config_sha256=sha(canonical(state.config)), generated_at=datetime.now(timezone.utc).isoformat(),
                    numpy=np.__version__, python=platform.python_version())
    np.savez_compressed(directory / "snapshot.npz", **{name: getattr(state, name) for name in TABLES})
    (directory / "manifest.json").write_bytes(canonical(manifest))
    return manifest


def restore(directory: Path):
    manifest = json.loads((directory / "manifest.json").read_bytes())
    require(manifest["schema"] == "demos-state-1" and manifest["generator"] == VERSION, "Unsupported checkpoint")
    require(sha(canonical(manifest["config"])) == manifest["config_sha256"], "Config checksum mismatch")
    with np.load(directory / "snapshot.npz", allow_pickle=False) as archive:
        state = State(manifest["config"], manifest["seed"], *(archive[name] for name in TABLES),
                      month=manifest["month"], replica=manifest["replica"])
    validate(state)
    require(digest(state) == manifest["snapshot_sha256"], "Snapshot checksum mismatch")
    return state, manifest
