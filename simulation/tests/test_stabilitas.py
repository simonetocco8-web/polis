import gzip
import json
from pathlib import Path
import unittest

import numpy as np

from demos.config import load_config, sha
from demos.engine import generate
from oikonomia.engine import step
from oikonomia.ledger import Journal
from oikonomia.markets import reprice
from oikonomia.snapshot import digest
from oikonomia.state import attach, reconcile
from stabilitas.diagnostics import OPENING, FINAL, run
from stabilitas.policy import Policy, symmetric_price

ROOT = Path(__file__).resolve().parents[1]


class StabilitasTest(unittest.TestCase):
    def baseline(self):
        return attach(generate(load_config("smoke", "eu27"), 42))

    def test_legacy_log_and_hash_are_preserved(self):
        log = gzip.decompress((ROOT / "archive/oikonomia-v0.4.0-events.jsonl.gz").read_bytes())
        self.assertEqual("135af7b434a0472b94f92414aaa388a4bdd70f8a54814541d85c18d0057e00a5", sha(log))
        self.assertEqual(OPENING, json.loads(log.splitlines()[0])["initial"])
        self.assertEqual(FINAL, json.loads(log.splitlines()[-1])["final"])

    def test_no_silent_wraparound_or_rounding_asymmetry(self):
        with self.assertRaisesRegex(ValueError, "amount"):
            Journal(1, "0"*64).record("oversized", [2**62]*4, [0])
        cfg = self.baseline().config
        self.assertEqual((5999, 6000), (reprice(6000, 10001, 10000, cfg), reprice(6000, 10000, 10001, cfg)))
        self.assertEqual((6000, 6000), (symmetric_price(6000, 10001, 10000, cfg), symmetric_price(6000, 10000, 10001, cfg)))

    def test_instrumented_control_has_identical_state_and_journal(self):
        left, right = self.baseline(), self.baseline()
        policy = Policy()
        for _ in range(12):
            self.assertEqual(step(left), step(right, policy=policy))
        self.assertEqual(digest(left), digest(right))
        self.assertEqual(12, len(policy.rows))

    def test_labor_opening_capacity_liquidity_and_autonomous_continuity(self):
        control = run("smoke", 42, "control", 1)["first_month"]
        continuity = run("smoke", 42, "A", 1)["first_month"]
        self.assertEqual(0, control["hires_from_search"])
        self.assertGreater(control["autonomous_to_unemployment"], continuity["autonomous_to_unemployment"])
        state = self.baseline()
        state.accounts["firm_deposit"][:] = 0
        from oikonomia.labor import plan
        plan(state, False)
        self.assertEqual(0, int((state.accounts["jobs"] == 2).sum()))

    def test_standard_first_month_counterfactual_identifies_the_opening_shock(self):
        control = run("standard", 20261122, "control", 1)
        continuity = run("standard", 20261122, "A", 1)
        self.assertEqual(4677, control["first_month"]["autonomous_to_unemployment"])
        self.assertEqual(18.010511, control["rows"][0]["unemployment_percent"])
        self.assertEqual(8.664548, continuity["rows"][0]["unemployment_percent"])
        self.assertEqual(control["opening_sha256"], continuity["opening_sha256"])

    def test_territorial_matching_capacity_and_wages(self):
        from oikonomia.labor import plan
        state = self.baseline()
        step(state)
        d, a = state.demographics, state.accounts
        previous = a["jobs"].copy()
        wages = plan(state, False)
        hires = np.flatnonzero((previous != 2) & (a["jobs"] == 2))
        self.assertGreater(len(hires), 0)
        np.testing.assert_array_equal(d.firms["territory"][a["employer"][hires]],
                                      d.households["territory"][d.people["household"][hires]])
        np.testing.assert_array_equal(wages, np.maximum(state.config["employee_wage_floor"],
                                                        (d.people["income_work"].astype(np.int64)*100+6)//12))
        reconcile(state)

    def test_reference_source_hashes(self):
        folder = ROOT / "stabilitas-sources"
        manifest = json.loads((folder / "manifest.json").read_bytes())
        self.assertEqual(8, len(manifest))
        for record in manifest.values():
            if record["status"] == "acquisito":
                self.assertEqual(record["sha256"], sha((folder / record["file"]).read_bytes()))
            else:
                self.assertTrue(record["problem"])

    def test_entry_uses_existing_deposits_capital_and_market_slots(self):
        state = self.baseline()
        a = state.accounts
        donors = np.flatnonzero(state.demographics.firms["territory"] == state.demographics.firms["territory"][0])
        self.assertGreater(len(donors), 1)
        vacant = donors[1]
        staff = a["employer"] == vacant
        a["jobs"][staff], a["employer"][staff] = 1, -1
        a["active"][vacant], a["inventory"][vacant], a["capital"][vacant] = 0, 0, 0
        # Transfer the initial slot deposit to a funded local donor.
        a["firm_deposit"][donors[0]] += a["firm_deposit"][vacant]
        a["firm_deposit"][vacant] = 0
        a["jobs"][(state.demographics.households["territory"][state.demographics.people["household"]] ==
                    state.demographics.firms["territory"][vacant]) & (a["jobs"] == 3)] = 1
        state.demographics.month = 11
        deposits, capital = int(a["firm_deposit"].sum()), int(a["capital"].sum())
        self.assertEqual(1, Policy("B").enter(state, Journal(12, state.journal)))
        self.assertEqual((deposits, capital), (int(a["firm_deposit"].sum()), int(a["capital"].sum())))
        self.assertEqual(1, a["active"][vacant])
        reconcile(state)

    def test_bank_distribution_reconciles_without_loan_and_replays(self):
        state = self.baseline()
        a = state.accounts
        loans, deposits, equity = int(a["bank_loans"][0]), int(a["house_deposit"].sum()), int(a["bank_equity"][0])
        paid = Policy("C").distribute(state, Journal(1, state.journal), 100)
        self.assertEqual(50, paid)
        self.assertEqual((loans, deposits + paid, equity - paid),
                         (int(a["bank_loans"][0]), int(a["house_deposit"].sum()), int(a["bank_equity"][0])))
        reconcile(state)
        result = run("smoke", 42, "B+C+E", 12)
        replayed = run("smoke", 42, "B+C+E", 12)
        self.assertEqual(result["final_sha256"], replayed["final_sha256"])
        self.assertEqual(result["rows"], replayed["rows"])

    def test_zero_input_stocks_are_absorbing_even_under_a_larger_reserve(self):
        state = self.baseline()
        state.accounts["inventory"][:] = 0
        policy = Policy("E")
        for _ in range(3):
            data, _ = step(state, policy=policy)
            self.assertEqual(0, data["units_produced"])
            self.assertEqual(0, data["inventory_units"])
