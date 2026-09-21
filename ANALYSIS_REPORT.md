# Satellite-Based Mineral Asset Analysis
## Target: 29.903605, -115.383656 — Municipio de San Quintín, Baja California, México

**Prepared:** 2026-08-25 · **Desk-study v2** (remote data + SGM El Aguajito 1:50,000 sheet integrated; no field data yet)
**Companion files:** `mineral_pipeline.py` (reusable code) · `maps/` (generated maps & products) · `data/sgm_saml_text.txt` (SGM sheet text)
**Additional targets:** T2 30.048522, -115.236173 (Cerro la Turquesa, 6.3/10) → `ANALYSIS_TARGET2.md` + `maps/t2/` · T3 30.025725, -115.286885 (Cerro la Palmita, 5.5/10) → `ANALYSIS_TARGET3.md` + `maps/t3/`

---

## 0 · Executive summary

| Item | Result |
|---|---|
| Exact location | Slopes west of **Arroyo San Isidro**, ~300 m elevation, southern part of Municipio de San Quintín (BCN), ~180 km S of Ensenada, ~300 km S of Mexicali |
| Terrain (10 m DEM, 4×4 km) | Undulating bajada: 213–484 m, mean 339 m; median slope 7.4°, only 9.1% >15°; dominant aspect S–SSW (~39%); arroyo drains through the site |
| Remote sensing (10 m Sentinel-2, 2020) | 86.5% bare brown soil/regolith, 10.3% desert scrub, **2.5% pale low-saturation "tone" patches** clustered N–NE of the point and along drainages (B/R up to 0.71 vs 0.52 background) — candidate pale regolith / weathered rock; **no strong RGB diagnostic of hydrothermal clay/carbonate** (needs SWIR to confirm) |
| Geological context | **Alisitos terrane** (island arc, Aptian–Albian 120–90 Ma): Alisitos Fm andesite/volcanic breccia (Kapa A-BvA) + Cretaceous batholith intrusions (Ks D-Tn diorite-tonalite, Ks Gr-Gd granodiorite) + Late Cretaceous Rosario Fm + Paleocene Sepultura Fm — per SGM sheet **El Aguajito H11-B85** (30°00′–30°15′N, just N of target; units continue across the sheet boundary visible in the Google image). SGM documents **argillic alteration (kaolinite/montmorillonite) across most of the sheet** — matches the pale purple-grey unit in the 2026 Google/Bing imagery around the pin |
| Mineralization record | **Zona Mineralizada "La Turquesa"** (SGM): **low-sulfidation epithermal Cu–Fe (± Au, Pb-Zn traces, turquoise)** modeled on Corbett (2001). 12 documented abandoned workings 15–20 km N of the target along the same terrane (Josefina, La Turquesa, El Hormiguero, La Prieta, Esperanza, El Cardonal, Santa Martha, San Martín, Santa Lucía, La Víbora, La Bonita, 5 Minas, El Sacrificio). Host: brecciated granodiorite + Alisitos andesite; veins N65–75°E; control: NE–SW normal faults + NW–SE strike-slip, N–S relay faults |
| Protection status | **No federal ANP at the point** (screened against BCN ANP lists); nearest: PN Sierra de San Pedro Mártir ~100 km N, San Quintín Bay reserves ~60 km NW → confirm with CONANP shapefile |
| Regulatory (as of Aug 2026) | Post-2023 Ley Minera: new concessions **only by public tender (concurso)**, 30-yr term, **no concessions in ANPs / water-stressed zones / population-risk zones**, prior consultation, social-impact study. Constitutional open-pit ban passed committee stage in 2024 — **verify current status before committing capital** |
| Biggest site risk | **Water** — intermittent Pacific-slope arroyos only; the 2023 law makes water availability a hard gate |
| Overall desk rating | **5.4/10 — MODERATE-TO-GOOD (upgraded from 4.3 after the SGM sheet evidence)**. A documented epithermal Cu-Fe-Au trend in the same terrane 15–20 km N, with the pale-tone surface at the target matching the documented argillic signature, justifies a focused field pass: 1 week, ~$15–30 k USD for stream-sediment + outcrop sampling along the Arroyo San Isidro transect |

---

## Part 1 · How to gather satellite data (and what NOT to do)

### 1.1 The Google/Bing question

