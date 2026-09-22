"""CSV <-> GeoJSON export + field-package builder (Workstream 7). Stdlib only."""
from __future__ import annotations

import csv
import io
import json
import zipfile

GEOJSON_COLUMNS = [
    "record_id", "target_id", "latitude", "longitude", "crs", "feature_type",
    "source", "source_page", "source_date", "coordinate_accuracy_m",
    "derivation_method", "confidence", "field_action", "license",
    "created_at", "pipeline_version",
]


def records_to_geojson(records):
    features = []
    for r in records:
        props = {k: r.get(k, "") for k in GEOJSON_COLUMNS if k not in ("latitude", "longitude")}
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [float(r["longitude"]), float(r["latitude"])]},
            "properties": props,
        })
    return {"type": "FeatureCollection", "features": features}


def records_to_csv(records, extra=("label", "area")):
    cols = list(GEOJSON_COLUMNS) + [c for c in extra if any(c in r for r in records)]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    for r in records:
        w.writerow(r)
    return buf.getvalue()


def build_field_package(target_id, records, scoring_note, readme_extra=""):
    """Return zip bytes: GeoJSON + CSV + README for one target (offline GPS use)."""
    mine = [r for r in records if r.get("target_id") == target_id]
    gj = json.dumps(records_to_geojson(mine), indent=1)
    csv_text = records_to_csv(mine)
    readme = (
        f"Field package {target_id} (Baja Mineral Explorer, desk study only)\n"
        f"CRS: EPSG:4326 (WGS84). Imagery/DEM error: +/-10-20 m horizontal.\n"
        f"{scoring_note}\n{readme_extra}\n"
        "Not investment/drilling advice. Verify in field + official registers.\n"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{target_id}_pins.geojson", gj)
        z.writestr(f"{target_id}_pins.csv", csv_text)
        z.writestr("README.txt", readme)
    return buf.getvalue()
