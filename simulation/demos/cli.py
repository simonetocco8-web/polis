import argparse
import csv
import sys
from pathlib import Path

from .config import PROFILES, canonical, load_config
from .engine import generate
from .events import replay, run
from .indicators import compare, export
from .snapshot import digest, restore, save
from .sources import acquire


def write_csv(path, data):
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["gruppo", "categoria", "valore", "unità"])
        for group, counts in data["groups"].items():
            for category, count in counts.items():
                unit = "imprese" if group in ("sectors", "firm_sizes") else "nuclei" if group == "households" else "abitazioni" if group == "dwelling_capacity" else "persone"
                writer.writerow([group, category, count, unit])


def main():
    parser = argparse.ArgumentParser(prog="python -m demos.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("generate")
    new.add_argument("output", type=Path)
    new.add_argument("--profile", choices=PROFILES, default="standard")
    new.add_argument("--reference", choices=("eu27", "hypothetical"), default="eu27")
    new.add_argument("--seed", type=int, required=True)
    source = commands.add_parser("sources")
    source.add_argument("output", type=Path)
    source.add_argument("--offline", action="store_true")
    for name in ("validate", "run", "replay", "clone", "export", "compare"):
        sub = commands.add_parser(name)
        sub.add_argument("snapshot", type=Path)
        if name not in ("validate", "compare"):
            sub.add_argument("output", type=Path)
        if name == "run":
            sub.add_argument("--months", required=True, type=int)
        if name == "replay":
            sub.add_argument("--events", required=True, type=Path)
    args = parser.parse_args()
    if args.command == "sources":
        acquire(args.output, args.offline)
        return
    if args.command == "generate":
        args.output.mkdir(parents=True, exist_ok=False)
        state = generate(load_config(args.profile, args.reference), args.seed)
        print(save(state, args.output)["snapshot_sha256"])
        return
    state, manifest = restore(args.snapshot)
    if args.command == "validate":
        print(digest(state))
    elif args.command == "compare":
        sys.stdout.buffer.write(canonical(compare(state)))
    else:
        args.output.mkdir(parents=True, exist_ok=False)
        if args.command == "run":
            run(state, args.months, args.output / "events.jsonl")
            print(save(state, args.output)["snapshot_sha256"])
        elif args.command == "replay":
            replay(state, args.events)
            print(save(state, args.output)["snapshot_sha256"])
        elif args.command == "clone":
            for label in "ABCDEF":
                save(state.clone(label), args.output / label)
        elif args.command == "export":
            data = export(state, manifest)
            (args.output / "statistics.json").write_bytes(canonical(data))
            write_csv(args.output / "statistics.csv", data)


if __name__ == "__main__":
    main()
