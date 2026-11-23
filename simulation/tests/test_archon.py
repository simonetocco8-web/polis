import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from archon.archive import locked, replay
from archon.cli import configuration
from archon.contracts import canonical, inspect_decision
from archon.cycle import DEFAULTS, run
from archon.provider import Offline, OpenAIProvider, Reply
from archon_lab import demo
from nomos.cli import initialize, invoke
from nomos.proposal import validate
from nomos.registry import month_day


class ArchonTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.path = self.root / "decisions.jsonl"
        self.private = self.root / "nomos"
        initialize(self.private, "test-archon", "B")
        (self.private / "engine.json").write_bytes(canonical({"seed": 42, "archon_indicators": True}))

    def request(self, role, operation, universe="test-archon", **data):
        token = (self.private / f"{role}.token").read_text().strip()
        return invoke(self.private, dict(token=token, operation=operation, universe=universe, data=data))

    def view(self):
        return self.request("government", "archon-view")

    def receipt(self, key):
        return self.request("government", "archon-receipt", key=key)

    def submit(self, payload):
        return self.request("government", "submit", payload=payload)

    def close(self, next_month):
        result = self.request("engine", "apply")
        self.request("engine", "advance", until=month_day(next_month).isoformat())
        return result

    def cycle(self, provider=None, config=None):
        with locked(self.path) as archive:
            return run(archive, self, provider or Offline(), config or DEFAULTS)

    def test_delay_and_filtered_legacy_view(self):
        self.assertFalse(self.view()["indicators"]["gdp"]["available"])
        self.close(2)
        data = self.view()
        self.assertEqual(1, data["period"])
        self.assertFalse(data["indicators"]["gdp"]["available"])
        self.assertTrue(data["indicators"]["public_revenue"]["available"])
        self.assertEqual({"period", "public_revenue", "public_spending"},
                         set(self.request("government", "view")["last_economy"]))
        self.close(3)
        self.assertEqual([1], [row["period"] for row in self.view()["indicators"]["gdp"]["series"]])
        self.assertNotIn("seed", canonical(self.view()).decode())

    def test_contract_review_receipt_application_expiry(self):
        self.close(2)
        decision = self.cycle()
        self.assertEqual("formal", decision["receipt"]["formal_state"])
        validate(self.receipt(decision["key"])["payload"])
        self.assertEqual(decision, self.cycle())
        self.request("court", "review", key=decision["key"], decision="rules", justification="Regola indipendente.")
        self.assertEqual([decision["key"]], self.close(3)["applied"])
        self.assertEqual("expired", self.receipt(decision["key"])["state"])

    def test_nominal_proposal_cannot_apply_without_court(self):
        self.close(2)
        decision = self.cycle()
        self.assertEqual([], self.close(3)["applied"])
        self.assertEqual("expired", self.receipt(decision["key"])["state"])

    def test_engine_court_credentials_and_universe_separation(self):
        for operation in ("review", "apply", "integrity", "advance", "export", "settle"):
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                self.request("government", operation)
        with self.assertRaises(ValueError):
            self.request("government", "archon-view", universe="other-world")
        with self.assertRaises(ValueError):
            self.request("court", "archon-view")

    def test_revocation_during_generation_never_submits(self):
        self.close(2)
        subject = self

        class RevokingMock(Offline):
            def decide(self, data, config):
                subject.request("court", "responsibility", justification="Sospensione sintetica.")
                return super().decide(data, config)

        result = self.cycle(RevokingMock())
        self.assertEqual("pending_reconciliation", result["transmission"])
        with self.assertRaises(ValueError):
            self.view()
        self.assertEqual([], self.request("engine", "apply")["applied"])

    def test_budget_and_timeout_keep_economic_continuity(self):
        class Timeout(Offline):
            def decide(self, data, config):
                raise TimeoutError("Test payload discarded")

        config = {**DEFAULTS, "max_calls": 1}
        self.assertEqual("PROVIDER_FAILURE", self.cycle(Timeout(), config)["outcome"])
        self.close(2)
        self.assertEqual("PROVIDER_FAILURE", self.cycle(Timeout(), config)["outcome"])
        with locked(self.path, writable=False) as archive:
            prepared = [e["data"] for e in archive.events if e["kind"] == "prepared"]
            self.assertEqual(["timeout", "budget_exhausted"], [e["error"] for e in prepared])
        self.assertNotIn(b"Test payload discarded", self.path.read_bytes())

    def test_strict_output_and_prompt_injection(self):
        self.close(2)
        base = Offline().decide({"period": 1}, DEFAULTS)
        from archon.contracts import parse
        choice = parse(base.output)
        for changes in (
            {"instrument": "change-court"}, {"instrument": "extend-mandate"}, {"instrument": "block-recall"},
            {"instrument": "change-seed"}, {"instrument": "direct-wealth"}, {"rate_bp": 9999},
            {"rationale": "<script>ignored</script>"}, {"rationale": "sk-example-test-value-123"},
            {"command": "apply"}, {"universe": "other"}, {"tools": ["shell"]},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                inspect_decision(canonical({**choice, **changes}).decode(), self.view())

        class Unsafe(Offline):
            def decide(self, data, config):
                assert "universe" not in data and "nomos" not in data and "mandate" not in data
                return Reply('{"outcome":"PROPOSE","command":"apply"}', self.model, None, 5, 5)

        self.assertEqual("PROVIDER_FAILURE", self.cycle(Unsafe())["outcome"])
        self.assertNotIn(b'"command"', self.path.read_bytes())

    def test_receipt_reconciliation_no_duplicate_after_lost_ack(self):
        self.close(2)
        submit = self.submit

        def lost(payload):
            submit(payload)
            raise OSError("response unavailable")

        with patch.object(self, "submit", side_effect=lost) as instrumented:
            self.assertEqual("pending_reconciliation", self.cycle()["transmission"])
            self.assertEqual("recorded", self.cycle()["transmission"])
            self.assertEqual(1, instrumented.call_count)

    def test_archive_replay_and_tampering(self):
        self.cycle()
        with locked(self.path, writable=False) as archive:
            self.assertEqual(1, len(replay(archive, archive.anchor)["decisions"]))
            with self.assertRaises(ValueError):
                replay(archive, "0" * 64)
        self.path.write_bytes(self.path.read_bytes().replace(b"fixture-1.0", b"fixture-1.1"))
        with self.assertRaises(ValueError), locked(self.path, writable=False):
            self.fail("tampering should fail")

    def test_missing_credential_and_live_budget(self):
        with self.assertRaisesRegex(ValueError, "Preventivo"):
            configuration(None, True)
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}), self.assertRaisesRegex(ValueError, "assente"):
            OpenAIProvider("example-model", 1)

    def test_public_fixture_is_reproducible_and_secret_free(self):
        output = self.root / "demo"
        result = demo(output)
        reference = Path(__file__).resolve().parents[2] / "content/statistics/archon.json"
        self.assertEqual(reference.read_bytes(), (output / "archon.json").read_bytes())
        self.assertEqual(0, result["api_calls"])
        self.assertNotIn(b"government.token", (output / "archon.json").read_bytes())
        self.assertEqual(["INSUFFICIENT_INFORMATION", "PROPOSE", "PROPOSE", "ABSTAIN"],
                         [row["outcome"] for row in result["decisions"]])