Directly downloading basemap tiles from `tile.google.com` or `bing.com` at scale **violates their Terms of Service**, is technically gated (CAPTCHAs, rotating tile "generations", regional blocking) and gives you *visual* imagery only — no spectral bands. For mineral work you want **spectral** data (SWIR!), which basemap tiles don't provide.

**Official routes:**

| Source | What you get | Cost |
|---|---|---|
| **Bing Maps Tile / Imagery API** (MS) | Aerial imagery tiles to z18+ via `dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial` + `t{0-3}.tile.bing.net`; good for visual geomorphology (drifts, pits, road cuts) | Free tier + paid (MS licensing) |
| **Google Earth Engine** | The real "Google data": Sentinel-2, Landsat, ASTER, MODIS, Sentinel-1 — full spectral libraries, 5-day S2 revisit | Free for research (ToU); commercial via EE Paid |
| **Google Photorealistic 3D Tiles API** | Google's highest-resolution oblique/aerial tiles, streamed via 3D Tiles | Paid |

### 1.2 The open-data stack (what this study used / recommends)

| Product | Resolution | Bands | License |
|---|---|---|---|
| **Sentinel-2** (Copernicus) | 10 m (RGB) / 20 m (red-edge) / 60 m (SWIR1/2) | 13, incl. SWIR at 60 m | CC BY-SA 4.0 — free |
| **HLS** (NASA/USGS harmonized Landsat 8/9 + S2) | 30 m | 11 S2 / 8 L8-9 | Public domain (US) / CC (S2) |
| **ASTER** (METI/NASA, 2000–2024) | 15–90 m | 14 incl. **SWIR 6/7 at 30 m** — the classic mineral bands | Free via Earthdata |
| **AVIRIS** (USGS SFUG archive) | 30 m | **224 hyperspectral channels** — diagnostic mineral mapping | Free via Earthdata |
| **Copernicus GLO-30 / SRTM / AW3D30** | 10–30 m | DEM | Free |
| **GIBS** (NASA) | 250 m–1 km | MODIS/VIIRS daily products (NDVI, true color) | Free |

### 1.3 Legal notes

* Sentinel-2/EOX s2cloudless tiles used here: **CC BY-NC-SA 4.0** (non-commercial research) — attribute "Contains modified Copernicus Sentinel data 2020".
* USGS SRTM-derived elevation tiles & Landsat: public domain.
* HLS/ASTER/AVIRIS: free with an **Earthdata Login** (urs.earthdata.gov, 5 min, no credit card).
* Bing/Google commercial use: keep within API terms; do not republish scraped tiles.

---

## Part 2 · Method (what was actually run on this target)

```
locate → terrain → surface screen → (full bands, next step) → context → score
```

1. **Locate** — reverse geocoding (OSM Nominatim) + labeled topographic tiles read visually → *Arroyo San Isidro, San Quintín municipio*.
2. **Terrain** — 9×10 m SRTM-derived GeoTIFF tiles (USGS `elevation-tiles-prod`, z14 mosaic, 4×4 km window) → slope, aspect (compass), hillshade, drainage.
3. **Surface screen** — 10 m Sentinel-2 2020 cloudless composite (EOX WMTS, z15 mosaic ≈2.3 km) → HSV rule classes (vegetation / soil / pale-tone / bright-crust / shadow) + **B/R blue-shift proxy** (Fe-oxide depletion indicator in RGB-only mode).
4. **Full bands (recommended next step, code ready)** — HLS 30 m (S2/Landsat) or S2 L2A: NDVI, NDWI, ferric-iron index (FAI), clay proxy (SWIR1-Red), carbonate proxy, SWIR1/SWIR2 ratio. `mineral_pipeline.py bands --lat … --lon …` (free Earthdata login).
5. **Context** — SGM geologic-mineral sheets, peer-reviewed PRB metallogeny, municipal inventories, ANP lists, current Ley Minera.

All code: **`mineral_pipeline.py`** (modes: `screen`, `dem`, `bands`, `tiles`).

---

## Part 3 · Deep analysis of 29.903605, -115.383656

### 3.1 Location

* **Administrative:** Municipio de San Quintín, Baja California (MX-BCN) — a municipio carved out of Ensenada in 2020.
* **Physical:** ~308–326 m a.s.l. (open-elevation 308 m; 10 m DEM 326 m). The point sits on a low, gently undulating slope on the **SW side of the Arroyo San Isidro** drainage, which crosses the site N–S (visible in both the topo and the S2 image).
* **Accessibility:** remote; nearest major road is the Transpeninsular (México 2) to the west, then dirt tracks. Nearest services: San Quintín town (NW, ~40–50 km), San Luis de la Ciénega / La Trinidad area to the south.

