<!-- CODEGRAPH_START -->
## CodeGraph

In repositories indexed by CodeGraph (a `.codegraph/` directory exists at the repo root), reach for it BEFORE grep/find or reading files when you need to understand or locate code:

- **MCP tool** (when available): `codegraph_explore` answers most code questions in one call — the relevant symbols' verbatim source plus the call paths between them, including dynamic-dispatch hops grep can't follow. Name a file or symbol in the query to read its current line-numbered source. If it's listed but deferred, load it by name via tool search.
- **Shell** (always works): `codegraph explore "<symbol names or question>"` prints the same output.

If there is no `.codegraph/` directory, skip CodeGraph entirely — indexing is the user's decision.
<!-- CODEGRAPH_END -->

# MinExplore — AGENTS.md

Research repo: satellite mineral prospecting, Baja California. Stdlib-first: scoring/validation/export run with no third-party deps (`python3 -m unittest`).

## Structure

- `mineral_pipeline.py` — network entry point; modes `screen|dem|spread|bands|tiles|pins|turquoise` (see `README.md` table). `pins`/`turquoise` need no `--lat/--lon`.
- `src/scores.py` — v3 split model: prospectivity vs feasibility (sole authority; T1 5.3/6.0, T2 7.2/4.3, T3 5.7/5.7; v2 blended 5.4/6.3/5.5 frozen legacy); `src/uncertainty.py`, `src/frontier.py`, `src/registry.py` (`sources/registry.json`); `src/validate.py` — record checks; `src/export.py` — GeoJSON + field packages.
- `api/server.py` — stdlib HTTP API + static server (no FastAPI); `site/coordinate.html` needs it. `docs/TERMS.md` + `docs/FEE_FLOW.md` govern paid use; paid deliverables = commercial-clean inputs only.
- `scripts/build_data.py` — canonical dataset builder (v2 IDs + provenance → `maps/`, `site/maps/`, `sample_data/`). `scripts/hires_pins.py`, `turquoise_map.py`, `make_previews.py` — map/sheet generators.
- `schemas/` (JSON Schema + data dictionary), `tests/` (unittest), `sample_data/` (DataKit), `.github/workflows/ci.yml`.
- `skills/predictive-analytics/` — agent skill for Tier 1 sensitivity + Tier 2 Monte Carlo + frontier-review protocol. Reads `src/scores.py`, never writes it; Tier 2 outputs stay in gitignored `predictive/`.
- `data/` — primary sources. `maps/` + `*.md` reports are generated/committed artifacts — read, don't regenerate casually.
- `site/` — static publish mirror (public demo, no backend); hero "View source code" still points at a `github.com/example` placeholder — replace with the real repo URL.

## Run

- Tests/validation/DataKit: no install. `screen`/`pins`/`turquoise`: `numpy`, `Pillow`. `dem`/`spread`: + `rasterio`, `pyproj` (`pip install numpy pillow rasterio pyproj`).
- `python3 -m unittest && python3 src/validate.py maps/PIN_POINTS.csv && python3 src/registry.py && python3 api/server.py --port 8080` (coordinate page; static-only alternative: `cd site && python3 -m http.server 8080`).
- `bands` requires `EARTHDATA_USER` / `EARTHDATA_PW`. `tiles --provider bing` requires `--key`; default `osm` needs none. All modes need network.

## Conventions / gotchas

- Truth hierarchy: `src/scores.py` + `scripts/build_data.py` + `schemas/` over site copy or docs. Ranks are NOT probabilities; B/R is an unvalidated RGB heuristic — never claim mineral IDs from it.
- `spread` caches DEM tiles at `<outdir>/../data/dem14_*.tif`, `dem` at `<outdir>/dem14_*.tif` — reuse, don't delete.
- i18n: `site/index.html` `I18N` dict (en/es/zh/ru) overwrites markup on load — update the dict, not just the HTML. EN leads; other locales pending.
- Resolution language: SRTM ~30 m native → 10 m working grid; S2 bands 4×10/6×20/3×60 m; rendered m/px ≠ sensor GSD. Keep the caveat on any new coordinates (±10–20 m horizontal).
- Do NOT scrape `tile.google.com` / `bing.com` tiles (ToS). Demo quota is browser-local by design (static host, no backend).
