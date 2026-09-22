# Satellite-Based Mineral Asset Analysis — TARGET 2

> **Score migration (v3.0.0):** ranks cited in this report use the frozen v2 blended mean (T1 5.4 / T2 6.3 / T3 5.5). Current model splits prospectivity vs feasibility (T1 5.3/6.0, T2 7.2/4.3, T3 5.7/5.7) — see `src/scores.py`.
## 30.048522, -115.236173 — slopes of **Cerro la Turquesa** (740 m), Municipio de San Quintín, Baja California, MX

**Prepared:** 2026-08-25 · **Desk-study v1** (remote data + SGM El Aguajito sheet context; no field data)
**Companion files:** `maps/t2/` (map sheet + waypoints) · main report: `ANALYSIS_REPORT.md` (Target 1, 21 km SW)

---

## 0 · Executive summary

| Item | Result |
|---|---|
| Exact location | On the **N/W slope of Cerro la Turquesa (740 m a.s.l.)**, target at 617 m; eastern flank of the central sierra, San Quintín municipio. **Carretera Transpeninsular (México 2) passes ~1.5–2 km SW** — far better access than Target 1 |
| Terrain (10 m DEM, 4×4 km) | 555–757 m (mean ~660); local max 757 m at 30.0330, -115.2212 (2.6 km SSE); steeper than T1: 13.6% of area >15° slope, max 40.9°; aspect multi-directional (SSW/WSW/NNE/N) |
| Remote sensing (10 m S2 2020 + samples) | Three distinct surface features: **(a)** a pale grey-green **exposed/low-chroma mass** ~900 m W, 200 m N (≈0.5–0.8 km across; R 0.39/G 0.35/B 0.22, S≈0.44, B/R 0.55–0.63 vs brown-soil B/R 0.44–0.54); **(b)** a **straight km-scale NE–SW linear bright band** ~1 km E (B/R 0.60–0.64 — the strongest blue-shift in the area; road vs fault-scarp/lineament — ground-truth); **(c)** the target point itself sits on a **pale surface** (B/R 0.63). VEG 9.1% (more cover than T1) |
| Geology | Same **Alisitos terrane** as Target 1 (eastern flank of the El Aguajito sheet area; units: Kapa A-BvA andesite/breccia + Ks D-Tn/Ks Gr-Gd batholith intrusives + Kcm Rosario Fm). SGM: argillic alteration widespread; conjugate NW-SE/NE-SW structure + N-S relays; circular lineaments around intrusives |
| Mineralization context | **The toponym "Cerro la Turquesa" is at the point** — surface evidence of historic turquoise (Cu) mining. The documented **Zona Mineralizada "La Turquesa"** (SGM: low-sulfidation epithermal Cu-Fe ± Au, 12 abandoned workings) lies **13–20 km W along the same 30.0–30.1°N band**; La Bonita mine is at **30.048 N — the exact same latitude as this target, 17 km W**. Regional turquoise = porphyry-copper-associated (Aridamérica belt, BCS/BCN/Sonora) per Arqueología Mexicana; mindat: turquoise locality "20 km east of El Rosario… northern end of a belt known for copper and iron mineralization" |
| Overall desk rating | **6.3/10 — MODERATE-TO-GOOD: the stronger of the two targets.** Pale exposed surface + turquoise toponym + documented Cu-Fe belt at the same latitude + highway access. Best first moves: log the pale mass outcrop, sample its drainage, and identify the NE-SW lineament |

---

## 1 · What the imagery shows (S2 2020, 10 m + 5×5 z15 mosaic)

1. **Pale mass (main anomaly):** large, mottled, low-chroma grey-green surface draping the N slope of the hill W of the target. Brighter and desaturated vs the brown surrounding slopes; vegetation only in the gullies cutting it. In RGB it reads as pale exposed rock/weathered regolith — consistent with the argillic/pale alteration signature SGM documents for this terrane. B/R 0.55–0.63 (moderate blue-shift) — weaker than T1's patches but spatially much more coherent (km-scale single surface).
2. **NE–SW linear band:** straight, bright, ~km-scale feature crossing ~1 km E of the target (N30W–S30E trend). B/R 0.60–0.64 consistently. Two candidates: (i) **unpaved road** (SGM describes terracería access roads from the Transpeninsular to the mines), or (ii) **fault/lineament with pale fault scarp or altered gouge** — SGM maps NE–SW lineaments as a principal structure in this terrane. Road-vs-fault is a 10-minute field question; if it's a fault with a scarp, it's the primary structural control to follow.
3. **Target point:** on a pale, sparsely vegetated surface (B/R 0.63) — i.e., the pin itself is inside the anomalous surficial material, not on brown soil.
4. **SW corner:** Carretera Transpeninsular (México 2) + a small tan exposure near it (possible works/quarry — verify).

## 2 · Terrain (10 m DEM, 4×4 km)

| Metric | Value |
|---|---|
| Elevation | 555–757 m; target 617 m |
| Local max | 757 m at 30.0330, -115.2212 (2.6 km SSE) |
| Slope | mean 8.7°, median 7.9°, p90 16.3°, max 40.9°; 13.6% >15°, 1.3% >25° |
| Aspect | multi-directional: SSW 13%, WSW 12%, NNE 11%, N 10% (complex topography, not a single-sided bajada like T1) |
| Drainage | dendritic; N–S valley through the target (D-1…D-6 waypoints) = sampling transect |

