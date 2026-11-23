import argparse
import os
from pathlib import Path

from archon.contracts import canonical
from .audit import audit, candidate_projection, public_fixture


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    fixture = sub.add_parser("fixture")
    fixture.add_argument("source", type=Path)
    private = sub.add_parser("audit")
    for key in ("archon", "nomos"):
        private.add_argument(key, type=Path)
        private.add_argument(f"--{key}-anchor", required=True)
    private.add_argument("--candidate", type=Path)
    args = parser.parse_args()
    if args.command == "fixture":
        result = public_fixture(args.source)
    else:
        result = audit(args.archon, args.nomos, args.archon_anchor, args.nomos_anchor)
        if args.candidate and result.get("integrity") == "VERIFIED":
            with args.candidate.open("xb") as file:
                file.write(canonical(candidate_projection(result)))
    print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
