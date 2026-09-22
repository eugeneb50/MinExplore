"""Published desk-screening scoring model.

v3.0.0: scores are SPLIT into geological prospectivity vs feasibility, shown
side by side and never blended. A geologically interesting site can still be
unsuitable or inaccessible.

- prospectivity(tid): geology, workings (deliberately downweighted — distance
  to a known mine must not dominate or the model just rediscovers districts),
  spectral, structure, exposure.
- feasibility(tid): access, water/regulatory, land_constraints (SIAM / RAN /
  CONANP / CONAGUA — currently not-yet-assessed placeholders; see docs).

Ranks are relative evidence scores, NOT probabilities of mineralization.
Deterministic: same evidence in, same score out. Stdlib only (CI-safe).

v2 legacy: score_target() / COMMITTED_SCORES preserve the old single blended
mean (T1 5.4 / T2 6.3 / T3 5.5) so history stays reproducible and tested.
"""
from __future__ import annotations

PIPELINE_VERSION = "3.0.0"

# --- v2 legacy (blended single mean; frozen) ---
WEIGHTS = {
    "geological_setting": 20,
    "known_workings": 15,
    "spectral_indication": 15,
    "structural_context": 15,
    "bedrock_exposure": 10,
    "access": 10,
    "water_regulatory": 15,
}

# --- v3 split ---
PROSPECTIVITY_WEIGHTS = {
    "geological_setting": 30,
    "known_workings": 10,  # downweighted: must not dominate (frontier rule)
    "spectral_indication": 20,
    "structural_context": 25,
    "bedrock_exposure": 15,
}
FEASIBILITY_WEIGHTS = {
    "access": 35,
    "water_regulatory": 35,
    "land_constraints": 30,
}

FACTOR_LABELS = {
    "geological_setting": "Geological setting",
    "known_workings": "Known workings",
    "spectral_indication": "Spectral indication",
    "structural_context": "Structural context",
    "bedrock_exposure": "Bedrock exposure",
    "access": "Access",
    "water_regulatory": "Water / regulatory",
    "land_constraints": "Land constraints (titles/ejidos/ANP/aquifers)",
}

