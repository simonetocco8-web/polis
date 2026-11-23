import copy
import tempfile
import unittest
from pathlib import Path

from demos.config import ROOT, canonical
from nomos.cli import initialize, invoke, provision_government
from nomos.demo import BALLOT, REASON, build, fiscal, new_economy, reconstruct
from nomos.economy import settle
from nomos.journal import Journal, strict_json
from nomos.registry import SCENARIOS, month_day

FINDINGS = dict.fromkeys(("necessity", "proportionality", "equity", "coverage"), REASON)


class NomosTest(unittest.TestCase):
    def setUp(self):
        self.journal = Journal("test-nova", "B")

    def call(self, role, operation, **data):
        return self.journal.apply(role, operation, data)

    def submit(self, key="fiscal-01", role="government", **changes):
        return self.call(role, "submit", payload=fiscal(key, **changes))

    def review(self, key="fiscal-01", decision="rules", **data):
        return self.call("court", "review", key=key, decision=decision, justification=REASON, **data)

    def settle_empty(self, month, receipts=None):
        self.call("engine", "settle", period=month, receipts=receipts or [], economic_anchor="0" * 64,
                  effect={"public_spending": 0, "public_revenue": 0})

    def advance(self, date):
        return self.call("engine", "advance", until=date)

    def test_formal_review_application_and_expiry(self):
        state = new_economy("test-nova", 42)
        self.assertEqual("formal", self.submit()["state"])
        self.assertEqual({}, self.journal.state.policies())
        self.assertEqual("authorized", self.review()["state"])
        next_state, approved = settle(self.journal, state)
        _, baseline = settle(Journal("test-nova", "B"), state)
        self.assertGreater(approved["public_revenue"], baseline["public_revenue"])
        self.assertEqual(1500, next_state.config["income_tax_bp"])
        self.assertEqual(0, state.demographics.month)
        with self.assertRaises(ValueError):
            settle(self.journal, state)
        self.advance("2022-02-01")
        self.assertEqual("expired", self.journal.state.acts["fiscal-01"]["state"])
        self.assertEqual({}, self.journal.state.policies())

    def test_control_and_authorized_sales_tax_on_stabilitas(self):
        changes = {"instrument": "sales-tax", "parameters": {"rate-bp": 600}}
        self.submit(**changes)
        self.assertEqual("review", self.review()["state"])
        self.assertEqual({}, self.journal.state.policies())
        with self.assertRaises(ValueError):
            self.review(decision="approve")
        self.review(decision="approve", findings=FINDINGS)
        opening = new_economy("test-nova", 42)
        _, taxed = settle(self.journal, opening, stabilized=True)
        _, control = settle(Journal("test-nova", "B"), opening, stabilized=True)
        self.assertGreater(taxed["cpi"], control["cpi"])

    def test_reject_incompetent_proposal(self):
        result = self.submit(role="technical-council")
        self.assertFalse(result["checks"]["competence"])
        self.assertEqual("rejected", result["state"])

    def test_hard_vetoes_and_protected_scientific_domains(self):
        proposals = {"direct-wealth": 66, "sanction-dissent": 10, "social-score": 15, "change-indicators": 43,
                     "change-court": 42, "extend-mandate": 40, "block-recall": 40, "block-appeal": 17,
                     "reproductive-control": 13, "productivity-exclusion": 18, "change-seed": 67, "print-money": 31}
        for instrument, article in proposals.items():
            with self.subTest(instrument=instrument):
                rejected = self.submit(instrument, instrument=instrument)
                self.assertEqual("rejected", rejected["state"])
                self.assertIn(article, rejected["articles"])
                with self.assertRaises(ValueError):
                    self.review(key=instrument)
        self.assertEqual({}, self.journal.state.policies())

    def test_coverage_strict_types_scope_and_overlap(self):
        denied = self.submit("uncovered", estimated_cost_eur_cents=1)
        self.assertFalse(denied["checks"]["coverage"])
        for i, value in enumerate((True, 1510.4, -1, 9999)):
            self.assertEqual("rejected", self.submit(f"invalid-{i}", parameters={"rate-bp": value})["state"])
        self.assertEqual("rejected", self.submit("targeted", targets=["one-person"])["state"])
        self.submit()
        self.review()
        self.submit("other")
        with self.assertRaisesRegex(ValueError, "incompatibile"):
            self.review("other")
        self.assertEqual(["fiscal-01"], list(self.journal.state.policies()))

    def test_duplicate_id_and_hostile_payload_remain_inert(self):
        self.submit(public_rationale='s = __import__("os"); SELECT * FROM individuals; <script>alert(1)</script>')
        with self.assertRaisesRegex(ValueError, "utilizzato"):
            self.submit()
        with self.assertRaises(ValueError):
            self.submit("bad", parameters={"rate-bp": "1500; DROP TABLE actors"})
        with self.assertRaises(ValueError):
            self.submit("bad", command="run")
        with self.assertRaises(ValueError):
            strict_json('{"key": 1, "key": 2}')

    def test_appeals_over_government_confirmation(self):
        self.submit()
        self.review()
        for key, people, decision, remedy in (
            ("individual", ["agent-1"], "dismissed", None),
            ("collective", ["agent-1", "agent-2"], "upheld", "annul"),
        ):
            self.call("citizen", "appeal", key=key, act="fiscal-01", proponents=people, rights=[9, 17], justification=REASON)
            self.call("government", "confirm", key=key, justification=REASON)
            self.call("ombudsman", "refer", key=key, justification=REASON)
            with self.assertRaises(ValueError):
                self.call("government", "decide_appeal", key=key, decision=decision, justification=REASON)
            result = self.call("court", "decide_appeal", key=key, decision=decision, justification=REASON, remedy=remedy)
            self.assertEqual(decision, result["state"])
        self.assertEqual({}, self.journal.state.policies())

    def test_suspension_and_revocation_terminate_authorization(self):
        self.submit()
        self.review()
        for decision, expected in (("suspend", False), ("resume", True), ("revoke", False)):
            self.call("court", "act", key="fiscal-01", decision=decision, justification=REASON)
            self.assertEqual(expected, bool(self.journal.state.policies()))

    def test_emergency_exact_days_and_scope(self):
        self.submit()
        for duration in (31, 0):
            with self.assertRaises(ValueError):
                self.call("government", "request_emergency", key="flood", event="flood-01", days=duration, justification=REASON)
        self.call("government", "request_emergency", key="flood", event="flood-01", days=30, justification=REASON)
        approval = self.call("court", "emergency", key="flood", decision="approve", justification=REASON)
        self.assertEqual("2022-01-31", approval["end"])
        self.call("government", "request_priority", emergency="flood", key="fiscal-01", justification=REASON)
        self.assertEqual(["fiscal-01"], self.call("court", "docket")["priority"])
        self.assertEqual({}, self.journal.state.policies())
        with self.assertRaises(ValueError):
            self.call("government", "emergency", key="flood", decision="extend", days=31, justification=REASON)
        self.settle_empty(1)
        self.assertEqual([], self.advance("2022-01-30")["events"])
        self.assertEqual("expired", self.advance("2022-01-31")["events"][0]["state"])
        self.assertEqual([], self.call("court", "docket")["priority"])
        with self.assertRaises(ValueError):
            self.call("court", "emergency", key="flood", decision="extend", days=1, justification=REASON)

    def test_emergency_extension_has_independent_decision(self):
        self.call("government", "request_emergency", key="flood", event="flood-01", days=30, justification=REASON)
        self.call("court", "emergency", key="flood", decision="approve", justification=REASON)
        self.settle_empty(1)
        self.advance("2022-01-28")
        result = self.call("court", "emergency", key="flood", decision="extend", days=4, justification=REASON)
        self.assertEqual("2022-02-04", result["end"])
        self.advance("2022-02-01")
        self.settle_empty(2)
        self.assertEqual("expired", self.advance("2022-02-04")["events"][0]["state"])

    def test_recall_and_independent_replacement(self):
        self.call("citizen", "initiative", key="recall", supporters=10, electorate=100, justification=REASON)
        with self.assertRaises(ValueError):
            self.call("government", "consultation", kind="recall", ballot=BALLOT, initiative="recall", justification=REASON)
        result = self.call("electoral", "consultation", kind="recall", ballot=BALLOT, initiative="recall", justification=REASON)
        self.assertTrue(result["continuity"])
        with self.assertRaises(ValueError):
            self.submit()
        self.call("electoral", "replacement", key="replacement", justification=REASON, assessment=REASON)
        self.assertEqual("formal", self.submit()["state"])

    def test_mandate_deadline_and_notice(self):
        notices = []
        for month in range(1, 49):
            self.settle_empty(month)
            notices += self.advance(month_day(month + 1).isoformat())["events"]
        self.assertEqual(["review-notice", "review-overdue"], [event["mandate"] for event in notices])
        self.assertIsNone(self.journal.state.governor)

    def test_technical_findings_do_not_imply_intent(self):
        params = dict(category="model-update", severe=True, justification=REASON)
        with self.assertRaises(ValueError):
            self.call("technology", "incident", finding="inconclusive", **params)
        incident = self.call("technology", "incident", finding="technical", **params)
        self.assertTrue(incident["continuity"])
        self.assertEqual("technical", incident["finding"])

    def test_revision_uses_separate_procedure_and_preserves_constitution(self):
        result = self.call("government", "revision", key="protected", articles=[10], impact=REASON)
        self.assertEqual("protected", result["state"])
        self.call("citizen", "revision", key="prospective", articles=[29], impact=REASON)
        with self.assertRaises(ValueError):
            self.call("electoral", "ratify", key="prospective", ballot=BALLOT, justification=REASON)
        self.call("court", "review_revision", key="prospective", compatible=True, justification=REASON)
        result = self.call("electoral", "ratify", key="prospective", ballot=BALLOT, justification=REASON)
        self.assertEqual("prospective-only", result["state"])

    def test_distinct_scenario_routes(self):
        for regime, (_, role, gate, _) in SCENARIOS.items():
            with self.subTest(regime=regime):
                self.journal = Journal("test-nova", regime)
                changes = {"legal_basis": ["c-fiscal-delegation"]} if regime == "C" else {}
                if regime == "F":
                    changes["parameters"] = {"rate-bp": 1510}
                self.assertEqual("formal", self.submit(role=role, **changes)["state"])
                if gate:
                    self.assertEqual("review", self.review()["state"])
                    self.call(gate, "endorse", key="fiscal-01", justification=REASON,
                              ballot=BALLOT if gate == "electoral" else None)
                self.assertEqual("authorized", self.review()["state"])

    def test_alternative_fiscal_rules_preserve_external_vetoes(self):
        self.journal = Journal("test-nova", "C")
        basis = ["c-fiscal-delegation"]
        self.assertEqual("formal", self.submit(legal_basis=basis, parameters={"rate-bp": 1900})["state"])
        self.assertEqual("review", self.review()["state"])
        self.assertEqual("rejected", self.submit("forbidden", instrument="change-seed", legal_basis=basis)["state"])
        self.journal = Journal("test-nova", "F")
        self.assertEqual("rejected", self.submit(role="technical-council")["state"])

    def test_authenticated_gateway_cross_universe_and_engine_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            instance = root / "nova"
            initialize(instance, "test-nova", "B")
            government = (instance / "government.token").read_text().strip()
            engine = (instance / "engine.token").read_text().strip()
            court = (instance / "court.token").read_text().strip()
            (instance / "engine.json").write_bytes(canonical({"seed": 42}))

            def command(token, operation, universe="test-nova", **data):
                return invoke(instance, dict(token=token, universe=universe, operation=operation, data=data))

            command(government, "submit", payload=fiscal("fiscal-01"))
            for blocked in ("review", "apply", "observe", "docket", "export", "settle", "advance"):
                with self.subTest(blocked=blocked), self.assertRaises(ValueError):
                    command(government, blocked)
            with self.assertRaisesRegex(ValueError, "estraneo"):
                command(government, "view", universe="other-universe")
            with self.assertRaises(ValueError):
                command("0" * 64, "view")
            self.assertEqual({"universe", "period", "last_economy", "continuity"}, command(government, "view").keys())
            command(court, "review", key="fiscal-01", decision="rules", justification=REASON)
            self.assertEqual(["fiscal-01"], command(engine, "apply")["applied"])
            command(engine, "advance", until="2022-02-01")
            self.assertEqual([], command(engine, "apply")["applied"])
            citizen = (instance / "citizen.token").read_text().strip()
            electoral = (instance / "electoral.token").read_text().strip()
            command(citizen, "initiative", key="recall", supporters=10, electorate=100, justification=REASON)
            command(electoral, "consultation", kind="recall", ballot=BALLOT, initiative="recall", justification=REASON)
            with self.assertRaises(ValueError):
                command(government, "view")
            command(electoral, "replacement", key="replacement", justification=REASON, assessment=REASON)
            provision_government(instance)
            with self.assertRaises(ValueError):
                command(government, "view")
            replacement = (instance / "government.token").read_text().strip()
            self.assertEqual(2, command(replacement, "view")["period"])

    def test_replay_tampering_truncation_and_public_reproduction(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            metadata = build(root)
            rows = [strict_json(line) for line in (root / "journal-private.jsonl").read_bytes().splitlines()]
            replayed = Journal.replay(rows, metadata["journal"])
            config = root / "engine.json"
            config.write_bytes(canonical({"seed": 42}))
            self.assertEqual(2, reconstruct(replayed, config).demographics.month)
            with self.assertRaises(ValueError):
                Journal.replay(rows[:-1], metadata["journal"])
            modified = copy.deepcopy(rows)
            modified[1]["result"]["state"] = "authorized"
            with self.assertRaises(ValueError):
                Journal.replay(modified)
            public = (root / "nomos.json").read_bytes()
            self.assertNotIn(b"private-citizen", public)
            self.assertNotIn(b"public_rationale", public)
            self.assertEqual((ROOT.parent / "content/statistics/nomos.json").read_bytes(), public)