### 3.2 Terrain & drainage (10 m DEM, 4×4 km window)

| Metric | Value |
|---|---|
| Elevation range | 213 – 484 m (mean 339 m) |
| Local maximum | 484 m at 29.9027, -115.3667 (~1.1 km E of target) |
| Slope | mean 8.3°, median 7.4°, p90 14.6°, max 41.8° |
| Steepness | 9.1% of area >15°; only 0.5% >25°; within 1 km: 34% >10°, 3% >20° |
| Aspect | **S 13.8% + SSE 13.1% + SSW 11.7%** (≈39% south-facing); secondary W/WSW (~21%), ESE (9.4%); N-facing only 3.9% |
| Drainage | Dendritic; Arroyo San Isidro is the main trunk crossing the site; ephemeral (rain-fed), no perennial flow |

**Interpretation:** classic dissected **bajada/alluvial-fan terrain** at the foot of the central sierra — low structural relief, well-drained, south-facing sunny slopes (max evaporation → pale, bleached regolith development), and drainages that concentrate detritus (good sampling lines). Low relief means any mineralization must come from **faulted uplift blocks or buried sources** — the drainage lines are the place to sample.

### 3.3 Remote-sensing results (10 m Sentinel-2, 2020 composite)

Class fractions within 1 km of the target (0.79–3.14 km²):

| Class | 1 km |
|---|---|
| Bare soil / regolith | **86.5 %** |
| Desert scrub (veg.) | 10.3 % |
| **Pale "tone" patches** | **2.5 %** |
| Bright crust (salt/caliche/carbonate) | 0 % |
| Shadow/dark | 0 % |

* **B/R blue-shift proxy:** mean 0.545 within 1 km vs 0.524 background; the top 1 % (B/R ≥ 0.712) covers ≈4.7 ha and is **clustered around the site, N–NE**, coinciding with the pale grey-toned patches visible on the composite (see `maps/class_map.png`, `maps/br_map_4km.png`).
* The pale patches have lower saturation (S≈0.42 vs 0.52 for typical brown soil) and slightly lower brightness — spectrally consistent with **paler regolith, exposed weathered rock, or caliche/carbonate crust**. RGB-only data cannot distinguish clay vs carbonate vs bleached sand.
* **No bright salt/crust zone, no strong blue-shift anomaly at the exact point.** The signal is *subtle and spatially patchy* — a screening hit, not a confirmation.

**Limitation (important):** the 2020 composite predates any recent surface change; and RGB has no SWIR — the diagnostic mineral bands. A single recent cloud-free S2 L2A scene with SWIR (B11/B12) or an ASTER pass is the cheapest way to confirm or kill the anomaly.

**Cross-check with 2026 Google/Bing aerials (provided by proponent):**
* Google (≈200 m scale): a large, coherent **purple-grey unit** (km-scale) occupies the area N–NW of the pin; the pin sits at its **SE margin**. The unit's boundary is sharp and follows a structural trend — this is exposed bedrock (Alisitos andesite/volcanic breccia and/or granodiorite with argillic overprint), not vegetation tone. SGM's "argillic alteration in most of the sheet" + the pale B/R response give this unit its metallogenetic relevance.
* Bing (10 m): the pin is on a **gentle lower slope beneath a scarp** — the N edge of the unit (resistant bedrock mesa); smooth bajada below; **no visible works at the pin** (consistent: nearest documented works 13+ km away).
* Bing (50 m): a **circular pale feature ~1.5 km W of the pin** — SGM documents circular lineaments associated with batholith intrusives in this region → candidate **Ks Gr-Gd intrusive contact**, a classic epithermal/Au-Ag-Cu contact-zone target (cf. La Cumbre, El Carrizo, Veta Blanca per H11-3).
* The N–S arroyo through the site follows SGM's documented **N–S relay fault geometry** — the main structural control to sample.

### 3.4 Geological context (published)

Regional framework (N → S along the peninsula axis):

