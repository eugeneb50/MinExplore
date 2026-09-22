"""Uncertainty and coverage layer (Tier 1/2 input).

How little is actually known about each target — kept VISIBLE and SEPARATE
from prospectivity. A poorly studied area is not automatically prospective.
Stdlib only.
"""
from __future__ import annotations

from src.scores import EVIDENCE

TAG_PENALTY = {
    "observed": 0,
    "derived": 1,
    "inferred": 2,
    "not-yet-assessed": 3,
    "requires-field-validation": 2,
}


def coverage(target_id):
    """Return uncertainty/coverage facts for a target.

    uncertainty_index: mean tag penalty scaled to 0-10 (higher = less known).
    low_confidence_factors: factors scored Low confidence (noise drivers).
    unassessed: factors tagged not-yet-assessed (coverage gaps).
    """
    ev = EVIDENCE[target_id]
    pens = [TAG_PENALTY[m["tag"]] for m in ev.values()]
    return {
        "uncertainty_index": round(10 * sum(pens) / (3 * len(pens)), 1),
        "low_confidence_factors": sorted(
            f for f, m in ev.items() if m["confidence"] == "Low"),
        "unassessed": sorted(
            f for f, m in ev.items() if m["tag"] == "not-yet-assessed"),
        "n_factors": len(pens),
    }


def all_coverage():
    return {t: coverage(t) for t in EVIDENCE}
