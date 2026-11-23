import argparse
import os
import sys
from pathlib import Path

from .archive import locked, replay
from .client import NomosClient
from .contracts import canonical, parse, require
from .cycle import DEFAULTS, run
from .provider import Offline, OpenAIProvider, cents_micro


def configuration(path, live):
    override = parse(path.read_bytes()) if path else {}
    require(type(override) is dict and override.keys() <= DEFAULTS.keys(), "Configurazione sconosciuta")
    config = {**DEFAULTS, **override}
    require(all(type(value) is int and 0 <= value <= 10**12 for value in config.values()), "Limiti non validi")
    require(1 <= config["max_calls"] <= (12 if live else 600) and 3_000 <= config["input_tokens"] <= 32_000
            and 128 <= config["output_tokens"] <= 4_000 and 1 <= config["timeout"] <= 90
            and config["technical_attempts"] == config["max_proposals_per_period"] == 1, "Limiti fuori intervallo")
    if live:
        per_call = cents_micro(config["input_tokens"], config["output_tokens"], config)
        require(path and min(config["input_micro_usd_per_token"], config["output_micro_usd_per_token"]) > 0
                and per_call <= config["budget_micro_usd"], "Preventivo e tariffe esplicite obbligatori")
    return config


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description="Archon · client del Governo di Nova")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("dry-run", "decide"):
        action = sub.add_parser(name)
        action.add_argument("--config", type=Path)
        action.add_argument("--live", action="store_true")
        if name == "decide":
            action.add_argument("--authorize-paid-run", action="store_true")
            action.add_argument("--socket", type=Path, required=True)
            action.add_argument("--archive", type=Path, required=True)
            action.add_argument("--universe", required=True)
            action.add_argument("--token-file", type=Path, required=True)
    restore = sub.add_parser("replay")
    restore.add_argument("archive", type=Path)
    restore.add_argument("--expected", required=True)
    args = parser.parse_args()
    try:
        if args.command == "replay":
            with locked(args.archive, writable=False) as archive:
                result = replay(archive, args.expected)
        else:
            config = configuration(args.config, args.live)
            if args.command == "dry-run":
                ceiling = cents_micro(config["input_tokens"], config["output_tokens"], config)
                funded = config["budget_micro_usd"] // ceiling if ceiling else config["max_calls"]
                result = {"max_calls": min(config["max_calls"], funded), "per_call_micro_usd": ceiling,
                          "budget_micro_usd": config["budget_micro_usd"], "provider": "openai" if args.live else "offline"}
            else:
                require(not args.live or args.authorize_paid_run, "Spesa API non autorizzata")
                require(not args.authorize_paid_run or args.live, "Attivazione live obbligatoria")
                provider = OpenAIProvider(os.environ.get("ARCHON_MODEL"), config["timeout"]) if args.live else Offline()
                nomos = NomosClient(args.socket, args.token_file.read_text().strip(), args.universe)
                with locked(args.archive) as archive:
                    decision = run(archive, nomos, provider, config)
                    result = {"decision": decision, "anchor": archive.anchor}
        sys.stdout.buffer.write(canonical(result))
    except (ValueError, AttributeError, TypeError, RuntimeError, OSError, ImportError, KeyError, RecursionError) as error:
        # Provider exceptions never reach the console with request bodies or credentials.
        parser.exit(2, f"Archon: {error}\n")


if __name__ == "__main__":
    main()