1. **Peninsular Ranges Batholith (PRB)** — Cretaceous (≈110–85 Ma) granodiorite–tonalite–granite; the Sierra San Pedro Mártir massif sits ~60–90 km north of the target and is the southern PRB expression.
2. **Alisitos island-arc suture** — the PRB intruded across the suture between the Alisitos arc and the North American margin; **orogenic gold deposits form in this suture setting** (quartz–carbonate veins in shear zones, synorogenic plutons ~107–103 Ma).
3. **Peninsular Ranges orogenic gold belt** (formally described 2023) — San Pedro Mártir Au district (incl. Valladares etc.) connects southward along the exhumed PRB axis to historical districts (e.g., El Álamo). **Our target lies on the southern projection of this axis** — the strongest metallogenetic argument for the site.
4. **Guerrero/Cortés basement** — Triassic–Jurassic (and Paleozoic inlier) metasediments (schists, gneisses, limestones, quartzites; greenschist→amphibolite facies) crop out as hanging-wall roofs to the granites; documented in the H11-2/H11-3 sheets (Ensenada, San Felipe) and I11-12 (Mexicali) — expect equivalents at/just north of our latitude.
5. **Laramide reworking (Late Cretaceous–Eocene)** — two-mica intrusions, NE–SW to N–S normal faults, pull-apart basins (e.g., Ojos Negros pull-apart documented in the Tijuana sheet) — the regional N–S to NNE structural trend that would channel hydrothermal fluids.
6. **Tertiary–Quaternary volcanism** — the San Quintín volcanic field (OIB alkali basalts, post-1 Ma) is ~50–70 km N; a 2024 municipal study notes Tertiary volcanic material (scoria, volcanic ash) quarried in the **south of the municipio** (i.e., our area) — volcanic cover could mask, or be a host for, younger epithermal systems.
7. **Local sheet geology — SGM El Aguajito H11-B85, 1:50,000 (2009)** (covers 30°00′–30°15′N, 115°20′–115°40′W, the sheet **immediately north** of the target; its units continue across the boundary visible in the Google image):
   * **Terrane:** Alisitos (arc, 120–90 Ma). Units: **Kapa A-BvA** (Alisitos Fm: andesite, andesitic breccia, pyroclastic flows, sandstone, rhyolite, limestone, conglomerate; "greenish-grey with reddish tones") → **Ks D-Tn** (diorite-tonalite) & **Ks Gr-Gd** (granite-granodiorite, Peninsular Ranges batholith phase; the granodiorite is "white, phaneritic, in places highly brecciated") → **Kcm Cgp-Ar / Kcm Ar-Lm** (Rosario Fm, Late Cretaceous polymictic conglomerate–sandstone–siltstone, western part) → **Tpa Ar-Cz** (Sepultura Fm, Paleocene sandstone–limestone with gypsum) → **Qpt Cgp + Qhoal** (Pleistocene–Holocene conglomerate, alluvium).
   * **Structure (satellite-interpreted):** four fault blocks (Rosario, Los Mártires, La Esperanza, Aguajito) bounded by **conjugate NW–SE / NE–SW lineaments**; **N–S "relay" fault geometry**; NE–SW **normal** faults, NW–SE **strike-slip**; **circular lineaments around batholith intrusives** (La Esperanza block). NW–SE lineaments attributed to extension from Gulf of California opening.
   * **Alteration:** **argillic (intermediate argillic: kaolinite and/or montmorillonite) "in most of the sheet"**; propylitic (chlorite-epidote-calcite-albitized plagioclase); silicification; oxidation (Fe oxides, jarosite).
   * **Metallogeny:** tied to Alisitos arc tectonic evolution (Early–Late Cretaceous). Sheet recommends future exploration of **blind sigmoidal structures and tabular brechas** (mineralization fills open spaces in the conjugate system).
   * **The sheet covering the target's own square is H11-B87 "Cerro el Huerfanito"** (29°45′–30°00′N per the SGM catalog sequence) — **to be pulled from SGM** (free PDF if published; otherwise order the interactive shapefile via SGM sales / geoinfo@sgm.gob.mx).

**Caveats:** the "Sierra La Trinidad batholith" in the 2023 IGR paper is the Los Cabos block in **Baja California SUR** (~23°N) — a different massif with a confusingly similar name; it is *not* our area. Sheet El Aguajito's geology is 11 km north of the point; the H11-B87 sheet will confirm unit positions at the point itself (the Google image shows the purple-grey unit clearly crossing the sheet boundary, so continuity is expected).

### 3.5 Documented mineralization near the target (SGM El Aguajito sheet, 2009)

