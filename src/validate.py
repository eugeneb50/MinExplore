"""Validation for pin/mine CSV + GeoJSON records (Workstream 7). Stdlib only."""
from __future__ import annotations

import csv
import json
import sys

REQUIRED_COLUMNS = [
    "record_id", "target_id", "latitude", "longitude", "crs", "feature_type",
    "source", "source_page", "source_date", "coordinate_accuracy_m",
    "derivation_method", "confidence", "field_action", "license",
    "created_at", "pipeline_version",
]

KNOWN_FEATURE_TYPES = {"target", "pale", "struct", "sed", "out", "mine"}
KNOWN_CONFIDENCE = {"High", "Medium", "Low"}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def find_duplicate_locations(records):
    """Warning-level check: exact duplicate coordinates under different IDs.

    Co-location can be legitimate (detail-sheet re-plot of the same pin;
    adjacent SGM workings at one rancheria), so these are warnings, not errors.
    """
    warnings = []
    seen_coords = {}
    for i, r in enumerate(records):
        lat, lon = _num(r.get("latitude")), _num(r.get("longitude"))
        rid = r.get("record_id", "?")
        if lat is None or lon is None:
            continue
        key = (round(lat, 6), round(lon, 6))
        if key in seen_coords and seen_coords[key] != rid:
            warnings.append(
                f"row {i + 1} ({rid}): shares location {key} with '{seen_coords[key]}'")
        else:
            seen_coords.setdefault(key, rid)
    return warnings


def validate_records(records, check_scores=True):
    """Return a list of error strings (empty = valid)."""
    errors = []
    seen_ids = {}
    for i, r in enumerate(records):
        line = f"row {i + 1} ({r.get('record_id', '?')})"
        for col in REQUIRED_COLUMNS:
            if col not in r or r[col] in (None, ""):
                errors.append(f"{line}: missing required column '{col}'")
        rid = r.get("record_id", "")
        if rid:
            if rid in seen_ids:
                errors.append(f"{line}: duplicate record_id '{rid}' (first at row {seen_ids[rid]})")
            else:
                seen_ids[rid] = i + 1
        lat, lon = _num(r.get("latitude")), _num(r.get("longitude"))
        if lat is None or not (-90 <= lat <= 90):
            errors.append(f"{line}: invalid latitude '{r.get('latitude')}'")
        if lon is None or not (-180 <= lon <= 180):
            errors.append(f"{line}: invalid longitude '{r.get('longitude')}'")
        if r.get("crs") and r["crs"] != "EPSG:4326":
            errors.append(f"{line}: unexpected crs '{r['crs']}' (expected EPSG:4326)")
        if r.get("feature_type") and r["feature_type"] not in KNOWN_FEATURE_TYPES:
            errors.append(f"{line}: unknown feature_type '{r['feature_type']}'")
        if r.get("confidence") and r["confidence"] not in KNOWN_CONFIDENCE:
            errors.append(f"{line}: unknown confidence '{r['confidence']}'")
        for prov in ("source", "derivation_method"):
            if prov in r and not r[prov]:
                errors.append(f"{line}: missing provenance '{prov}'")
    if check_scores:
        try:
            from src.scores import COMMITTED_SCORES, all_scores
            for tid, expected in COMMITTED_SCORES.items():
                if all_scores()[tid] != expected:
                    errors.append(f"score reproduction: {tid} computed {all_scores()[tid]} != committed {expected}")
        except ImportError:
            pass
    return errors


def load_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_geojson(path):
    with open(path, encoding="utf-8") as f:
        gj = json.load(f)
    recs = []
    for feat in gj.get("features", []):
        props = dict(feat.get("properties", {}))
        lon, lat = feat["geometry"]["coordinates"][:2]
        props.setdefault("longitude", lon)
        props.setdefault("latitude", lat)
        props.setdefault("crs", "EPSG:4326")
        recs.append(props)
    return recs


def main(paths):
    failed = False
    for p in paths:
        recs = load_geojson(p) if p.endswith(".geojson") else load_csv(p)
        errs = validate_records(recs)
        warns = find_duplicate_locations(recs)
        if errs:
            failed = True
            print(f"FAIL {p} ({len(errs)} errors):")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK {p} ({len(recs)} records)")
        for w in warns:
            print(f"  warning: {w}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["maps/PIN_POINTS.csv"]))
