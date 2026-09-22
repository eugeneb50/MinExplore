"""Immutable source registry (stdlib only).

Every target traces: target -> derived evidence -> transformation ->
source asset -> publisher, license, retrieval date. Registry lives in
sources/registry.json; this module validates records against
schemas/source_registry.schema.json (structural subset enforced here so CI
needs no third-party validator).
"""
from __future__ import annotations

import hashlib
import json
import os

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "sources", "registry.json")

REQUIRED = ["source_id", "publisher", "dataset_name", "source_version",
            "retrieved_at", "license", "commercial_use_allowed",
            "ai_use_allowed", "redistribution_allowed", "original_crs",
            "citation"]
OPTIONAL = ["checksum", "original_resolution", "processing_version",
            "transform_history", "allowed_uses", "url"]


def load(path=REGISTRY_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate(records):
    """Return list of error strings (empty = valid)."""
    errors = []
    seen = set()
    for i, r in enumerate(records):
        where = f"record {i} ({r.get('source_id', '?')})"
        for col in REQUIRED:
            if col not in r or r[col] in (None, ""):
                # retrieved_at may be "runtime"/"on demand" — still required present
                errors.append(f"{where}: missing required field '{col}'")
        for flag in ("commercial_use_allowed", "ai_use_allowed",
                     "redistribution_allowed"):
            if flag in r and not isinstance(r[flag], bool):
                errors.append(f"{where}: '{flag}' must be boolean")
        sid = r.get("source_id", "")
        if sid:
            if sid in seen:
                errors.append(f"{where}: duplicate source_id '{sid}'")
            seen.add(sid)
    return errors


def fingerprint(records):
    h = hashlib.sha256()
    for r in sorted(records, key=lambda r: r.get("source_id", "")):
        h.update(json.dumps(r, sort_keys=True).encode())
    return h.hexdigest()[:16]


def commercial_clean(records):
    """Subset usable in paid deliverables."""
    return [r for r in records if r.get("commercial_use_allowed") is True]


def main(path=REGISTRY_PATH):
    doc = load(path)
    records = doc.get("sources", []) if isinstance(doc, dict) else doc
    errs = validate(records)
    if errs:
        print("REGISTRY ERRORS:")
        for e in errs:
            print(" -", e)
        raise SystemExit(1)
    print(f"registry OK: {len(records)} sources, fingerprint {fingerprint(records)}")
    clean = [r["source_id"] for r in commercial_clean(records)]
    print(f"commercial-clean ({len(clean)}): {', '.join(clean)}")


if __name__ == "__main__":
    main()
