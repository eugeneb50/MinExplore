#!/usr/bin/env python3
"""Canonical field-pin + mine-inventory dataset builder (Workstreams 6+7).

Single source of truth for IDs and provenance. Writes:
  maps/PIN_POINTS.csv, maps/PIN_POINTS.geojson,
  site/maps/PIN_POINTS.csv, site/maps/PIN_POINTS.geojson,
  maps/mine_inventory_elaguajito.csv/.geojson (+ site/maps/ copies),
  sample_data/ (DataKit subset).

ID history (v1 -> v2, see schemas/datadictionary.md):
  TGT (x4 sheets) -> T1-TGT, T2-TGT, T2i-TGT, T3-TGT
  T2-1,T2-2,T2-4,T2-5,T2-6,T2-7 (T2 PIN MAP) -> T2-OVERVIEW-01..06
  T2-1,T2-2,T2-6 (T2 DETAIL) -> T2-DETAIL-01..03
Stdlib only.
"""
import csv
import json
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.export import records_to_csv, records_to_geojson  # noqa: E402
from src.scores import PIPELINE_VERSION  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATED = "2026-08-25"
ESI = "Esri World Imagery tile service (research use)"
S2V = "EOX Sentinel-2 2020 cloudless viewing composite (CC BY-NC-SA 4.0)"
SGM = "SGM Carta Geologico-Minera El Aguajito H11-B85 1:50,000 (2009)"
MAP_LIC = "CC BY-NC-SA 4.0 (rendering); underlying imagery per provider terms"


def P(rid, tid, lat, lon, ftype, label, area, note, src, page, date,
      acc, method, conf):
    return {"record_id": rid, "target_id": tid, "latitude": lat, "longitude": lon,
            "crs": "EPSG:4326", "feature_type": ftype, "source": src,
            "source_page": page, "source_date": date, "coordinate_accuracy_m": acc,
            "derivation_method": method, "confidence": conf, "field_action": note,
            "license": MAP_LIC, "created_at": CREATED,
            "pipeline_version": PIPELINE_VERSION, "label": label, "area": area}


DESK = "desk pick on sub-meter base layer for field check"
RGBH = "RGB visual-screening heuristic pick (unvalidated; needs field + spectral validation)"

