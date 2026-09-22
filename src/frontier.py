"""Frontier-priority model (predictive skill support).

Frontier priority = prospectivity x expected information gain
                    x field feasibility - constraint penalties

All terms are relative evidence scores on 0-10-ish scales, NOT probabilities
of mineralization. Stdlib only.
"""
from __future__ import annotations

from src.scores import feasibility, prospectivity
from src.uncertainty import coverage


def information_gain(target_id):
    """Expected information gain 0-10: how much a realistic field action could
    clarify. Proxy: normalized count of Low-confidence + unassessed factors
    (more open questions = more to gain), scaled so the max across committed
    targets maps near 10. Deterministic."""
    cov = coverage(target_id)
    n = len(cov["low_confidence_factors"]) + len(cov["unassessed"])
    return round(min(10.0, n * 1.5), 1)


def frontier_priority(target_id, constraint_penalties=None):
    """Return the frontier-priority breakdown. Penalties: list of 0-10
    deductions (e.g. ANP overlap, active title); default none assessed."""
    penalties = constraint_penalties or []
    p = prospectivity(target_id)
    g = information_gain(target_id)
    f = feasibility(target_id)
    score = round((p / 10) * g * (f / 10) * 10 - sum(penalties), 1)
    return {"prospectivity": p, "information_gain": g, "feasibility": f,
            "constraint_penalties": list(penalties),
            "frontier_priority": score,
            "disclaimer": "Relative evidence score, NOT a probability of mineralization."}


def all_frontier():
    return {t: frontier_priority(t) for t in ("T1", "T2", "T3")}
