# Architecture

```
public inputs (EOX/USGS/Esri/SGM)                checked-in evidence
        │                                              │
        ▼                                              ▼
mineral_pipeline.py ── screen/dem/spread ──► maps/*.png/*.jpg (viewing products)
  (numpy/Pillow;            │                 + field_waypoints.csv
   rasterio/pyproj          ▼
   for dem/spread)   scripts/hires_pins.py ──► maps/pins/*.jpg (static sheets)
                     scripts/turquoise_map.py ─► corridor overview
                            │
scripts/build_data.py ◄─────┘ (canonical IDs + provenance, stdlib only)
        │   ▲
        │   │  src/scores.py      — v3 split: prospectivity vs feasibility (sole authority)
        │   │  src/uncertainty.py — coverage layer (kept separate from prospectivity)
        │   │  src/frontier.py    — frontier priority = P × info-gain × F − penalties
        │   │  src/registry.py    — immutable source registry (license/CRS history)
        │   │  src/validate.py    — unique IDs, coords, CRS, provenance, score repro
        │   │  src/export.py      — GeoJSON + field-package builder
        ▼   │
maps/PIN_POINTS.{csv,geojson} ──► site/maps/ (published mirror) ──► site/index.html
mine_inventory.{csv,geojson} ──►   (static Leaflet demo, no backend)   + *-preview.webp
sources/registry.json ──► commercial-clean subset gates paid deliverables
        │                                                    ▲
sample_data/ (DataKit)                       quota: 5/visitor (static demo) /
tests/ + .github/workflows/ci.yml ──► green badge  30/hr/IP (API free tier)

Full-stack surface (optional, stdlib only):
  site/coordinate.html ──POST /api/analyze──► api/server.py ──► evidence pack
        │ (6 tabs: prospectivity/spectroscopy/structure/docs/feasibility/uncertainty)
        └── fee panel ──POST /api/jobs──► jobs/jobs.jsonl ──► manual fulfillment
```

## Module map

- `mineral_pipeline.py` — network entry point (modes `screen|dem|spread|bands|tiles|pins|turquoise` + offline `prospect|feasibility|evidence-pack`). `pins`/`turquoise` delegate to `scripts/`.
- `src/scores.py` — v3 split weights + evidence; sole authority for prospectivity/feasibility (v2 blended mean frozen for history).
- `src/uncertainty.py` — coverage/uncertainty layer, visible separately.
- `src/frontier.py` — frontier-priority formula + info-gain estimator.
- `src/registry.py` — source registry validation + commercial-clean subset.
- `src/validate.py` — record validation; CLI exits non-zero on errors, prints co-location warnings.
- `src/export.py` — CSV↔GeoJSON + zip field packages (also mirrored in demo JS for the browser).
- `api/server.py` — stdlib HTTP: static `site/` + `/api/analyze|jobs|webhooks`. No FastAPI until demand justifies it.
- `scripts/build_data.py` — canonical dataset builder; writes `maps/`, `site/maps/`, `sample_data/`.
- `scripts/make_previews.py` — gallery WebP previews (~5% of full-res weight).
- `site/index.html` — static demo page; embedded TARGETS/MINES/PINS mirror the canonical CSVs.
- `site/coordinate.html` — full-stack analyze page (needs `api/server.py`); six tabs + fee panel.

## Key decisions (see site “Engineering decisions and tradeoffs”)

Files are the database (36 pins, 14 workings — PostGIS unwarranted). CRS: EPSG:4326 public, EPSG:3857 internal mosaic grid, UTM 11N for bearings. DEM tiles cached on disk and reused. `pipeline_version` + `created_at` on every record; ID history in `schemas/datadictionary.md`. Degradation: no elevation API → distances still work; no imagery → CSV/GeoJSON still work offline.
