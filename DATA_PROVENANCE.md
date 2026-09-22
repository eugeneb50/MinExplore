# Data provenance

> **Fee-product gate:** this repo is CC BY-NC-SA 4.0 and two inputs below are
> non-commercial (EOX) or research-use (Esri). Nothing derived from an NC /
> research-use source may appear in a paid deliverable. Paid products
> (`docs/FEE_FLOW.md`) must be built from commercially-clean inputs only —
> each row carries explicit `commercial_use_allowed` / `ai_use_allowed` /
> `redistribution_allowed` flags, mirrored in machine-readable
> `sources/registry.json`.

| Source | What is used | Native resolution | How it is used here | License / terms | Commercial? | AI/RAG use? | Redistribution? | Original CRS | Accessed |
|---|---|---|---|---|---|---|---|---|---|
| EOX s2cloudless (Copernicus Sentinel-2 2020) | Rendered RGB **viewing** composite via WMTS | S2 bands 4×10 m / 6×20 m / 3×60 m; composite is a visual product, not analysis-ready reflectance | `screen`/`spread` tone classes + unvalidated RGB heuristic | CC BY-NC-SA 4.0 (non-commercial research) | **No** — NC | Allowed (NC-bound) | ShareAlike only | EPSG:3857 (tiles) | 2026-08, `tiles.maps.eox.at` |
| Esri World Imagery | Viewing true-color tiles (Maxar-class) | Rendered Web-Mercator display scale (z17 ≈1.03, z18 ≈0.52 m/px at ~30° N) — not sensor GSD | Pin-sheet base layers, demo base map | Esri/Maxar terms, research use | **No** — research use | No | No | EPSG:3857 (tiles) | 2026-08, `server.arcgisonline.com` |
| USGS elevation-tiles-prod | SRTM-derived GeoTIFF tiles (z14) | ~30 m native, resampled to 10 m working grid (no new detail) | Slope/aspect/hillshade/drainage, target elevations | Public domain | Yes | Yes | Yes | EPSG:3857 (tiles; source DEM geographic) | 2026-08, `s3.amazonaws.com/elevation-tiles-prod` |
| SGM Carta El Aguajito H11-B85 (2009) | 1:50,000 geologic-mineral map + mine inventory (`data/sgm_saml_text.txt`) | 1:50,000 (≈500 m transcription accuracy for workings) | Geology cross-ref, 14-workings inventory, target context | SGM public sheet | Yes — public government data (cite SGM) | Yes | Yes, with citation | Mixed — see CRS note below | PDF transcribed 2026-08 |
| OSM / open-elevation | Toponyms (Cerro la Turquesa/Palmita, MEX 2); point elevations for demo | — / ~30 m | Labels; demo elevation lookup (keyless API) | ODbL / open-elevation terms | Yes (attribution required) | Yes | Yes, under ODbL | EPSG:4326 | runtime |
| NASA HLS via CMR (`bands` mode only) | Landsat 8/9 + Sentinel-2 surface reflectance, 30 m | 30 m | NDVI/ferric/clay/carbonate indices; needs free Earthdata login | Open, account required | Yes (US public data) | Yes | Yes | Per-granule (UTM/Sinusoidal) | on demand |

## Source CRS history (do not silently coerce to WGS84)

SGM cartography spans geodetic reference systems (notably NAD27 and ITRF92),
which produce gaps/overlaps between sheets. Every ingested layer records
`original_crs` + transform history in `sources/registry.json`; WGS84 is a
*derived* working CRS, and each derived coordinate inherits the accuracy budget
of its source (see `coordinate_accuracy_m` in `schemas/datadictionary.md`).

## What “m/px” means on each product

- Pin sheets: **rendered** Web-Mercator display scale at sheet latitude (NOT sensor GSD).
- Spread sheets: **export** scale (~4 m/px at 1000-px panels over 4 km).
- Corridor overview: **export** scale of the upscaled mosaic.
- DEM derivatives: computed on the **10 m working grid** from ~30 m native SRTM.
