import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from archon.contracts import canonical, digest, parse
from experimentum.protocol import freeze, load, readiness, validate
from experimentum.runner import run, shock_window
from experimentum.statistics import describe
from theoria.experimentum import verify

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "experimentum/pilot-001.json"


class ExperimentumTest(unittest.TestCase):
    def setUp(self):
        self.frozen = parse(FROZEN.read_bytes())
        self.anchor = self.frozen["protocol_sha256"]
        self.protocol = load(FROZEN, self.anchor)

    def test_preregistration_and_comparison_gates(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            draft, frozen = folder/"draft.json", folder/"frozen.json"
            draft.write_bytes(canonical(self.protocol))
            freeze(draft, frozen)
            with self.assertRaises(FileExistsError):
                freeze(draft, frozen)
            frozen.write_bytes(canonical({**self.frozen, "protocol": {**self.protocol, "months": 5}}))
            with self.assertRaises(ValueError):
                load(frozen, self.anchor)
        for alteration in ({"scenarios": ["A", "B"]}, {"mode": "confirmatory"}, {"stage": "extended"},
                           {"months": 600}, {"replicas": [2,2]}, {"budget_api_micro_usd": 1}, {"calibration": "validated"}):
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                validate({**self.protocol, **alteration})
        self.assertEqual("NOT_READY", readiness(["A","B"])["state"])

    def test_reproduction_and_independent_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = run(self.protocol, root/"first")
            self.assertEqual(report, run(self.protocol, root/"second"))
            self.assertEqual(3, len({r["checkpoint_sha256"] for r in report["replicas"]}))
            self.assertEqual("REPRODUCED", verify(report, self.anchor)["technical"])
            self.assertEqual("NOT_READY", verify(report, self.anchor)["comparability"])
            self.assertEqual(canonical(report), (ROOT.parent/"content/statistics/experimentum.json").read_bytes())
            self.assertEqual(digest(report), (ROOT.parent/"content/statistics/experimentum.sha256").read_text().strip())
            for replica in report["replicas"]:
                self.assertEqual(replica["checkpoint_sha256"], replica["replay_checkpoint_sha256"])
                self.assertEqual(replica["anchor"], replica["replay_anchor"])
            for field in ("gdp", "previous"):
                changed = copy.deepcopy(report)
                changed["replicas"][0]["series"][0][field] = 0
                with self.assertRaises(ValueError):
                    verify(changed, self.anchor)
            with self.assertRaises(ValueError):
                verify({**report, "sources": {}}, self.anchor)
            with self.assertRaises(ValueError):
                verify(report, "0"*64)

    def test_shock_independence_and_failed_replica_retention(self):
        first = shock_window(101, 6)
        self.assertNotEqual(first["commitment"], shock_window(307, 6)["commitment"])
        self.assertEqual(first, shock_window(101, 6))
        with tempfile.TemporaryDirectory() as tmp:
            with patch("experimentum.runner.step", side_effect=RuntimeError("fixture error")):
                report = run(self.protocol, Path(tmp)/"run")
            self.assertEqual("INVALIDATED", verify(report, self.anchor)["technical"])
            self.assertEqual(3, report["aggregates"][0]["indicators"]["gdp"]["missing"])
            self.assertEqual(["engine-error"]*3, [r["error"] for r in report["replicas"]])
            self.assertEqual([], report["exclusions"])

    def test_economic_failure_and_missing_are_distinct(self):
        row = {"month": 1, "gdp": 0, "units_produced": 0, "unemployment_percent": None,
               "public_revenue": 0, "public_arrears": True, "firm_failures": 1}
        stats = describe([{"series": [row]}], 1)[0]["indicators"]
        self.assertEqual(1, stats["public_arrears"]["mean"])
        self.assertEqual(0, stats["gdp"]["mean"])
        self.assertIsNone(stats["unemployment_percent"]["mean"])