# Evidence tags: observed | derived | inferred | not-yet-assessed | requires-field-validation
EVIDENCE = {
    "T1": {
        "geological_setting": {"score": 6, "confidence": "Medium", "tag": "observed",
            "note": "SGM Alisitos andesite/breccia + N-S relay drainage (H11-B85)."},
        "known_workings": {"score": 4, "confidence": "Medium", "tag": "observed",
            "note": "13-21 km S of documented workings; no workings on site."},
        "spectral_indication": {"score": 5, "confidence": "Low", "tag": "derived",
            "note": "Unvalidated RGB visual-screening heuristic (B/R 0.55-0.63 on pale patches). Requires field validation."},
        "structural_context": {"score": 5, "confidence": "Low", "tag": "inferred",
            "note": "N-S relay drainage inferred as structure; requires field validation."},
        "bedrock_exposure": {"score": 6, "confidence": "Medium", "tag": "derived",
            "note": "86% bare regolith from HSV surface classification + gentle slopes."},
        "access": {"score": 9, "confidence": "Medium", "tag": "derived",
            "note": "Tracks within a few km; approximate road distance."},
        "water_regulatory": {"score": 4, "confidence": "Low", "tag": "not-yet-assessed",
            "note": "Preliminary desk screen only; arid corridor, no water rights assessed."},
        "land_constraints": {"score": 5, "confidence": "Low", "tag": "not-yet-assessed",
            "note": "SIAM titles / RAN ejidos / CONANP zoning / CONAGUA aquifers not yet screened."},
    },
    "T2": {
        "geological_setting": {"score": 8, "confidence": "Medium", "tag": "observed",
            "note": "SGM Alisitos andesite + granodiorite contact zone (H11-B85)."},
        "known_workings": {"score": 7, "confidence": "Medium", "tag": "observed",
            "note": "On eastern projection of documented Cu-Fe belt; turquoise-mining toponym at site."},
        "spectral_indication": {"score": 6, "confidence": "Low", "tag": "derived",
            "note": "Unvalidated RGB visual-screening heuristic on km-scale pale mass ~1 km W. Requires field validation."},
        "structural_context": {"score": 7, "confidence": "Low", "tag": "inferred",
            "note": "Straight NE-SW lineament ~1 km E (road vs fault scarp - field check). Requires field validation."},
        "bedrock_exposure": {"score": 8, "confidence": "Medium", "tag": "derived",
            "note": "Pale mass + hillslopes; good outcrop potential per terrain + visual classification."},
        "access": {"score": 6, "confidence": "Medium", "tag": "derived",
            "note": "MEX 2 ~2 km away; approximate road distance."},
        "water_regulatory": {"score": 2, "confidence": "Low", "tag": "not-yet-assessed",
            "note": "Preliminary desk screen only; water availability is the principal regulatory risk."},
        "land_constraints": {"score": 5, "confidence": "Low", "tag": "not-yet-assessed",
            "note": "SIAM titles / RAN ejidos / CONANP zoning / CONAGUA aquifers not yet screened."},
    },
    "T3": {
        "geological_setting": {"score": 6, "confidence": "Medium", "tag": "observed",
            "note": "SGM ridge between T1 and T2; Rosario Fm + intrusives (H11-B85)."},
        "known_workings": {"score": 4, "confidence": "Medium", "tag": "observed",
            "note": "No documented workings on site; corridor high ground."},
        "spectral_indication": {"score": 4, "confidence": "Low", "tag": "derived",
            "note": "Unvalidated RGB visual-screening heuristic; spectrally quiet. Requires field validation."},
        "structural_context": {"score": 6, "confidence": "Low", "tag": "inferred",
            "note": "Ridge position on T1-T2 corridor trend; requires field validation."},
        "bedrock_exposure": {"score": 8, "confidence": "Medium", "tag": "derived",
            "note": "Steepest terrain (30% of area >15 deg) -> best bedrock exposure."},
        "access": {"score": 8, "confidence": "Medium", "tag": "derived",
            "note": "MEX 2 cut-banks ~2 km NE; approximate road distance."},
        "water_regulatory": {"score": 4, "confidence": "Low", "tag": "not-yet-assessed",
            "note": "Preliminary desk screen only; arid corridor, no water rights assessed."},
        "land_constraints": {"score": 5, "confidence": "Low", "tag": "not-yet-assessed",
            "note": "SIAM titles / RAN ejidos / CONANP zoning / CONAGUA aquifers not yet screened."},
    },
}

COMMITTED_SCORES = {"T1": 5.4, "T2": 6.3, "T3": 5.5}  # v2 blended legacy (frozen)

# v3 split ranks (prospectivity, feasibility). Computed via prospectivity() /
# feasibility() below, then frozen here; asserted by tests/test_scores.py:
COMMITTED_V3 = {
    "T1": {"prospectivity": 5.3, "feasibility": 6.0},
    "T2": {"prospectivity": 7.2, "feasibility": 4.3},
    "T3": {"prospectivity": 5.7, "feasibility": 5.7},
}


def _weighted(ev, weights):
    total = sum(weights[f] for f in weights)
    return round(sum(weights[f] * ev[f]["score"] for f in weights) / total, 1)


def score_target(target_id):
    """v2 blended mean (legacy, frozen)."""
    ev = EVIDENCE[target_id]
    total = sum(WEIGHTS[f] for f in WEIGHTS)
    return round(sum(WEIGHTS[f] * ev[f]["score"] for f in WEIGHTS) / total, 1)


def prospectivity(target_id):
    """v3 geological prospectivity (0-10). Never blended with feasibility."""
    return _weighted(EVIDENCE[target_id], PROSPECTIVITY_WEIGHTS)


def feasibility(target_id):
    """v3 access/legal/environmental feasibility (0-10). Shown separately."""
    return _weighted(EVIDENCE[target_id], FEASIBILITY_WEIGHTS)


def all_scores():
    return {t: score_target(t) for t in EVIDENCE}


def all_split():
    return {t: {"prospectivity": prospectivity(t), "feasibility": feasibility(t)}
            for t in EVIDENCE}


def weights_table():
    total = sum(WEIGHTS.values())
    return [(f, WEIGHTS[f], round(100 * WEIGHTS[f] / total, 1)) for f in WEIGHTS]
