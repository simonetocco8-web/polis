import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from hypothesis import given, strategies as st

from demos.config import load_config, sha
from demos.engine import generate
from demos.snapshot import digest as demos_digest
from oikonomia.banking import lend, service, write_off
from oikonomia.cli import execute, replay
from oikonomia.engine import step
from oikonomia.ledger import Journal, apportion
from oikonomia.markets import clear, reprice
from oikonomia.national import accounts, inequality
from oikonomia.snapshot import digest, restore, save
from oikonomia.state import attach, reconcile


class OikonomiaTest(unittest.TestCase):
    def small(self, variant="baseline"):
        return attach(generate(load_config("smoke", "eu27"), 42), variant)

    def test_ledger_duplicate_and_overdraft_do_not_change_account(self):
        ledger = Journal(1, "0" * 64)
        source, target = np.array([100]), np.array([0])
        ledger.transfer("test", source, target, np.array([30]), np.array([30]), "source", "target")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            ledger.transfer("test", source, target, np.array([30]), np.array([30]), "source", "target")
        with self.assertRaisesRegex(ValueError, "Insufficient"):
            ledger.transfer("other", source, target, np.array([100]), np.array([100]), "source", "target")
        with self.assertRaisesRegex(ValueError, "Unbalanced"):
            ledger.record("unbalanced", [10], [9])
        self.assertEqual((70, 30), (source[0], target[0]))

    @given(st.lists(st.integers(0, 10**11), min_size=1, max_size=10), st.integers(0, 100))
    def test_allocation_is_exact_and_overflow_safe(self, weights, percent):
        total = sum(weights) * percent // 100
        payout = apportion(total, weights)
        self.assertEqual(total, int(payout.sum()))
        self.assertTrue(np.all(payout <= weights))

    def test_national_accounts_and_closed_market_hand_calculation(self):
        self.assertEqual((150, 150, 150, 200, 20), accounts(10, 20, 6, 2, 2, 1, 1, 0, 100, 10, 120))
        with self.assertRaisesRegex(ValueError, "GDP"):
            accounts(10, 20, 6, 2, 3, 1, 1, 0, 100, 10, 120)
        firms, households, inventory = np.array([0, 0]), np.array([30, 50]), np.array([1, 2])
        sold = clear(Journal(1, "0" * 64), "goods", inventory, np.array([9, 8]), households, firms, 10, "households")
        self.assertEqual(3, sold[3])
        self.assertEqual(0, inventory.sum())
        self.assertEqual(80, households.sum() + firms.sum())
        self.assertIsNone(inequality(np.array([0, 0, 10]))[2])

    def test_bank_deposits_credit_losses_and_halt_reconcile(self):
        state = self.small()
        a = state.accounts
        journal = Journal(1, state.journal)
        request = np.zeros_like(a["firm_debt"])
        request[0] = 20000
        opening = a["firm_deposit"][0]
        lend(state, journal, "firm", request, 20000)
        self.assertEqual(opening + 20000, a["firm_deposit"][0])
        self.assertEqual(20000, a["bank_loans"][0])
        reconcile(state)
        interest, missed = service(state, journal, "firm")
        self.assertEqual(100, interest)
        self.assertFalse(missed[0])
        self.assertEqual(19166, write_off(state, journal, request > 0))
        reconcile(state)
        lend(state, Journal(2, journal.anchor), "firm", request, 20000, halted=True)
        self.assertEqual(0, a["bank_loans"][0])

    def test_insolvent_firm_is_closed_and_bank_with_nonpositive_equity_halts(self):
        state = self.small()
        a = state.accounts
        state.config["opening_reserves"] -= int(a["bank_equity"][0]) - 1
        a["bank_equity"][0] = 1
        state.config["loan_rate_monthly_bp"] = 0
        request = np.zeros_like(a["firm_debt"])
        request[0] = 50000
        journal = Journal(0, state.journal)
        lend(state, journal, "firm", request, 50000)
        payout = np.zeros_like(request)
        payout[0] = a["firm_deposit"][0]
        receipt = np.zeros_like(a["house_deposit"])
        receipt[0] = payout[0]
        journal.transfer("fixture-payment", a["firm_deposit"], a["house_deposit"], payout, receipt, "firm", "house")
        state.journal = journal.anchor
        a["arrears"][0] = 2
        a["inventory"][0] = 0
        staff = a["employer"] == 0
        a["jobs"][staff], a["employer"][staff] = 1, -1
        row, _ = step(state)
        self.assertEqual(0, a["active"][0])
        self.assertGreaterEqual(row["bank_credit_losses"], 50000)
        self.assertTrue(row["bank_credit_halted"])
        reconcile(state)

    def test_migration_checkpoint_replay_and_isolation(self):
        demos = generate(load_config("smoke", "eu27"), 42)
        original = demos_digest(demos)
        state = attach(demos)
        copy = state.clone("B")
        self.assertEqual(digest(copy), digest(state))
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            initial = root / "initial"
            initial.mkdir()
            save(state, initial)
            execute(state, 12, root / "run", detail=True)
            verified = restore(initial)
            replay(verified, root / "run/events.jsonl")
            self.assertEqual(digest(state), digest(verified))
            self.assertEqual(digest(state), digest(restore(root / "run")))
            self.assertNotEqual(digest(copy), digest(state))
            self.assertNotEqual(0, (root / "run/journal.jsonl.gz").stat().st_size)
        self.assertEqual(original, demos_digest(demos))

    def test_stresses_and_recession_have_a_distinct_path(self):
        totals = []
        for variant in ("baseline", "recession", "production-shock", "credit-crisis"):
            state = self.small(variant)
            outcome = []
            for _ in range(12):
                row, _ = step(state)
                outcome.append(row["gdp"])
                self.assertGreaterEqual(row["inventory_units"], 0)
                self.assertEqual(row["gdp"], row["gdp_expenditure"])
                if variant == "credit-crisis" and 4 <= row["month"] <= 9:
                    self.assertTrue(row["bank_credit_halted"])
            totals.append(outcome)
        self.assertEqual(4, len({tuple(series) for series in totals}))
        config = self.small().config
        self.assertEqual(config["price_max"], reprice(config["price_max"], 0, 1000, config))

    def test_published_standard_prefix_matches_a_fresh_run(self):
        root = Path(__file__).resolve().parents[2]
        file = root / "content/statistics/oikonomia.json"
        published = json.loads(file.read_bytes())
        self.assertEqual(sha(file.read_bytes()), file.with_suffix(".sha256").read_text().strip())
        state = attach(generate(load_config("standard", "eu27"), 20261122))
        self.assertEqual(digest(state), published["initial_sha256"])
        with tempfile.TemporaryDirectory() as folder:
            rebuilt = execute(state, 3, Path(folder) / "run")
        self.assertEqual(published["rows"][:3], rebuilt["rows"])
