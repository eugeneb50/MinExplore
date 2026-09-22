# Pin record data dictionary (record v2, `pipeline_version` 2.0.0)

JSON Schema: `pins.schema.json`. Canonical builder: `scripts/build_data.py`. Validator: `src/validate.py`.

| Column | Meaning | Example |
|---|---|---|
| `record_id` | Globally unique ID (v2) | `T2-OVERVIEW-01` |
| `target_id` | Owning target/zone (`T1,T2,T3,ZA,ZB,ZC`) | `T2` |
| `latitude` / `longitude` | WGS84 decimal degrees | `30.0502 / -115.2466` |
| `crs` | Always `EPSG:4326` | `EPSG:4326` |
| `feature_type` | One of `target,pale,struct,sed,out,mine` | `pale` |
| `source` | Imagery/map the pin was picked on | `Esri World Imagery tile service (research use)` |
| `source_page` | Sheet or record within the source | `t2_pins` |
| `source_date` | Source vintage | `2024-26` |
| `coordinate_accuracy_m` | Horizontal error budget | `20` (imagery) / `500` (1:50k transcription) |
| `derivation_method` | How the point was produced | `RGB visual-screening heuristic pick (unvalidated; …)` |
| `confidence` | `High/Medium/Low` | `Low` |
| `field_action` | What to do on site | `alteration front — sample both sides of contact` |
| `license` | Terms flowing to the record | `CC BY-NC-SA 4.0 (rendering); …` |
| `created_at` / `pipeline_version` | Dataset vintage / code version | `2026-08-25 / 2.0.0` |
| `label` / `area` | Legacy display columns (kept for compatibility) | `P1 pale mass CENTER / T2 PIN MAP` |

## ID history v1 → v2 (breaking change, 2026-09)

| v1 | v2 | Reason |
|---|---|---|
| `TGT` (T1 sheet) | `T1-TGT` | reused on 4 sheets |
| `TGT` (T2 sheet) | `T2-TGT` | reused on 4 sheets |
| `TGT` (T2 detail) | `T2i-TGT` | reused on 4 sheets |
| `TGT` (T3 sheet) | `T3-TGT` | reused on 4 sheets |
| `T2-1,T2-2,T2-4,T2-5,T2-6,T2-7` (overview) | `T2-OVERVIEW-01…06` | collided with detail rows |
| `T2-1,T2-2,T2-6` (detail) | `T2-DETAIL-01…03` | collided with overview rows |

`T1-*`, `T3-*`, `A-*`, `B-*`, `C-*` were already unique and kept. Detail re-plots intentionally share coordinates with their overview twins (flagged as warnings, not errors, by the validator).
