import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from hypothesis import given, settings, strategies as st

from demos.config import load_config
from demos.engine import generate, monthly_probability, step
from demos.events import replay, run
from demos.indicators import compare, export
from demos.randomness import uniform
from demos.snapshot import digest, restore, save
from demos.validation import validate


class DemosTest(unittest.TestCase):
    def test_standard_export_matches_the_committed_aggregate(self):
        state = generate(load_config("standard", "eu27"), 20261122)
        data = json.loads((Path(__file__).resolve().parents[2] / "content/statistics/demos.json").read_text())
        self.assertEqual(100_000, len(state.people))
        self.assertEqual(5000, len(state.firms))
        self.assertEqual(data["snapshot_sha256"], digest(state))
        manifest = {key: data[key] for key in ("snapshot_sha256", "config_sha256", "generator", "generated_at")}
        self.assertEqual(data, export(state, manifest))
        self.assertEqual({"2022", "2023"}, set(compare(state)["comparisons"]))

    def test_random_domains_are_independent_of_iteration_and_draw_count(self):
        full = uniform(3, "birth", 1, [1, 2, 3])
        uniform(3, "mortality", 1, range(20))
        np.testing.assert_array_equal(full[[2, 0]], uniform(3, "birth", 1, [3, 1]))
        self.assertFalse(np.array_equal(full, uniform(3, "birth", 2, [1, 2, 3])))

    @given(st.integers(min_value=0, max_value=2**32-2), st.integers(min_value=1, max_value=18))
    @settings(max_examples=18, deadline=None)
    def test_determinism_and_demographic_properties(self, seed, months):
        config = load_config("smoke", "hypothetical")
        state = generate(config, seed)
        self.assertEqual(digest(state), digest(generate(config, seed)))
        self.assertNotEqual(digest(state), digest(generate(config, seed + 1)))
        for _ in range(months):
            event = step(state)
            self.assertEqual(event["final"], event["initial"] + len(event["births"]) - len(event["deaths"])
                             + len(event["immigrants"]) - len(event["emigrants"]))
            validate(state)

    @given(st.floats(min_value=0, max_value=1, allow_nan=False))
    def test_monthly_survival_reconstructs_annual_probability(self, annual):
        self.assertAlmostEqual(annual, 1 - (1 - monthly_probability(annual))**12, places=12)

    def test_checkpoint_and_replay_to_600_months(self):
        state = generate(load_config("smoke", "eu27"), 8)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            save(state, root / "initial")
            run(state, 300, root / "first.log")
            save(state, root / "middle")
            restored, _ = restore(root / "middle")
            run(restored, 300, root / "second.log")
            rerun, _ = restore(root / "initial")
            replay(rerun, root / "first.log")
            replay(rerun, root / "second.log")
            self.assertEqual(600, rerun.month)
            self.assertEqual(digest(restored), digest(rerun))
            with self.assertRaises(ValueError):
                step(rerun)

    def test_universes_own_their_mutable_state(self):
        baseline = generate(load_config("smoke", "eu27"), 5)
        universes = [baseline.clone(label) for label in "ABCDEF"]
        initial = digest(baseline)
        for state in universes:
            self.assertEqual(initial, digest(state))
            self.assertFalse(np.shares_memory(state.people, baseline.people))
        step(universes[0])
        universes[0].config["macro_targets"]["annual_gdp_eur"] = 0
        self.assertTrue(all(digest(state) == initial for state in universes[1:]))
        self.assertEqual(initial, digest(baseline))

    def test_corrupt_genealogy_and_bad_checkpoint_are_rejected(self):
        state = generate(load_config("smoke", "eu27"), 4)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            metadata = save(state, root)
            metadata["snapshot_sha256"] = "0"*64
            (root / "manifest.json").write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError, "checksum"):
                restore(root)
        state.people["parent"][0] = 0
        with self.assertRaisesRegex(ValueError, "genealogy"):
            validate(state)
