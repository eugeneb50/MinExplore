"""Deterministic scoring tests: v2 legacy (frozen) + v3 split model."""
import unittest

from src.scores import (COMMITTED_SCORES, COMMITTED_V3, EVIDENCE,
                        FEASIBILITY_WEIGHTS, PROSPECTIVITY_WEIGHTS, WEIGHTS,
                        all_scores, all_split, feasibility, prospectivity,
                        score_target)


class TestScoresV2Legacy(unittest.TestCase):
    def test_committed_values_reproduce(self):
        for tid, expected in COMMITTED_SCORES.items():
            self.assertEqual(score_target(tid), expected, tid)

    def test_deterministic(self):
        self.assertEqual(all_scores(), all_scores())

    def test_scores_in_range(self):
        for tid in EVIDENCE:
            self.assertGreaterEqual(score_target(tid), 0)
            self.assertLessEqual(score_target(tid), 10)


class TestScoresV3Split(unittest.TestCase):
    def test_committed_split_reproduces(self):
        for tid, expected in COMMITTED_V3.items():
            got = all_split()[tid]
            self.assertEqual(got["prospectivity"], expected["prospectivity"], tid)
            self.assertEqual(got["feasibility"], expected["feasibility"], tid)

    def test_split_covers_all_factors_exactly_once(self):
        for tid, ev in EVIDENCE.items():
            keys = set(ev)
            self.assertEqual(set(PROSPECTIVITY_WEIGHTS) | set(FEASIBILITY_WEIGHTS), keys, tid)
            self.assertEqual(set(PROSPECTIVITY_WEIGHTS) & set(FEASIBILITY_WEIGHTS), set())

    def test_known_workings_downweighted(self):
        self.assertLess(PROSPECTIVITY_WEIGHTS["known_workings"],
                        WEIGHTS["known_workings"])

    def test_split_in_range(self):
        for tid in EVIDENCE:
            for v in (prospectivity(tid), feasibility(tid)):
                self.assertGreaterEqual(v, 0)
                self.assertLessEqual(v, 10)

    def test_deterministic(self):
        self.assertEqual(all_split(), all_split())


if __name__ == "__main__":
    unittest.main()