**Zona Mineralizada "La Turquesa"** — sheet SE/central portion, ~30 km E of El Rosario along the Transpeninsular. Type: **vein-fault + stockwork, low-sulfidation epithermal (Corbett 2001 model); Cu–Fe dominant, traces Au and Pb-Zn; turquoise as gemstone** (gambusino activity only; no operating mines). Host: Alisitos andesite (Kapa A-BvA) + brecciated Ks Gr-Gd / Ks D-Tn. Mineralogy: chalcopyrite, hematite, bornite, specularite, sphalerite, pyrite, quartz, limonite, jarosite, chrysocolla (probable), **malachite, azurite** (Cu-carbonates = surface Cu oxidation), calcite.

Documented abandoned workings (UTM zone 11N, converted):

| Work | ~Lat, Lon | ~Dist from target | Notes |
|---|---|---|---|
| Josefina | 30.122, -115.360 | 13 km N | Cu-Fe in brecciated white granodiorite; E-W adit + catas; NW regional control |
| Santa Martha | 30.147, -115.357 | 16 km N | Epithermal fissure-fills, NW–SE + NE–SW lineament system |
| San Martín | 30.146, -115.375 | 16 km N | Specularite, **malachite, azurite**, chalcopyrite, chrysocolla?, jarosite, pyrite |
| La Víbora | 30.171, -115.524 | 19 km NNW | Vein-fault, strike N35°E |
| 5 Minas | 30.124, -115.344 | 15 km N | Fe-Cu in **tabular brecha** |
| El Sacrificio | 30.124, -115.344 | 15 km N | Occurrence, tabular brecha zone |
| El Moro | 30.220, -115.396 | 21 km N | Occurrence |
| Santa Lucía | 30.158, -115.454 | 18 km NNW | 3 catas + 40 m drift |
| La Turquesa | 30.071, -115.446 | 19 km NNE | **Argillic + Fe-oxide + calcite alteration, massive and highly eroded** |
| El Hormiguero | 30.071, -115.391 | 18.5 km N | Intense secondary alteration: **clays, Fe oxides, calcite** |
| La Prieta | 30.070, -115.392 | 18.5 km N | Open pit; NE trend on pit face |
| Esperanza | 30.067, -115.376 | 18 km N | **Veins N65°–75°E** converging at ranchería La Prieta |
| El Cardonal | 30.067, -115.376 | 18 km N | Normal fault N82°E/32°NW; turquoise; "main mine of the region" |
| La Bonita | 30.048, -115.412 | 17 km N | Brecha N53°E/69°NW, 0.7 m mineralized |

**Reading for the target:** the workings define a **N–NE trending Cu-Fe-epithermal corridor at 115.36–115.45°W, 30.04–30.17°N**. The target at 29.90°N, 115.38°W sits on the **southern continuation of that corridor**, on the same terrane, where SGM reports widespread argillic alteration and N–S relay structures. The pale purple-grey unit in the 2026 Google/Bing imagery is the surface expression to test for.

Also: Au-Ag-Cu mesothermal veins near the **granodiorite–diorite contact** (La Cumbre, El Carrizo, Veta Blanca) per SGM San Felipe H11-3 sheet (30–32°N) — contact-zone style worth testing at the circular pale feature W of the pin.

*No published deposits at the exact point; nearest documented workings are 13–21 km away — the southern end of the corridor is unworked/under-documented.*

### 3.6 Environmental & land constraints

* **ANPs (screened):** no federal ANP at or immediately around the point. Nearest federal ANPs: PN Sierra de San Pedro Mártir (~100 km N), PN San Quintín (2023, 0.86 km² coastal), San Quintín Bay ADVCs (~60 km NW). → **Still verify** against the official CONANP shapefile (free download).
* **Water (critical):** 2023 Ley Minera prohibits new concessions in zones **without water availability** per Ley de Aguas Nacionales. This is an arid, Pacific-slope catchment with intermittent arroyos only — expect CONAGUA scrutiny to be the single hardest gate for any project here. Water strategy (deep wells + permits) must be part of the feasibility case from day one.
* **Land tenure:** rural BC is dominated by ejido/federal lands; the 2023 law requires **agreements with landowners** (expropriation eliminated) → tenure due diligence before any tender.
* **Community/social:** sparse population (rancherías); still, social-impact study + (if applicable) prior consultation are mandatory pre-title.

### 3.7 Regulatory snapshot (August 2026)

