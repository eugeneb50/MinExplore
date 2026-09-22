"""Tests for uncertainty, frontier-priority, and source registry (stdlib only)."""
import os
import unittest

from src.frontier import all_frontier, frontier_priority, information_gain
from src.registry import REGISTRY_PATH, commercial_clean, fingerprint, load, validate
from src.uncertainty import all_coverage, coverage


class TestUncertainty(unittest.TestCase):
    def test_index_in_range(self):
        for tid, cov in all_coverage().items():
            self.assertGreaterEqual(cov["uncertainty_index"], 0)
            self.assertLessEqual(cov["uncertainty_index"], 10)

    def test_unassessed_subset_of_low(self):
        for tid, cov in all_coverage().items():
            self.assertTrue(set(cov["unassessed"]) <= set(cov["low_confidence_factors"]), tid)

    def test_deterministic(self):
        self.assertEqual(all_coverage(), all_coverage())


class TestFrontier(unittest.TestCase):
    def test_formula(self):
        fp = frontier_priority("T2")
        p, g, f = fp["prospectivity"], fp["information_gain"], fp["feasibility"]
        self.assertAlmostEqual(fp["frontier_priority"], round((p / 10) * g * (f / 10) * 10, 1))

    def test_penalties_subtract(self):
        base = frontier_priority("T2")["frontier_priority"]
        pen = frontier_priority("T2", constraint_penalties=[5.0])["frontier_priority"]
        self.assertAlmostEqual(base - pen, 5.0)

    def test_disclaimer_present(self):
        self.assertIn("NOT a probability", all_frontier()["T1"]["disclaimer"])

    def test_info_gain_in_range(self):
        for t in ("T1", "T2", "T3"):
            self.assertGreaterEqual(information_gain(t), 0)
            self.assertLessEqual(information_gain(t), 10)


class TestRegistry(unittest.TestCase):
    def test_seed_registry_valid(self):
        doc = load(REGISTRY_PATH)
        self.assertEqual(validate(doc["sources"]), [])

    def test_unique_ids(self):
        doc = load(REGISTRY_PATH)
        ids = [r["source_id"] for r in doc["sources"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_nc_sources_excluded_from_commercial(self):
        doc = load(REGISTRY_PATH)
        clean = {r["source_id"] for r in commercial_clean(doc["sources"])}
        self.assertNotIn("eox-s2cloudless-2020", clean)
        self.assertNotIn("esri-world-imagery", clean)
        self.assertIn("sgm-h11-b85", clean)

    def test_validator_catches_duplicates(self):
        doc = load(REGISTRY_PATH)
        recs = doc["sources"] + [dict(doc["sources"][0])]
        self.assertTrue(any("duplicate" in e for e in validate(recs)))

    def test_fingerprint_stable(self):
        doc = load(REGISTRY_PATH)
        self.assertEqual(fingerprint(doc["sources"]), fingerprint(doc["sources"]))

    def test_registry_file_exists(self):
        self.assertTrue(os.path.exists(REGISTRY_PATH))


if __name__ == "__main__":
    unittest.main()
