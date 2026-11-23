import hashlib
import json
from pathlib import Path

import numpy as np

from demos.config import canonical, sha
from demos.snapshot import digest as demos_digest, restore as demos_restore, save as demos_save
from demos.validation import require

from . import VERSION
from .state import Economy, reconcile


def header(state):
    return {"schema": "oikonomia-state-1", "model": VERSION, "origin": state.origin,
            "demography": demos_digest(state.demographics), "config": state.config,
            "price": state.price, "journal": state.journal, "variant": state.variant}


def digest(state):
    result = hashlib.sha256(canonical(header(state)))
    for key, value in sorted(state.accounts.items()):
        result.update(canonical([key, value.dtype.str, len(value)]))
        result.update(value.tobytes())
    return result.hexdigest()


def save(state, folder: Path):
    reconcile(state)
    demos_save(state.demographics, folder / "demography")
    np.savez_compressed(folder / "accounts.npz", **state.accounts)
    manifest = dict(header(state), snapshot_sha256=digest(state), config_sha256=sha(canonical(state.config)))
    (folder / "economic-manifest.json").write_bytes(canonical(manifest))
    return manifest


def restore(folder: Path):
    meta = json.loads((folder / "economic-manifest.json").read_bytes())
    require(meta["schema"] == "oikonomia-state-1" and meta["model"] == VERSION, "Unsupported economic snapshot")
    d, _ = demos_restore(folder / "demography")
    with np.load(folder / "accounts.npz", allow_pickle=False) as arrays:
        accounts = dict(arrays)
    state = Economy(d, meta["config"], meta["origin"], accounts, meta["price"], meta["journal"], meta["variant"])
    reconcile(state)
    require(digest(state) == meta["snapshot_sha256"] and demos_digest(d) == meta["demography"]
            and sha(canonical(state.config)) == meta["config_sha256"], "Economic snapshot hash mismatch")
    return state
