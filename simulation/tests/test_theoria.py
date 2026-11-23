import json
import tempfile
import unittest
from pathlib import Path

from archon_lab import demo
from nomos.cli import initialize, invoke
from theoria.audit import audit, candidate_projection, classification, comparison_ready, public_fixture, rules_hash


class TheoriaTest(unittest.TestCase):
    def test_archive_replay_missing_tampering_and_projection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture = demo(root)
            a, n = root / "archon-private.jsonl", root / "nomos-private.jsonl"
            ah = json.loads(a.read_bytes().splitlines()[-1])["hash"]
            inputs = a, n, ah, fixture["nomos_sha256"]
            report = audit(*inputs)
            self.assertEqual("VERIFIED", report["status"])
            self.assertEqual("PARTIALLY_VERIFIED", report["provenance"])
            self.assertEqual(report, audit(*inputs))
            cases = report["cases"]
            self.assertEqual(["INSUFFICIENT_INFORMATION", "PROPOSE", "PROPOSE", "ABSTAIN"],
                             [case["outcome"] for case in cases])
            self.assertIn("gdp", cases[1]["missing"])
            self.assertFalse(cases[1]["information"]["gdp"]["available"])
            self.assertTrue(cases[1]["institution"]["receipt"]["checks"]["syntax"])
            self.assertIn("gdp", cases[2]["available"])
            self.assertEqual("NOT_APPLICABLE", cases[-1]["effects_status"])
            reduced = candidate_projection(report)
            self.assertEqual("candidate-private-not-authorized", reduced["mode"])
            self.assertNotIn("archon-smoke", json.dumps(reduced))
            self.assertNotIn("rationale", json.dumps(reduced))
            self.assertEqual("INTEGRITY_FAILURE", audit(a, n, "0"*64, inputs[3])["status"])
            self.assertEqual("INSUFFICIENT_EVIDENCE", audit(root/"missing", n, ah, inputs[3])["status"])
            a.write_bytes(a.read_bytes().replace(b"fixture-1.0", b"fixture-0.0"))
            self.assertEqual("INTEGRITY_FAILURE", audit(*inputs)["status"])
            with self.assertRaises(ValueError):
                public_fixture(a)

    def test_states_do_not_imply_causal_success(self):
        for state in ("review", "formal", "authorized"):
            self.assertEqual(("PENDING_OUTCOME", "PENDING_OUTCOME"), classification("PROPOSE", state))
        for state in ("suspended", "revoked", "rejected"):
            self.assertEqual("INSUFFICIENT_EVIDENCE", classification("PROPOSE", state)[1])
        self.assertEqual("PENDING_OUTCOME", classification("PROPOSE", "executive")[1])
        self.assertEqual("UNVERIFIED", classification("PROVIDER_FAILURE")[0])
        self.assertEqual("NOT_APPLICABLE", classification("ABSTAIN")[1])
        with self.assertRaises(ValueError):
            classification("UNKNOWN")

    def test_observer_cannot_mutate_or_cross_universes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)/"nomos"
            initialize(root, "observer-test", "B")
            token = (root/"observer.token").read_text().strip()
            before = (root/"journal.jsonl").read_bytes()
            request = dict(token=token, universe="observer-test", operation="observe", data={})
            self.assertEqual(0, invoke(root, request)["period"])
            for op in ("view", "archon-view", "submit", "act", "review", "advance", "apply", "settle", "replacement", "ratify"):
                with self.subTest(op=op), self.assertRaises(ValueError):
                    invoke(root, dict(request, operation=op))
            with self.assertRaises(ValueError):
                invoke(root, dict(request, universe="other"))
            self.assertEqual(before, (root/"journal.jsonl").read_bytes())

    def test_release_fixture_and_comparison_preconditions(self):
        root = Path(__file__).resolve().parents[2] / "content/statistics"
        a = public_fixture(root/"archon.json")
        self.assertEqual(a, json.loads((root/"theoria.json").read_bytes()))
        self.assertEqual(rules_hash(), a["rules_sha256"])
        with self.assertRaises(ValueError):
            comparison_ready({"B": {}})
        item = dict.fromkeys(("initial","shocks","calibration","window","exclusions","statistical_plan"), "a"*64)
        item["replicas"] = ["replica-1","replica-2"]
        self.assertEqual({"matched_manifests": True, "status": "INSUFFICIENT_EVIDENCE"},
                         comparison_ready(dict.fromkeys("ABCDEF", item)))