PINS = [
    # T1 — Arroyo San Isidro (Esri z17 rendered 1.03 m/px)
    P("T1-1", "T1", 29.906097, -115.390962, "pale", "P1 WNW pale cluster", "T1 PIN MAP",
      "outcrop check + rock chips; look for alteration colour zoning", S2V + " + " + ESI, "t1_pins", "2020", "20", RGBH, "Low"),
    P("T1-2", "T1", 29.897790, -115.381181, "pale", "P2 S pale patch", "T1 PIN MAP",
      "map extent; chips; gully walls", S2V + " + " + ESI, "t1_pins", "2020", "20", RGBH, "Low"),
    P("T1-3", "T1", 29.904306, -115.379883, "pale", "P3 E pale patch", "T1 PIN MAP",
      "map extent; chips", S2V + " + " + ESI, "t1_pins", "2020", "20", RGBH, "Low"),
    P("T1-5", "T1", 29.905147, -115.384249, "sed", "P4 arroyo N", "T1 PIN MAP",
      "sediment pair (2 bags) - N relay", ESI, "t1_pins", "2024-26", "20", DESK, "Medium"),
    P("T1-6", "T1", 29.902032, -115.385183, "sed", "P5 arroyo S", "T1 PIN MAP",
      "sediment pair - S relay", ESI, "t1_pins", "2024-26", "20", DESK, "Medium"),
    P("T1-TGT", "T1", 29.903605, -115.383656, "target", "TARGET", "T1 PIN MAP",
      "reference point; verify mapped surface/terrain match on site", SGM, "T1 target", "2009", "20", "desk target pick cross-referenced to SGM sheet", "Medium"),
    # T2 overview (Esri z17 rendered 1.03 m/px)
    P("T2-OVERVIEW-01", "T2", 30.050200, -115.246600, "pale", "P1 pale mass CENTER", "T2 PIN MAP",
      "map the mass; identify rock; 100 m chip grid; hunt blue-green", S2V + " + " + ESI, "t2_pins", "2020", "20", RGBH, "Low"),
    P("T2-OVERVIEW-02", "T2", 30.049000, -115.242800, "pale", "P2 mass E edge", "T2 PIN MAP",
      "alteration front - sample both sides of contact", S2V + " + " + ESI, "t2_pins", "2020", "20", RGBH, "Low"),
    P("T2-OVERVIEW-03", "T2", 30.044500, -115.236000, "struct", "P3 band @ arroyo", "T2 PIN MAP",
      "ROAD or FAULT SCARP? measure, sample gouge", ESI, "t2_pins", "2024-26", "20", "lineament traced on sub-meter base layer; road vs scarp unresolved", "Low"),
    P("T2-OVERVIEW-04", "T2", 30.040500, -115.226500, "struct", "P4 band 1.5 km E", "T2 PIN MAP",
      "trace lineament; look for 2nd scarp", ESI, "t2_pins", "2024-26", "20", "lineament traced on sub-meter base layer; requires field validation", "Low"),
    P("T2-OVERVIEW-05", "T2", 30.044000, -115.247000, "sed", "P5 arroyo below mass", "T2 PIN MAP",
      "sediment pair - mass catchment", ESI, "t2_pins", "2024-26", "20", DESK, "Medium"),
    P("T2-OVERVIEW-06", "T2", 30.044000, -115.233000, "out", "P6 summit 740 m", "T2 PIN MAP",
      "Cerro la Turquesa: lithology + structural grain", ESI, "t2_pins", "2024-26", "20", DESK, "Medium"),
    P("T2-TGT", "T2", 30.048522, -115.236173, "target", "TARGET", "T2 PIN MAP",
      "reference point; turquoise-mining toponym at site", SGM, "T2 target", "2009", "20", "desk target pick cross-referenced to SGM sheet", "Medium"),
    # T2 detail inset (Esri z18 rendered 0.52 m/px; same physical pins re-plotted)
    P("T2-DETAIL-01", "T2", 30.050200, -115.246600, "pale", "P1 mass center", "T2 DETAIL",
      "outcrop + chips", ESI, "t2_mass_inset_z18", "2024-26", "20", "detail-sheet re-plot of T2-OVERVIEW-01 at z18", "Low"),
    P("T2-DETAIL-02", "T2", 30.049000, -115.242800, "pale", "P2 E edge", "T2 DETAIL",
      "alteration front", ESI, "t2_mass_inset_z18", "2024-26", "20", "detail-sheet re-plot of T2-OVERVIEW-02 at z18", "Low"),
    P("T2-DETAIL-03", "T2", 30.045500, -115.248500, "sed", "P5 gully mouth", "T2 DETAIL",
      "sediment - fresh wall sample", ESI, "t2_mass_inset_z18", "2024-26", "20", DESK, "Medium"),
    P("T2i-TGT", "T2", 30.048522, -115.236173, "target", "TARGET", "T2 DETAIL",
      "reference point (off-sheet north of inset)", SGM, "T2 target", "2009", "20", "desk target pick cross-referenced to SGM sheet", "Medium"),
    # T3 (Esri z17 rendered 1.03 m/px)
    P("T3-2", "T3", 30.017216, -115.271919, "out", "P2 ridge high 808 m", "T3 PIN MAP",
      "Cerro la Palmita: outcrop map + grain", ESI, "t3_pins", "2024-26", "20", DESK, "Medium"),
    P("T3-3", "T3", 30.022132, -115.293371, "out", "P3 steepest 36 deg", "T3 PIN MAP",
      "857 m W - first bedrock, sample + structure", ESI, "t3_pins", "2024-26", "20", "steepest-slope pick from 10 m working grid (SRTM ~30 m native)", "Medium"),
    P("T3-4", "T3", 30.017932, -115.285430, "sed", "P4 arroyo S", "T3 PIN MAP",
      "sediment pair", ESI, "t3_pins", "2024-26", "20", DESK, "Medium"),
    P("T3-5", "T3", 30.024154, -115.289239, "sed", "P5 arroyo W", "T3 PIN MAP",
      "sediment pair", ESI, "t3_pins", "2024-26", "20", DESK, "Medium"),
    P("T3-6", "T3", 30.030500, -115.274500, "out", "P6 MEX 2 cut-bank", "T3 PIN MAP",
      "road cut NE - free outcrops + any old works", ESI, "t3_pins", "2024-26", "20", DESK, "Medium"),
    P("T3-TGT", "T3", 30.025725, -115.286885, "target", "TARGET", "T3 PIN MAP",
      "reference point; corridor ridge high ground", SGM, "T3 target", "2009", "20", "desk target pick cross-referenced to SGM sheet", "Medium"),
    # Zone A — El Cardonal / La Prieta / Esperanza (Esri z17)
    P("A-1", "ZA", 30.067000, -115.376000, "mine", "A1 El Cardonal", "ZONE A",
      "TURQUOISE documented - walk N82E fault scarp; sample all blue-green", SGM, "El Cardonal sheet record", "2009", "500", "SGM inventory digitization; ~500 m accuracy from 1:50,000", "Medium"),
    P("A-2", "ZA", 30.070000, -115.392000, "mine", "A2 La Prieta pit", "ZONE A",
      "walk pit walls - fresh oxidized Cu surfaces", SGM, "La Prieta sheet record", "2009", "500", "SGM inventory digitization; ~500 m accuracy from 1:50,000", "Medium"),
    P("A-3", "ZA", 30.067500, -115.380000, "mine", "A3 Esperanza", "ZONE A",
      "N65-75E vein convergence - trace trenches", SGM, "Esperanza sheet record", "2009", "500", "SGM inventory digitization; ~500 m accuracy from 1:50,000", "Medium"),
    P("A-4", "ZA", 30.076500, -115.380500, "struct", "A4 fault trace N", "ZONE A",
      "map N82E scarp 1 km north", SGM + " + " + ESI, "zoneA_pins", "2009", "500", "fault trace from SGM sheet redrawn on base layer", "Low"),
    P("A-5", "ZA", 30.060500, -115.379500, "struct", "A5 fault trace S", "ZONE A",
      "map scarp 1 km S toward corridor", SGM + " + " + ESI, "zoneA_pins", "2009", "500", "fault trace from SGM sheet redrawn on base layer", "Low"),
    P("A-6", "ZA", 30.068500, -115.386500, "sed", "A6 arroyo", "ZONE A",
      "sediment pair", ESI, "zoneA_pins", "2024-26", "20", DESK, "Medium"),
    # Zone B — San Martin (S2 z16 rendered 1.47 m/px)
    P("B-1", "ZB", 30.146000, -115.375000, "mine", "B1 San Martin", "ZONE B",
      "old drift/catas: sample wall chrysocolla/azurite", SGM, "San Martin sheet record", "2009", "500", "SGM inventory digitization; ~500 m accuracy from 1:50,000", "Medium"),
    P("B-2", "ZB", 30.141000, -115.378000, "pale", "B2 S argillic slope", "ZONE B",
      "survey for blue-green on eroded slopes", S2V, "zoneB_pins", "2020", "30", RGBH, "Low"),
    P("B-3", "ZB", 30.149000, -115.370000, "sed", "B3 arroyo", "ZONE B",
      "sediment pair", S2V, "zoneB_pins", "2020", "30", DESK, "Medium"),
    # Zone C — La Turquesa core (S2 z16 rendered 1.47 m/px)
    P("C-1", "ZC", 30.071000, -115.446000, "mine", "C1 La Turquesa core", "ZONE C",
      "zone type locality: survey for turquoise", SGM, "La Turquesa sheet record", "2009", "500", "SGM inventory digitization; ~500 m accuracy from 1:50,000", "Medium"),
    P("C-2", "ZC", 30.071000, -115.391000, "pale", "C2 El Hormiguero", "ZONE C",
      "massive argillic + Fe-oxide: gully walls", SGM + " + " + S2V, "zoneC_pins", "2009", "500", "SGM alteration polygon cross-checked on S2 viewing composite", "Low"),
    P("C-3", "ZC", 30.062000, -115.420000, "pale", "C3 argillic slope", "ZONE C",
      "fresh gully walls; chips", S2V, "zoneC_pins", "2020", "30", RGBH, "Low"),
    P("C-4", "ZC", 30.075000, -115.410000, "sed", "C4 arroyo", "ZONE C",
      "sediment pair", S2V, "zoneC_pins", "2020", "30", DESK, "Medium"),
]

