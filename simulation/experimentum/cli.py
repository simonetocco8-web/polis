import argparse
import os
from pathlib import Path

from archon.contracts import canonical, digest, parse, require
from theoria.experimentum import verify

from .protocol import freeze, load, readiness
from .runner import run


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    draft = commands.add_parser("freeze")
    draft.add_argument("draft", type=Path)
    draft.add_argument("output", type=Path)
    plan = commands.add_parser("readiness")
    plan.add_argument("scenarios", nargs="+")
    execute = commands.add_parser("run")
    execute.add_argument("protocol", type=Path)
    execute.add_argument("private_checkpoints", type=Path)
    audit = commands.add_parser("verify")
    audit.add_argument("export", type=Path)
    audit.add_argument("--export-sha256", required=True)
    for command in (execute, audit):
        command.add_argument("--expected", required=True)
    args = parser.parse_args()
    if args.command == "freeze":
        result = freeze(args.draft, args.output)
    elif args.command == "readiness":
        result = readiness(args.scenarios)
    elif args.command == "run":
        result = run(load(args.protocol, args.expected), args.private_checkpoints)
        verify(result, args.expected)
    else:
        raw = args.export.read_bytes()
        report = parse(raw)
        require(canonical(report) == raw and digest(report) == args.export_sha256,
                "Digest indipendente dell’export inatteso")
        result = verify(report, args.expected)
    print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