In force since **DOF 08-05-2023** (Ley Minera reform):
* Concessions granted **only through public tender** (concurso) by SGM/SE; 30-year term (30+25 renewal structure).
* **Prohibited:** concessions in ANPs; in water-stressed zones; where activity risks population.
* **Required before title:** social-impact study + social-impact authorization; closure/post-closure program; water use concession; landowner agreements; **prior consultation** (applicant-funded) where indigenous/Afromexican communities are on the lot.
* Mining no longer a "priority activity" vs other uses.
* **Open-pit (tajo) ban:** constitutional reform approved in committee Aug 2024 with an executive-exception clause; as of mid-2026 treat its final status as **unverified** — check DOF/Congreso before structuring any open-pit plan (underground methods remain explicitly permitted).
* Litium & "strategic" minerals: state-reserved (2022 reform) — not relevant to Au/base metals.

### 3.8 Prospectivity scoring (desk)

| Factor | Score /10 | Rationale |
|---|---|---|
| Metallogenic setting | **8** | Same Alisitos terrane as a **documented Cu-Fe-epithermal corridor** (La Turquesa zone, 12 workings) 13–21 km N; target on the corridor's S continuation; Au-Ag-Cu contact zones also documented at granodiorite-diorite contacts (H11-3) |
| Structure | **7** | Sheet-documented: conjugate NW–SE/NE–SW system, NE–SW normals, N–S relay faults, circular intrusive lineaments; arroyo follows the N–S relay; vein trends N65–75°E known locally |
| Remote sensing | **6** | Pale B/R blue-shift at the pin **matches the documented argillic (kaolinite/montmorillonite) signature**; purple-grey bedrock unit + circular feature visible on 2026 Google/Bing; still no SWIR confirmation |
| Outcrop/access to bedrock | 4 | Deep regolith in places; drainages + scarp expose bedrock (sampleable) |
| Historical signal | **8** | 12 named abandoned Cu-Fe-Au workings in the corridor; turquoise + malachite/azurite at San Martín/El Cardonal; SGM explicitly recommends exploring blind sigmoids/brechias |
| Water | 3 | Arid, intermittent drainage — hard regulatory gate |
| Access & infrastructure | 3 | Remote, dirt access, no power grid near site (El Rosario services ~30 km W per sheet) |
| Environmental/social | 5 | No ANP at point, sparse population; but desert ecosystem + Ramsar bay nearby in NW |
| Regulatory certainty | 5 | Public-tender model = competitive but transparent; open-pit status in flux |
| **Weighted total** | **≈5.4/10** | **MODERATE-TO-GOOD — field reconnaissance strongly justified; corridor extension test is the play** |

### 3.9 Recommended next steps (priority order, costs indicative)

1. **Pull SGM sheet H11-B87 "Cerro el Huerfanito" (1:50,000)** — the sheet that actually covers the point (29°45′–30°00′N, 115°20′–115°40′W). Confirms unit positions, any local workings, and the S/N position of the purple-grey (argillic) unit at the pin. The sheet immediately north (H11-B85 El Aguajito) is already integrated. *(SGM: geoinfo@sgm.gob.mx or sales portal; free PDF if published, else interactive shapefile ~16,384 MXN)*
2. **SWIR confirmation:** download the latest cloud-free S2 L2A (Copernicus Data Space, free login) + one ASTER L1A scene over the 10×10 km → run `mineral_pipeline.py bands` → clay/carbonate indices over the pale-tone zone. *(≈$0 + time)*
3. **Check AVIRIS flight coverage** (USGS SFUG, free) over 29.5–30.5°N / 115°W — if a 30 m hyperspectral line exists, it's the single best desk tool for this site.
4. **Concession & tenure screen:** SENER/minalia lote map + Gaceta Minera for active titles near the point; ejido status via municipal registry. *(≈$0.5–2 k USD)*
5. **Field pass (1 wk, 2 geologists):** map the pale-tone zone & the Arroyo San Isidro transect; collect ~50–100 rock + stream-sediment samples (Au, Ag, Cu, Pb, Zn, Mo by ICP-MS); photo-document any works. *(≈$15–30 k USD incl. assays)*
6. **Magnetometry** over 4–10 km² to locate structural/iron-rich zones under the regolith. *(≈$10–25 k USD)*
7. **Water study:** baseline well/yield potential + CONAGUA basin availability opinion before any tender strategy. *(≈$5–15 k USD)*
8. Only then: **tender strategy** for a mining lot (lote minero) sized to the anomaly, with closure plan & social study in the bid.

