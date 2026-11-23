import argparse
from contextlib import nullcontext
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import platform
import resource
import time

import numpy as np

from demos.config import canonical, sha
from demos.snapshot import restore as demos_restore
from demos.validation import require

from . import VERSION
from .engine import VARIANTS, step
from .snapshot import digest, restore, save
from .state import attach


def execute(state, months, folder, detail=False):
    require(0 < months <= state.demographics.config["months"] - state.demographics.month, "Invalid horizon")
    folder.mkdir(parents=True, exist_ok=False)
    initial = digest(state)
    d = state.demographics
    opening_population = len(d.people[d.people["status"] == 0])
    opening_households = len(np.unique(d.people["household"][d.people["status"] == 0]))
    opening_firms = len(d.firms)
    start = time.perf_counter()
    rows = []
    with (gzip.open(folder / "journal.jsonl.gz", "wb") if detail else nullcontext(None)) as ledger:
        with (folder / "events.jsonl").open("wb") as events:
            events.write(canonical({"initial": initial, "months": months, "accounts_detail": detail}))
            for _ in range(months):
                row, event = step(state, ledger)
                rows.append(row)
                events.write(canonical({"row": row, **event}))
            events.write(canonical({"final": digest(state), "journal": state.journal}))
    manifest = save(state, folder)
    for index, row in enumerate(rows):
        row["inflation_monthly_percent"] = round((row["cpi"] / rows[index-1]["cpi"] - 1) * 100, 6) if index else None
        annual = sum(month["gdp"] for month in rows[max(0, index-11):index+1])
        row["debt_gdp_percent"] = round(100 * row["public_debt"] / annual, 6) if index >= 11 and annual > 0 else None
        deficit = -sum(month["fiscal_balance"] for month in rows[max(0, index-11):index+1])
        row["deficit_gdp_percent"] = round(100 * deficit / annual, 6) if index >= 11 and annual > 0 else None
    summary = {"schema": "oikonomia-aggregate-1", "model": VERSION, "scenario": state.variant,
               "status": "prova-tecnica-non-calibrata", "demos_origin": state.origin, "config_sha256": manifest["config_sha256"],
               "initial_sha256": initial, "final_sha256": manifest["snapshot_sha256"], "journal_sha256": state.journal,
               "generated_at": datetime.now(timezone.utc).isoformat(), "opening_population": opening_population,
               "opening_households": opening_households, "opening_firms": opening_firms, "months": months, "base_year": state.config["base_year"],
               "reference": d.config["reference"], "trade": "economia-chiusa", "polis_index": None, "rows": rows}
    payload = canonical(summary)
    (folder / "statistics.json").write_bytes(payload)
    (folder / "statistics.sha256").write_text(sha(payload) + "\n")
    (folder / "benchmark.json").write_bytes(canonical({
        "seconds": round(time.perf_counter() - start, 3),
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python": platform.python_version(), "numpy": np.__version__,
        "checkpoint_bytes": (folder / "accounts.npz").stat().st_size + (folder / "demography/snapshot.npz").stat().st_size,
        "events_bytes": (folder / "events.jsonl").stat().st_size,
    }))
    return summary


def replay(state, path):
    with path.open() as events:
        start = json.loads(next(events))
        require(start["initial"] == digest(state), "Replay origin mismatch")
        require(type(start["months"]) is int and 0 < start["months"] <= state.demographics.config["months"] - state.demographics.month,
                "Invalid replay horizon")
        for _ in range(start["months"]):
            row, event = step(state)
            require(json.loads(next(events)) == {"row": row, **event}, "Replay mismatch")
        require(json.loads(next(events)) == {"final": digest(state), "journal": state.journal}, "Replay checksum mismatch")
        require(not events.read(), "Unexpected events after trailer")


def main():
    parser = argparse.ArgumentParser(prog="python -m oikonomia.cli")
    cmd = parser.add_subparsers(dest="command", required=True)
    for name in ("migrate", "run", "validate", "replay", "clone"):
        sub = cmd.add_parser(name)
        sub.add_argument("snapshot", type=Path)
        if name != "validate":
            sub.add_argument("output", type=Path)
        if name == "migrate":
            sub.add_argument("--variant", choices=VARIANTS, default="baseline")
        if name == "run":
            sub.add_argument("--months", type=int, required=True)
            sub.add_argument("--journal-detail", action="store_true")
        if name == "replay":
            sub.add_argument("--events", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "migrate":
        demos, _ = demos_restore(args.snapshot)
        args.output.mkdir(parents=True, exist_ok=False)
        save(attach(demos, args.variant), args.output)
        return
    state = restore(args.snapshot)
    if args.command == "run":
        execute(state, args.months, args.output, args.journal_detail)
    elif args.command == "replay":
        replay(state, args.events)
        args.output.mkdir(parents=True, exist_ok=False)
        save(state, args.output)
    elif args.command == "clone":
        args.output.mkdir(parents=True, exist_ok=False)
        for label in "ABCDEF":
            save(state.clone(label), args.output / label)
    print(digest(state))


if __name__ == "__main__":
    main()
