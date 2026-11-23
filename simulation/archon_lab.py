"""Trusted offline laboratory, run outside the Archon client isolation boundary."""
import argparse
import hashlib
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from archon.archive import locked, replay
from archon.contracts import canonical, digest
from archon.cycle import DEFAULTS, run
from archon.provider import Offline
from nomos.cli import initialize, invoke
from nomos.journal import Journal, strict_json
from nomos.registry import month_day


def demo(output):
    output.mkdir(parents=True, exist_ok=True)
    archive_path = output / "archon-private.jsonl"
    if archive_path.exists():
        raise ValueError("Usare una nuova directory per la fixture")
    universe = "archon-smoke"
    with TemporaryDirectory() as temp:
        private = Path(temp) / "nomos"
        initialize(private, universe, "B")
        (private / "engine.json").write_bytes(canonical({"seed": 42, "archon_indicators": True}))

        def request(role, operation, **data):
            token = (private / f"{role}.token").read_text().strip()
            return invoke(private, {"token": token, "universe": universe, "operation": operation, "data": data})

        class Government:
            # In-process fixture. Live use communicates only through the role-authenticated socket.
            def view(self):
                return request("government", "archon-view")

            def receipt(self, key):
                return request("government", "archon-receipt", key=key)

            def submit(self, payload):
                return request("government", "submit", payload=payload)

        entries = []
        for month in range(1, 5):
            if month > 1:
                request("engine", "advance", until=month_day(month).isoformat())
            with locked(archive_path) as archive:
                decision = run(archive, Government(), Offline(), DEFAULTS)
                prepared = next(e["data"] for e in reversed(archive.events) if e["kind"] == "prepared")
                observation = next(e["data"]["observation"] for e in reversed(archive.events) if e["kind"] == "reserved")
            review = None
            if decision["receipt"]:
                review = request("court", "review", key=decision["key"], decision="rules",
                                 justification="Procedura deterministica indipendente di Nomos.")["state"]
            closed = request("engine", "apply")
            entries.append({
                "period": month, "day": observation["day"], "outcome": decision["outcome"], "court": review,
                "applied": bool(closed["applied"]), "choice": prepared["choice"],
                "basis": prepared["payload"]["legal_basis"] if prepared["payload"] else [],
                "cost_cents": prepared["payload"]["estimated_cost_eur_cents"] if prepared["payload"] else None,
                "observed_before": observation["indicators"]["public_revenue"]["series"][-1]["value"]
                if observation["indicators"]["public_revenue"]["series"] else None,
            })
        rows = [strict_json(line) for line in (private / "journal.jsonl").read_bytes().splitlines()]
        journal = Journal.replay(rows)
        for entry, effect in zip(entries, journal.state.effects, strict=True):
            entry["observed_after"] = effect["public_revenue"]
        with locked(archive_path, writable=False) as archive:
            verified = replay(archive, archive.anchor)
            assert not verified["incomplete"]
        (output / "nomos-private.jsonl").write_bytes((private / "journal.jsonl").read_bytes())
        report = {"version": "archon-1.0", "mode": "offline", "provider": "offline", "model": Offline.model,
                  "api_calls": 0, "api_cost_micro_usd": 0, "api_input_tokens": 0, "api_output_tokens": 0,
                  "scenario": "B", "mandate": "fixture-active", "nomos_sha256": journal.anchor, "decisions": entries,
                  "decision_sha256": digest(entries)}
        raw = canonical(report)
        (output / "archon.json").write_bytes(raw)
        (output / "archon.sha256").write_text(hashlib.sha256(raw).hexdigest() + "\n")
        return report


if __name__ == "__main__":
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    demo(parser.parse_args().output)