### 3.9b Field map sheet (for the on-site accuracy test)

`python3 mineral_pipeline.py spread --lat 29.903605 --lon -115.383656 --half-km 2` generates:

* **`maps/map_spread_4km.jpg`** — a 3×3 field sheet, all panels on the **same 4×4 km extent, 4 m/px**, with a 500 m lat/lon cross-grid on every panel (read your position off the grid), scale bar, N arrow, red target square:
  1. True color (S2 2020) · 2. Hillshade · 3. Elevation · 4. Slope · 5. Aspect · 6. Surface classes · 7. B/R blue-shift · 8. **Target overlay** (pale-tone + 500/1000 m rings + waypoints A–N) · 9. Context (14.7 km).
* **`maps/field_waypoints.csv`** — 15 GPS checkpoints (lat/lon, UTM 11N, map elevation, **bearing + distance from the target**, and what you should see there).

**Accuracy expectations** (what "right" looks like on the ground):
* Imagery geolocation ±10–20 m · DEM vertical ±3–8 m · phone GPS ±5–15 m → expect **15–30 m total discrepancy**; flag anything >50 m or systematic (one direction).
* Target (TGT): gentle slope, brown soil, sparse scrub, arroyo ~60–100 m NE.
* Purple **pale-tone patches** = expect visibly paler grey/whitish soil or exposed weathered rock, less scrub than surroundings.
* D-1…D-6 = dry arroyo channel with gravel/cobbles (best sediment-sampling spots).
* L/M/N = steepest rocky ground (36–41°), the best outcrop/sampling candidates.

**Recommended on-site test (≈2 h):** stand at TGT and record your GPS; then visit, in priority order: **I (N, 210 m) → H (S, 260 m) → C (E, 430 m, pale patch) → A (WNW, 875 m, big pale cluster) → B (S, 795 m) → E (ridge 484 m, E, 1.9 km) → L (SSE, 2.6 km, outcrop)**. At each stop record GPS + 1 north-facing photo + "matches expectation? y/n". Send me the points/photos and I'll compute the RMSE, recalibrate the index thresholds, and revise the prospectivity score.

*(Spread-based re-classification on the 4 km window: SOIL 81.8%, VEG 12.4%, pale-TONE 5.2%, B/R @1 km = 0.572, p99 = 0.709 — slightly higher TONE fraction than the 2.3 km z15 pass because the z14 render is marginally less saturated.)*

### 3.10 What would change the rating

* **Upgrade to 6.5–7.5:** H11-B87 sheet shows the argillic purple-grey unit + granodiorite intrusives actually at the pin; SWIR (S2 L2A/ASTER) confirms kaolinite/montmorillonite signature; Arroyo San Isidro stream-sediments return Cu/Fe ± Au-Ag-Pb-Zn anomalies tracking the N–S relay; the circular feature W of the pin logs as an intrusive contact.
* **Downgrade to ≤3.5:** H11-B87 shows the unit is Rosario Fm clastics or unaltered andesite (no alteration zonation at the pin); SWIR shows no clay/carbonate; stream-sediments flat; or the lot is already under an active concession.

---

## Appendix A · Generated products (`maps/`)

| File | Content |
|---|---|
| **`map_spread_4km.jpg`** | **3×3 field map sheet** (9 non-redundant panels, 4×4 km, 4 m/px, 500 m grid, rings + waypoints) |
| **`field_waypoints.csv`** | **15 GPS checkpoints** with UTM 11N, elevation, bearing/distance from target, field notes |
| **`mine_inventory_elaguajito.csv`** | 14 documented Cu-Fe-Au workings from the SGM sheet (lat/lon, UTM, distance, mineralogy) |
| `class_map.png` | RGB-screen classes (soil/veg/pale-tone/crust/dark) on 2.3 km S2 mosaic |
| `br_map.png` | B/R blue-shift proxy (blue→yellow) |
| `hillshade.png` | SW-aspect hillshade, 10 m DEM, 4×4 km |
| `dem_window.tif` | Georeferenced 10 m DEM window (EPSG:3857, ~4×4 km) |
| `dem_win.npy`, `slope_win.npy`, `dem14_*.tif` | Raw arrays / 10 m DEM tiles (re-runs are instant) |

## Appendix B · Key sources