## 3 · Distances to documented workings (La Turquesa zone, SGM 2009)

| Work | Distance | Bearing |
|---|---|---|
| 5 Minas | 13.3 km | WNW |
| El Cardonal / Esperanza | 13.6 km | WNW |
| Josefina | 14.4 km | NW |
| El Hormiguero | 15.1 km | WNW |
| **La Bonita** (vein-fault, brecha N53°E) | **16.9 km** | **W — same latitude (30.048 N)** |
| San Martín (malachite/azurite) | 17.2 km | NW |
| Zona La Turquesa (core) | 20.4 km | WNW |
| Target 1 (Arroyo San Isidro) | 21.4 km | SW |

## 4 · Prospectivity score

| Factor | /10 | Rationale |
|---|---|---|
| Metallogenic setting | 8 | Same Alisitos terrane & latitude band as the documented Cu-Fe-epithermal (±Au) corridor; turquoise toponym at the point |
| Structure | 7 | km-scale NE–SW lineament at the site (SGM's principal trend); N–S relay + conjugate system documented |
| Remote sensing | 6.5 | Coherent pale exposed surface + linear blue-shift band + target on pale surface; RGB-only (needs SWIR) |
| Outcrop/access to bedrock | 6 | Visible exposed pale surface within 1 km (better than T1's soil-mantled site) |
| Historical signal | 8 | "Cerro la Turquesa" toponym + 13–20 km to named Cu-Fe workings incl. same-latitude La Bonita |
| Water | 3 | Arid; ephemeral drainage — hard regulatory gate |
| Access & infrastructure | 6 | **México 2 at ~2 km** (vs T1: none nearby) |
| Environmental/social | 5 | No ANP screened at point (verify); sparse population; desert ecosystem |
| Regulatory certainty | 5 | Public-tender model; open-pit status in flux |
| **Total** | **≈6.3/10** | **MODERATE-TO-GOOD — prioritize over Target 1 for the field pass** |

## 5 · On-site test (≈2 h)

Waypoints in `maps/t2/field_waypoints.csv` (12 points; bearings/distances from TGT). Priority order:

1. **A — the pale mass (W, 1.6 km):** the key objective. Map its extent; identify the surface (exposed rock vs pale regolith); look for color zoning (blue-green = Cu/carbonate: azurite/malachite/chrysocolla; white = clay/silica); collect 5–10 rock chips + 1 bag of slope soil; photograph any old works (catas, trenches).
2. **The NE–SW band (E, ~1 km):** road or fault scarp? If a scarp: measure strike/dip, sample gouge; note any linear soil-color change.
3. **D-3/D-4 (arroyo, 360 m S / 360 m W):** stream-sediment samples (2 bags each) — the pale mass's drainage; assay Au, Ag, Cu, Fe, Pb, Zn, Mo by ICP-MS.
4. **F/G (N, ~0.5–1 km):** where the band crosses open ground — second look for lineament.
5. **STEEP-3 (SSE, 1.4 km, 36°):** steepest ground — bedrock outcrop check; note lithology (andesite? granodiorite? Rosario conglomerate?).
6. **RIDGE (SSE, 2.6 km, 757 m):** summit lithology + any views of structural trends.

Accuracy expectations: imagery ±10–20 m · DEM ±3–8 m · phone GPS ±5–15 m → 15–30 m total discrepancy expected; flag >50 m or systematic offsets. Send points + photos → I'll compute RMSE and recalibrate.

## 6 · Next steps (priority)

1. **Field pass** as above (this target outranks T1 for first visit).
2. **SWIR confirmation:** latest cloud-free S2 L2A + one ASTER L1A over 10×10 km → `mineral_pipeline.py bands` → clay/carbonate indices over the pale mass; also tests the NE–SW band.
3. **AVIRIS** (USGS SFUG, free) coverage check over 30.0–30.1 N / 115.2 W.
4. **Sheet H12-column for this square** (east of El Aguajito; not yet published in SGM's online catalog) — request from SGM (geoinfo@sgm.gob.mx); also ask specifically for any localities named "Cerro la Turquesa" in the CRM/SGM mine inventory (the 1980s-90s "yacimiento" inventories often predate the 2009 sheet).
5. **Concession screen:** minalia.sener.gob.mx lot map for 30.0–30.1 N, 115.2–115.3 W (the La Turquesa zone lots are documented in the SE/central sheet — check whether any extend to this square).
6. Water baseline (wells) before any tender strategy.

---

### Re-run

```bash
python3 mineral_pipeline.py screen --lat 30.048522 --lon -115.236173 --outdir maps/t2
python3 mineral_pipeline.py dem    --lat 30.048522 --lon -115.236173 --half-km 2 --outdir maps/t2
python3 mineral_pipeline.py spread --lat 30.048522 --lon -115.236173 --half-km 2 --outdir maps/t2
```

**Sources** (full list in main report Appendix B): SGM El Aguajito H11-B85 1:50,000 (2009) PDF — Alisitos units, La Turquesa zona mineralizada, 12 workings, Corbett model, structure; SGM sheet catalog (H11-B series); EOX s2cloudless (S2 2020, CC BY-NC-SA 4.0); USGS elevation-tiles-prod (10 m DEM); mindat turquoise locality "El Rosario, San Quintín Municipality"; Arqueología Mexicana, "Geología de la turquesa" (porphyry-copper belt, Baja California/Sonora); OSM (Cerro la Turquesa toponym, México 2 alignment).
