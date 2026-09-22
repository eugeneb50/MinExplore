# MinExplore — Master Build Guide (GUIDE.md)

Single source of truth for the 9-workstream reviewer overhaul.
Constraints: **static-only demo** (no backend), **honest stack** (Python stdlib+numpy/PIL/rasterio + static Leaflet; no PostGIS/React/AWS), all 9 items in one pass.

## 0. Stack reality (do not invent)

- Pipeline: `mineral_pipeline.py` (argparse/urllib/numpy/PIL; `rasterio`+`pyproj` for dem/spread), `scripts/hires_pins.py`, `scripts/turquoise_map.py`.
- Site: `site/index.html` static demo + `site/coordinate.html` full-stack page (needs `api/server.py`) + `vendor/leaflet.js`.
- API: `api/server.py` stdlib HTTP (static + `/api/analyze|jobs|webhooks`); no FastAPI until demand justifies it.
- Data: `site/maps/PIN_POINTS.csv` (36 rows, duplicate `TGT`/`T2-1`/`T2-2` IDs — fix in W7), `site/maps/mine_inventory_elaguajito.csv` (14 rows, no CRS/provenance).
- Missing (to add): `src/ tests/ schemas/ sample_data/ .github/workflows/ LICENSE ARCHITECTURE.md DATA_PROVENANCE.md`.
- Known CLI quirk: `pins`/`turquoise` subcommands wrongly require `--lat/--lon` (fix argparse in this pass).

## 1. W6 — Scoring model (build first, locks truth)

- `src/scores.py` v3: `PIPELINE_VERSION` 3.0.0, split `PROSPECTIVITY_WEIGHTS` (30/10/20/25/15) + `FEASIBILITY_WEIGHTS` (35/35/30) over `EVIDENCE[target][factor] = {score, confidence, tag, note}`; `prospectivity()`/`feasibility()` deterministic; committed split T1 5.3/6.0, T2 7.2/4.3, T3 5.7/5.7. v2 blended (5.4/6.3/5.5) frozen as legacy. Disclaimer: NOT a probability of mineralization.
- `src/uncertainty.py` (coverage layer, separate), `src/frontier.py` (frontier priority = P × info-gain × F − penalties), `src/registry.py` (`sources/registry.json`: license/commercial/AI/redistribution + CRS history).
- Test `tests/test_scores.py`: v2 legacy frozen + v3 split committed; `tests/test_frontier.py` (formula, penalties, registry incl. NC-exclusion); `tests/test_api.py` (contract on localhost).

## 2. W7 — IDs + provenance + GeoJSON (build second)

- ID remap: `TGT`→`T1-TGT`/`T2-TGT`/`T3-TGT` (+`T2i-TGT` for detail sheet); overview `T2-1,T2-2,T2-6` stay; detail rows → `T2-DETAIL-01/02/03`. Publish remap table (old→new) in `schemas/datadictionary.md`.
- Canonical columns: `record_id,target_id,latitude,longitude,crs,feature_type,source,source_page,source_date,coordinate_accuracy_m,derivation_method,confidence,field_action,license,created_at,pipeline_version` (+ legacy `label,area` kept).
- New `src/validate.py` checks: unique IDs, valid WGS84, required columns, known feature types {target,pale,struct,sed,out,mine}, CRS==EPSG:4326, provenance non-empty, duplicate locations flagged, score reproduction via `src/scores.py`.
- New `src/export.py`: CSV→GeoJSON (`EPSG:4326`, properties = provenance), field-package builder (GeoJSON+CSV+README → zip).
- Outputs: rewrite `maps/PIN_POINTS.csv` + `site/maps/PIN_POINTS.csv`, add `PIN_POINTS.geojson` in both, `mine_inventory.geojson`, `schemas/pins.schema.json`, `sample_data/` subset (=DataKit).
- Edit `scripts/hires_pins.py` PINS keys + embedded site `PINS` array to new IDs.

## 3. W4+W5 — Wording + resolution truth

- Swaps (site hero/cards/FAQ/JSON-LD, `site/llms.txt`, root `README.md`, pipeline docstring): surveyed→"remotely screened candidate targets"; "Surveys identify"→"This desk study identifies"; "Highest-potential"→"Highest-ranked under the current desk-screening model"; "B/R clay-calcite indicator"→"unvalidated RGB visual-screening heuristic"; "Legal pipeline"→"pipeline using documented data-access methods". Add hypothesis framing line.
- Resolution: "SRTM ~30 m native, resampled to 10 m working grid (no new detail)"; S2 "4×10 m / 6×20 m / 3×60 m — analysis used EOX rendered RGB viewing tiles, not analysis-ready surface reflectance" + EOX visual-consistency caveat; annotate every m/px figure as native-GSD vs rendered vs export scale.
- i18n: EN first + "translations pending" note; backfill es/zh/ru if time permits.

## 4. W1+W8 — Reviewer bar + case study + repo docs

- Hero: new H1 "Baja Mineral Explorer — a reproducible geospatial data pipeline for mineral-exploration field planning" + ingest→validate→rank→package subline + 5-link bar (Run the demo → #runner; View source → repo URL placeholder `REPO_URL`; Architecture → ARCHITECTURE.md/section; Tests and CI → badge + tests/; Download sample DataKit → sample_data/).
- New site section "Engineering decisions and tradeoffs" (10 prompts, 2–4 sentences each, traceable) + mirror in `ARCHITECTURE.md`.
- New `README.md` (problem/inputs/normalization/ranking/outputs/local-run/tests/limitations), `ARCHITECTURE.md`, `DATA_PROVENANCE.md`.

## 5. W2 — Public static demo

- `site/index.html`: runner public by default (delete key requirement for runner; keep or drop member gate — drop it, note premium/batch as "contact" line). `localStorage` quota `bme_demo_count` (5/visitor, honest "browser-local" label). "Load example coordinate" (T2) button. Keep haversine/bearing/elevation; add JSON + GeoJSON `<details>` output, "Download field package" (Blob: GeoJSON+CSV+README), loading/error states on elevation fetch, share-link preserved.
- Acceptance: cold visitor runs example → map + distances + JSON + download, no key.

## 6. W9 — Perf + delivery

- `scripts/make_previews.py` (PIL): `site/maps/*-preview.webp` (~800px, q70) for each large JPG; gallery/lightbox use previews, full-res via download links; keep `loading="lazy"`; low-bandwidth toggle (S2+CSV only); offline package = W2 bundle. Document CDN/Cache-Control in `site/README.md`; COGs noted as future (current rasters are PNG/JPG).
- Verify: Lighthouse/WebPageTest post-deploy (manual), record page weight before/after.

## 7. CI + packaging + license

- `.github/workflows/ci.yml`: `python -m unittest` + `python src/validate.py` on committed data + sample_data.
- `Dockerfile` + `docker-compose.yml`: single python-only service for reproducible local runs (document: no DB/tileserver; optional).
- `LICENSE`: CC BY-NC-SA 4.0 for content/code (matches site footer + EOX NC-SA flow-down); imagery stays provider-licensed (stated).
- Fix `pins`/`turquoise` argparse (`required=False` for lat/lon on those two).

## Build order

scores → validate/export → data regen → wording/resolution → hero/case-study/docs → demo JS → previews → CI/docker/license → full verify (`python -m unittest`, validate, local serve, Lighthouse notes).