MINES = [
    ("Josefina", 30.122, -115.360, "abandoned mine", "Cu-Fe epithermal in brecciated white granodiorite; E-W adit 5 m + catas"),
    ("Santa Martha", 30.147, -115.357, "abandoned mine", "epithermal fissure-fills; NW-SE + NE-SW lineament system"),
    ("San Martin", 30.146, -115.375, "abandoned mine", "specularite, malachite, azurite, chalcopyrite, chrysocolla?, jarosite, pyrite, quartz"),
    ("Santa Lucia", 30.158, -115.454, "abandoned mine", "3 catas + 40 m drift (4 x 3 m)"),
    ("La Vibora", 30.171, -115.524, "abandoned mine", "vein-fault strike N35E; 2 x 2 x 5 m cut"),
    ("5 Minas", 30.124, -115.344, "abandoned mine", "Fe-Cu in tabular brecha zone"),
    ("El Sacrificio", 30.124, -115.352, "mineral occurrence", "Fe-Cu hydrothermal veinlets in tabular brecha"),
    ("El Moro", 30.220, -115.396, "mineral occurrence", "occurrence; SGM sheet record"),
    ("La Turquesa", 30.071, -115.446, "abandoned mine", "argillic + Fe-oxide + calcite alteration; massive highly eroded; Cu-Fe-turquoise"),
    ("El Hormiguero", 30.071, -115.391, "abandoned mine", "intense secondary alteration: clays, Fe oxides, calcite"),
    ("La Prieta", 30.070, -115.392, "abandoned mine", "open pit; NE trend on pit face"),
    ("Esperanza", 30.067, -115.380, "abandoned mine", "veins N65-75E converging at rancheria La Prieta"),
    ("El Cardonal", 30.067, -115.376, "abandoned mine", "normal fault N82E/32NW; turquoise; main mine of region"),
    ("La Bonita", 30.048, -115.412, "abandoned mine", "brecha N53E/69NW 0.7 m mineralized; exploration holes around"),
]


