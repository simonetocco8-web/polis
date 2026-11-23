import argparse
import fcntl
import hmac
import os
import secrets
import socketserver
import sys
from pathlib import Path

from demos.config import canonical, sha

from .journal import Journal, strict_json
from .registry import COMMANDS, SCENARIOS, require

LIMIT = 65536


def initialize(directory, universe, regime):
    journal = Journal(universe, regime)
    directory.mkdir(mode=0o700)
    keys = {}
    for role in (*COMMANDS, "operator"):
        token = secrets.token_hex(32)
        keys[role] = sha(token.encode())
        (directory / f"{role}.token").write_text(token + "\n")
    (directory / "roles.json").write_bytes(canonical({"keys": keys, "government_mandate": journal.state.governor}))
    (directory / "journal.jsonl").write_bytes(canonical(journal.events[0]))
    return {"universe": universe, "regime": regime, "anchor": journal.anchor}


def authenticate(directory, token, mandate):
    require(isinstance(token, str) and len(token) == 64 and token.isascii(), "Credenziale non valida")
    digest = sha(token.encode())
    roles = strict_json((directory / "roles.json").read_bytes())
    for role, expected in roles["keys"].items():
        if hmac.compare_digest(digest, expected):
            require(role != "government" or (mandate is not None and roles["government_mandate"] == mandate),
                    "Credenziale del mandato inattiva")
            return role
    raise ValueError("Credenziale non valida")


def invoke(directory, request):
    require(type(request) is dict and set(request) == {"token", "universe", "operation", "data"},
            "Busta del comando non valida")
    operation = request["operation"]
    require(isinstance(operation, str) and type(request["data"]) is dict, "Comando non valido")
    with (directory / "journal.jsonl").open("r+b") as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        rows = [strict_json(line) for line in file]
        journal = Journal.replay(rows)
        role = authenticate(directory, request["token"], journal.state.governor)
        require(request["universe"] == journal.state.universe, "Universo estraneo")
        if operation in ("archon-view", "archon-receipt"):
            from .information import observation, receipt
            from .registry import identifier
            require(role == "government" and journal.state.regime == "B", "Vista non autorizzata")
            if operation == "archon-view":
                require(not request["data"], "Argomenti inattesi")
                return observation(journal)
            require(set(request["data"]) == {"key"}, "Riferimento obbligatorio")
            return receipt(journal, identifier(request["data"]["key"]))
        if operation == "view":
            require(role == "government" and not request["data"], "Vista non autorizzata")
            return journal.government_view()
        if operation in ("validate", "replay", "export"):
            require(role in ("operator", "observer"), "Audit non autorizzato")
            if operation == "export":
                require(not request["data"], "Argomenti di esportazione non validi")
                from .publication import public_report
                return public_report(journal)
            require(set(request["data"]) == {"expected"} and isinstance(request["data"]["expected"], str)
                    and request["data"]["expected"] == journal.anchor, "Testa attesa obbligatoria")
            return {"anchor": journal.anchor, "events": len(rows), "period": journal.state.period}
        require(operation != "settle", "Chiusura riservata al collegamento economico")
        if operation == "apply":
            require(role == "engine" and not request["data"], "Applicazione riservata al motore")
            from .demo import reconstruct
            from .economy import settle
            settings = directory / "engine.json"
            economy = reconstruct(journal, settings)
            publish = strict_json(settings.read_bytes()).get("archon_indicators") is True
            _, stats = settle(journal, economy, stabilized=True, publish=publish)
            result = {"period": stats["month"], "applied": journal.events[-1]["result"]["applied"]}
        else:
            result = journal.apply(role, operation, request["data"])
        if len(journal.events) != len(rows):
            file.seek(0, os.SEEK_END)
            file.write(canonical(journal.events[-1]))
            file.flush()
            os.fsync(file.fileno())
        return result


def provision_government(directory):
    """Local service administrator provisions the next independent mandate."""
    with (directory / "journal.jsonl").open("rb") as file:
        fcntl.flock(file, fcntl.LOCK_EX)
        journal = Journal.replay([strict_json(line) for line in file])
        mandate = journal.state.governor
        roles = strict_json((directory / "roles.json").read_bytes())
        require(mandate and mandate != roles["government_mandate"], "Nessun nuovo mandato da abilitare")
        token = secrets.token_hex(32)
        roles["keys"]["government"] = sha(token.encode())
        roles["government_mandate"] = mandate
        next_roles = directory / "roles.next"
        next_token = directory / "government.next"
        next_roles.write_bytes(canonical(roles))
        next_token.write_text(token + "\n")
        next_token.replace(directory / "government.token")
        next_roles.replace(directory / "roles.json")
        return {"mandate": mandate}


def serve(directory, socket):
    class Request(socketserver.StreamRequestHandler):
        def handle(self):
            self.connection.settimeout(3)
            try:
                raw = self.rfile.readline(LIMIT + 1)
                require(len(raw) <= LIMIT and raw.endswith(b"\n"), "Richiesta fuori formato")
                output = {"ok": True, "result": invoke(directory, strict_json(raw))}
            except (OSError, ValueError, TypeError, KeyError, RecursionError):
                output = {"ok": False, "error": "Richiesta respinta"}
            try:
                self.wfile.write(canonical(output))
            except OSError:
                pass

    server = socketserver.UnixStreamServer(str(socket), Request)
    try:
        socket.chmod(0o660)
        server.serve_forever()
    finally:
        server.server_close()
        socket.unlink()


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description="Nomos · registro giuridico locale")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("directory", type=Path)
    init.add_argument("universe")
    init.add_argument("regime", choices=list(SCENARIOS))
    request = commands.add_parser("request", help="Legge una busta JSON da stdin")
    request.add_argument("directory", type=Path)
    rotate = commands.add_parser("provision-government")
    rotate.add_argument("directory", type=Path)
    service = commands.add_parser("serve")
    service.add_argument("directory", type=Path)
    service.add_argument("socket", type=Path)
    demo = commands.add_parser("demo")
    demo.add_argument("directory", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = initialize(args.directory, args.universe, args.regime)
        elif args.command == "provision-government":
            result = provision_government(args.directory)
        elif args.command == "serve":
            serve(args.directory, args.socket)
            return
        elif args.command == "demo":
            from .demo import build
            result = build(args.directory)
        else:
            raw = sys.stdin.buffer.read(LIMIT + 1)
            require(len(raw) <= LIMIT, "Richiesta troppo grande")
            result = invoke(args.directory, strict_json(raw))
        sys.stdout.buffer.write(canonical(result))
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as error:
        parser.exit(2, f"{error}\n")


if __name__ == "__main__":
    main()
