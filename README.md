# Baja Mineral Explorer — a reproducible geospatial data pipeline for mineral-exploration field planning

Ingests public geological, satellite, elevation, and mine-inventory data; validates and normalizes coordinates; ranks candidate targets; and produces GPS-ready field packages.

This desk study organizes incomplete public evidence into explicit, field-testable hypotheses — it is not a discovery claim. No field survey, geochemistry, spectroscopy, or drilling has validated the three candidate targets.

**Reviewer shortcuts:** [Analyze a coordinate](site/coordinate.html) (full-stack page: public data + maps, paid deeper analysis) · [Run the demo](site/index.html#demo) (public, no login) · [Architecture](ARCHITECTURE.md) · [Tests and CI](#tests) · [Sample DataKit](sample_data/) · [Data provenance](DATA_PROVENANCE.md) · [Terms](docs/TERMS.md) · [Build guide](GUIDE.md)

**Stack (honest):** Python stdlib for scoring/validation/export/registry/API (`numpy`/`Pillow`; `rasterio`/`pyproj` for `dem`/`spread`) · static Leaflet site + one stdlib API service (`api/server.py`, no FastAPI until demand justifies it) · no database (GeoParquet/DuckDB-ready columns; PostGIS later as a loader, not a rewrite).

## What problem does this solve?

Prospecting field work starts from scattered public evidence (a 2009 SGM sheet, viewing-grade satellite mosaics, old mine lists). This pipeline turns that into ranked, GPS-importable field hypotheses with explicit provenance and known error bars (±10–20 m horizontal).

## What data enters the system?

| Source | Product | Resolution truth | Access |
|---|---|---|---|
| EOX Sentinel-2 2020 cloudless | Rendered RGB **viewing** composite (visual consistency, not analysis-ready reflectance; S2 bands natively 4×10 m / 6×20 m / 3×60 m) | rendered tiles | Open, CC BY-NC-SA 4.0 |
| Esri World Imagery | Viewing true color (rendered Web-Mercator display scale: z17 ≈1.03, z18 ≈0.52 m/px — not sensor GSD) | rendered | Tile service, research use |
| USGS elevation-tiles-prod | SRTM elevation, ~30 m native, resampled to 10 m working grid (no new detail) | ~30 m native | Public domain |
| SGM El Aguajito H11-B85 (2009) | 1:50,000 geologic-mineral map + 14-workings inventory (`data/sgm_saml_text.txt`) | 1:50,000 (~500 m transcription accuracy) | Public sheet |
| OSM / OpenTopoMap | Basemap tiles (`tiles --provider osm`, the default) + demo Terrain layer; OSM toponyms (Cerro la Turquesa/Palmita, MEX 2) | rendered tiles | Open, ODbL |
| open-elevation API | Point elevations for the demo coordinate runner (keyless) | ~30 m | Free API, no key |
| NASA HLS via CMR (`bands` mode only) | Landsat 8/9 + Sentinel-2 surface reflectance, 30 m → NDVI/ferric/clay/carbonate indices | 30 m | Open, free Earthdata login required |

Bing Maps is a supported `tiles --provider bing` option (key required) but was not used in any committed product. Full per-source detail lives in [DATA_PROVENANCE.md](DATA_PROVENANCE.md).

## How is it normalized?

WGS84 (EPSG:4326) in and out; Web-Mercator only as an internal mosaic grid; UTM 11N for field bearings. `scripts/build_data.py` is the single source of truth for pin/mine records: globally unique v2 IDs, 16 provenance columns, CSV + GeoJSON outputs. `src/validate.py` enforces unique IDs, valid coords, CRS declaration, provenance, and score reproduction.

## How are targets ranked?

Split model in `src/scores.py` v3.0.0 (deterministic, CI-enforced) — geological
**prospectivity** and access/legal/environmental **feasibility**, shown side by
side and never blended:

| | Prospectivity | Feasibility |
|---|---|---|
| T1 Arroyo San Isidro | **5.3** | **6.0** |
| T2 Cerro la Turquesa | **7.2** | **4.3** |
| T3 Cerro la Palmita | **5.7** | **5.7** |

Prospectivity weights: geology 30 · workings 10 (deliberately downweighted — distance to a mine must not dominate) · spectral 20 · structure 25 · exposure 15. Feasibility weights: access 35 · water/regulatory 35 · land constraints 30 (SIAM/RAN/CONANP/CONAGUA pending → not-yet-assessed placeholder). `src/uncertainty.py` adds the coverage layer; `src/frontier.py` computes frontier priority = prospectivity × info-gain × feasibility − penalties (T3 currently leads on frontier priority precisely because feasibility matters). Ranks, not probabilities. The spectral factor is an **unvalidated RGB visual-screening heuristic** — never a mineral ID. v2 blended ranks (5.4/6.3/5.5) are frozen in code for history. Full evidence table on the [site](site/index.html#scores).

## What outputs are generated?

- `maps/PIN_POINTS.{csv,geojson}` — 36 field pins (v2 IDs + provenance), mirrored in `site/maps/`
- `maps/mine_inventory_elaguajito.{csv,geojson}` — 14 SGM workings + source/accuracy columns
- `maps/pins/*.jpg` + `turquoise_prospect_map.jpg` + field sheets (printable, preview WebPs in `site/maps/`)
- `sources/registry.json` — immutable source registry (license/commercial/AI/redistribution flags, CRS history)
- Public demo (static page): any coordinate → distances/bearings + JSON/GeoJSON + field-package download, 5/visitor browser-local quota
- Full-stack page (`site/coordinate.html` + `api/server.py`): any coordinate → six-system evidence pack + maps + fixed-fee deeper-analysis offer (`docs/FEE_FLOW.md`)

## How do I run it locally?

```bash
pip install numpy pillow rasterio pyproj   # rasterio/pyproj only for dem/spread
python3 -m unittest                        # scorer + validator + export + registry + api tests
python3 scripts/build_data.py              # regenerate canonical CSV/GeoJSON + DataKit
python3 src/validate.py maps/PIN_POINTS.csv
python3 src/registry.py                    # validate source registry
python3 mineral_pipeline.py pins           # map sheets (-> maps/pins/)
python3 mineral_pipeline.py spread --lat 30.048522 --lon -115.236173 --half-km 2 --outdir maps/t2
python3 mineral_pipeline.py prospect --outdir maps            # offline, no network
python3 mineral_pipeline.py evidence-pack --lat 30.048522 --lon -115.236173 --outdir maps
python3 api/server.py --port 8080          # full-stack page: open http://127.0.0.1:8080/coordinate.html
# static demo only (no API): cd site && python3 -m http.server 8080
```

`bands` needs free `EARTHDATA_USER`/`EARTHDATA_PW`; `tiles --provider bing` needs `--key` (default `osm` needs none). All modes need network.

## Tests

`python3 -m unittest` — `tests/test_scores.py` (committed ranks reproduce deterministically) + `tests/test_validate.py` (unique IDs, bad coords, provenance, GeoJSON round-trip, field-package contents). CI (`.github/workflows/ci.yml`) also validates all committed CSV/GeoJSON.

## Known limitations

- RGB-only screening cannot identify minerals; SWIR + field work required (see pipeline `NOTE ON SWIR`).
- Viewing composites ≠ analysis-ready reflectance; rendered m/px ≠ sensor resolution.
- Mine coordinates transcribed from 1:50,000 (~500 m accuracy); imagery/DEM ±10–20 m.
- Demo quota is browser-local (no backend by design); elevation lookup needs the open-elevation API.
- Not investment, drilling, or legal advice (MX Ley Minera 2023: public tender, ANP/water gates).
