# baja-mineral — satellite-based mineral prospecting, Baja California, MX

**Single entry point:** `mineral_pipeline.py` — all modes below.

| Target | Coordinates | Site | Desk score |
|---|---|---|---|
| **T1** | 29.903605, -115.383656 | Arroyo San Isidro | 5.4/10 |
| **T2** | 30.048522, -115.236173 | **Cerro la Turquesa** (740 m) | **6.3/10** |
| **T3** | 30.025725, -115.286885 | **Cerro la Palmita** (800 m) | 5.5/10 |

## Pipeline commands

```bash
python3 mineral_pipeline.py screen    --lat <LAT> --lon <LON> --outdir maps/<t>   # S2 RGB surface screen (no account)
python3 mineral_pipeline.py dem       --lat <LAT> --lon <LON> --half-km 2 --outdir maps/<t>  # 10 m DEM: slope/aspect/hillshade
python3 mineral_pipeline.py spread    --lat <LAT> --lon <LON> --half-km 2 --outdir maps/<t>  # 3x3 field sheet + GPS waypoints
python3 mineral_pipeline.py pins                                                     # 7 sub-meter pin sheets (36 pins) -> maps/pins/
python3 mineral_pipeline.py turquoise                                                # corridor overview map -> maps/
python3 mineral_pipeline.py bands     --lat <LAT> --lon <LON> --days 365 --outdir maps/<t>  # 30 m spectral indices (free Earthdata login)
python3 mineral_pipeline.py tiles     --lat <LAT> --lon <LON> --zoom 17 --provider osm --outdir maps/<t>  # basemap mosaic (bing w/ key)
```

## Reports

| File | What |
|---|---|
| `ANALYSIS_REPORT.md` | **T1** — methodology (Google/Bing/open-data routes) + deep analysis + scoring + next steps |
| `ANALYSIS_TARGET2.md` | **T2** — pale argillic mass + NE–SW lineament + turquoise toponym |
| `ANALYSIS_TARGET3.md` | **T3** — corridor ridge between T1 and T2; three-target pattern |
| `TURQUOISE_TARGETS.md` | **Ranked turquoise prospecting guide** (4 zones + 5-day field protocol) |
| `PIN_POINTS.md` | **High-res pin-map guide** (7 sheets + pin types + usage) |

## Maps & data

| Path | What |
|---|---|
| `maps/pins/*.jpg` + `PIN_POINTS.csv` | **36 pin-point exploration pins** on sub-meter imagery (Esri z17/z18, S2 z16) |
| `maps/turquoise_prospect_map.jpg` | Corridor overview: 14 SGM workings + 4 prospect zones + T1/T2/T3 |
| `maps/map_spread_4km.jpg`, `maps/t2/…`, `maps/t3/…` | 4×4 km 3×3 field sheets + `field_waypoints.csv` per target |
| `maps/class_map.png`, `br_map.png`, `hillshade.png` | T1 layer products |
| `maps/mine_inventory_elaguajito.csv` | 14 documented SGM Cu-Fe workings (coords + mineralogy) |
| `data/sgm_saml_text.txt` | **SGM El Aguajito H11-B85 1:50,000 (2009) — full text** (primary source) |
| `data/sgm_catalog_text.txt` | SGM 1:50,000 sheet catalog (H11-B series, sheet names) |
| `scripts/hires_pins.py`, `scripts/turquoise_map.py` | Map generators (also via `pins` / `turquoise` modes) |

## Key sources
SGM El Aguajito H11-B85 (2009) PDF → `data/sgm_saml_text.txt` · EOX s2cloudless (S2 2020, CC BY-NC-SA 4.0) · USGS elevation-tiles-prod (10 m DEM) · Esri World Imagery (research use) · NASA CMR/HLS · SGM catalog · mindat · Arqueología Mexicana (turquoise belt). Full list: `ANALYSIS_REPORT.md` Appendix B.