def mine_records():
    recs = []
    for name, lat, lon, mtype, notes in MINES:
        recs.append({"record_id": "SGM-" + name.upper().replace(" ", "-").replace("5-MINAS", "5MINAS"),
                     "name": name, "latitude": lat, "longitude": lon, "crs": "EPSG:4326",
                     "type": mtype, "notes": notes, "source": SGM,
                     "source_date": "2009", "coordinate_accuracy_m": "500 (digitized from 1:50,000)",
                     "license": "SGM public sheet; coordinates as transcribed",
                     "pipeline_version": PIPELINE_VERSION})
    return recs


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(path, mode, encoding=None if isinstance(content, bytes) else "utf-8") as f:
        f.write(content)


def main():
    from src.validate import validate_records
    errs = validate_records(PINS)
    if errs:
        print("VALIDATION ERRORS:")
        for e in errs:
            print(" -", e)
        raise SystemExit(1)
    csv_text = records_to_csv(PINS)
    gj_text = json.dumps(records_to_geojson(PINS), indent=1)
    for d in (os.path.join(ROOT, "maps"), os.path.join(ROOT, "site", "maps")):
        write(os.path.join(d, "PIN_POINTS.csv"), csv_text)
        write(os.path.join(d, "PIN_POINTS.geojson"), gj_text)
    print(f"pins: {len(PINS)} records -> maps/ + site/maps/ (csv+geojson)")

    mines = mine_records()
    mcols = ["record_id", "name", "latitude", "longitude", "crs", "type", "notes",
             "source", "source_date", "coordinate_accuracy_m", "license", "pipeline_version"]
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=mcols)
    w.writeheader()
    for m in mines:
        w.writerow(m)
    mgj = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [m["longitude"], m["latitude"]]},
         "properties": {k: m[k] for k in mcols if k not in ("latitude", "longitude")}} for m in mines]}
    for d in (os.path.join(ROOT, "maps"), os.path.join(ROOT, "site", "maps")):
        write(os.path.join(d, "mine_inventory_elaguajito.csv"), buf.getvalue())
        write(os.path.join(d, "mine_inventory_elaguajito.geojson"), json.dumps(mgj, indent=1))
    print(f"mines: {len(mines)} records -> maps/ + site/maps/ (csv+geojson)")

    # DataKit sample: T2 pins + 2 mines + scoring example
    samp = [r for r in PINS if r["target_id"] == "T2"][:6]
    sdir = os.path.join(ROOT, "sample_data")
    write(os.path.join(sdir, "pins_sample.csv"), records_to_csv(samp))
    write(os.path.join(sdir, "pins_sample.geojson"), json.dumps(records_to_geojson(samp), indent=1))
    write(os.path.join(sdir, "mines_sample.csv"), "\n".join(buf.getvalue().splitlines()[:3]) + "\n")
    from src.scores import EVIDENCE, WEIGHTS, all_scores, all_split
    write(os.path.join(sdir, "scoring_example.json"), json.dumps(
        {"weights": WEIGHTS, "scores_v2_blended_legacy": all_scores(),
         "split_v3": all_split(), "evidence_T2": EVIDENCE["T2"],
         "disclaimer": "Desk-screening ranks, NOT probabilities of mineralization. "
                       "v3 shows prospectivity vs feasibility separately, never blended."}, indent=1))
    write(os.path.join(sdir, "README.md"),
          "# Sample DataKit\n\nTiny runnable subset: 6 T2 pin records (CSV+GeoJSON), "
          "2 mine records, and the published scoring model with evidence.\n\n"
          "```bash\npython3 -m unittest         # runs scorer + validator tests\n"
          "python3 src/validate.py sample_data/pins_sample.csv\n```\n"
          "Full data: `maps/PIN_POINTS.*`. Schema: `schemas/pins.schema.json`.\n")
    print("sample_data/ DataKit written")


if __name__ == "__main__":
    main()