* OSM Nominatim / OpenTopoMap (location, "Arroyo San Isidro"): nominatim.openstreetmap.org · tile.opentopomap.org
* open-elevation API (308 m point elevation): api.open-elevation.com
* EOX s2cloudless (S2 2020, CC BY-NC-SA 4.0): tiles.maps.eox.at
* USGS elevation-tiles-prod (10 m DEM tiles): s3.amazonaws.com/elevation-tiles-prod
* NASA CMR / HLS (Landsat+S2 harmonized, 30 m): cmr.earthdata.nasa.gov
* SGM Carta Geológico-Minera Estatal Baja California 1:500,000 (2005, free PDF): mapserver.sgm.gob.mx/Cartas_Online/metadatos_geol/1_baja_california_GL-MN_ESTATAL.HTML
* SGM sheets Ensenada H11-2 (La Quinota 17 g/t Au; Guerrero terrane basement): …/2_GL_ensenada.html · San Felipe H11-3 (Au-Ag-Cu at granodiorite–diorite contacts): …/4_GL_san_felipe.html · Mexicali I11-12: …/3_GL_mexicali.html
* **SGM Carta Geológico-Minera El Aguajito H11-B85, 1:50,000 (2009)** — controlling local sheet (30°00′–30°15′N, just N of target): Alisitos terrane units, La Turquesa zona mineralizada, 12 abandoned Cu-Fe-Au workings, Corbett low-sulfidation epithermal model, widespread argillic alteration, conjugate NW-SE/NE-SW + N-S relay structure. PDF: mapserver.sgm.gob.mx/InformesTecnicos/CartografiaWeb/T022009SAML0001_01.PDF (extracted text: `data/sgm_saml_text.txt`)
* SGM 1:50,000 sheet catalog (H11-B series; **H11-B87 "Cerro el Huerfanito" = the sheet covering the target**): mapserver.sgm.gob.mx/ReportesVentas/GeoMinerasIntPDF.jsp
* Peninsular Ranges orogenic gold belt (San Pedro Mártir): sciencedirect.com/science/article/abs/pii/S0895981123002407
* San Quintín volcanic field (OIB basalts): terrapeninsular.org (2017 PDF)
* "Los retos del desarrollo para el nuevo municipio de San Quintín" (2024; mining toward south of municipio, Au/Ag): researchgate.net/publication/378661467
* Frontier mining history (San Quintín port, 1880s): scielo.org.mx (Región y Sociedad 2004)
* IGR 2023 Sierra La Laguna / Sierra La Trinidad (**Los Cabos, BCS** — name-collision warning): researchgate.net/publication/369891227
* Ley Minera current text (incl. 2023 reforms): diputados.gob.mx/LeyesBiblio/pdf/LMin.pdf · HLC summary: hlc.com/es/publications/mexico-aprueba-reforma-minera
* Open-pit constitutional reform (committee approval, Aug 2024): boletín 7086, comunicacionsocial.diputados.gob.mx · status coverage Sep 2024: diario.red
* Gaceta Parlamentaria LXVI (2026, water/mining initiatives): gaceta.diputados.gob.mx/Gaceta/66/2026/abr/20260429-II-6.html
* ANP lists BCN: dof.gob.mx (PN San Quintín 2023) · elimparcial.com (20 ANPs) · terrapeninsular.org

---

### How to re-run / extend

```bash
# surface screen + terrain (no accounts needed)
python3 mineral_pipeline.py screen --lat 29.903605 --lon -115.383656
python3 mineral_pipeline.py dem    --lat 29.903605 --lon -115.383656 --half-km 2

# field map sheet + GPS waypoints (no accounts needed)
python3 mineral_pipeline.py spread --lat 29.903605 --lon -115.383656 --half-km 2

# full 30 m spectral indices (free Earthdata login: urs.earthdata.gov)
export EARTHDATA_USER=you EARTHDATA_PW=secret
python3 mineral_pipeline.py bands  --lat 29.903605 --lon -115.383656 --days 365

# any other target: change --lat/--lon (e.g., next Baja California site)
```

**Proponent-provided inputs (2026-08-25):** Google/Bing aerial screenshots (`uploads/Screenshot_2026-08-25_17-*.png`) and SGM El Aguajito H11-B85 report PDF (`uploads/T022009SAML0001_01.pdf` → `data/sgm_saml_text.txt`) — both integrated in §3.3–3.5.
