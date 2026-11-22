"""Counter-based domain/period/entity draws, with no shared mutable RNG."""
import hashlib

import numpy as np


def key(seed, domain, month):
    return int.from_bytes(hashlib.sha256(f"demos-1:{seed}:{domain}:{month}".encode()).digest()[:8], "little")


def uniform(seed, domain, month, ids):
    z = np.asarray(ids, dtype=np.uint64) ^ np.uint64(key(seed, domain, month))
    z = (z ^ (z >> 30)) * np.uint64(0xBF58476D1CE4E5B9)
    z = (z ^ (z >> 27)) * np.uint64(0x94D049BB133111EB)
    return ((z ^ (z >> 31)) >> 11).astype(np.float64) / 2**53


def choose(weights, draws):
    cdf = np.cumsum(weights, dtype=float)
    cdf /= cdf[-1]
    return np.searchsorted(cdf, draws, side="right")
