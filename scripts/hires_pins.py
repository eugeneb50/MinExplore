#!/usr/bin/env python3
"""High-resolution pin-point exploration maps for the Baja corridor targets.

Produces (maps/pins/):
  t1_pins.png, t2_pins.png, t2_mass_inset_z18.png, t3_pins.png,
  zoneA_pins.png, zoneB_pins.png, zoneC_pins.png, PIN_POINTS.csv

Imagery: Esri World Imagery z17 (0.74 m/px) for T1/T2/T3/ZoneA,
         z18 (0.37 m/px) for the T2 pale-mass inset,
         open Sentinel-2 2020 z16 (1.47 m/px) for Zones B/C.
Pins: numbered field objectives (outcrop / structure / sediment / works / pale).
"""
import csv
import io
import math
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W2 = 40075016.686
UA = {"User-Agent": "arena-agent/1.0 (research)"}


def slippy(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    lat_r = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_r) + 1 / math.cos(lat_r)) / math.pi) / 2 * n)
    return x, y


def fetch_one(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=60).read()


def fetch_mosaic(provider, z, clat, clon, n):
    """(2n+1)^2 tile mosaic centered on clon/clat. Returns (canvas, tile_m)."""
    cx, cy = slippy(clon, clat, z)
    tile_m = W2 / 2 ** z  # meters (3857) per tile
    jobs = [(dx, dy) for dy in range(-n, n + 1) for dx in range(-n, n + 1)]
    results = {}
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {}
        for dx, dy in jobs:
            if provider == "esri":
                url = (f"https://server.arcgisonline.com/ArcGIS/rest/services/"
                       f"World_Imagery/MapServer/tile/{z}/{cy+dy}/{cx+dx}")
            else:
                url = (f"https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/"
                       f"default/GoogleMapsCompatible/{z}/{cy+dy}/{cx+dx}.jpg")
            futs[ex.submit(fetch_one, url)] = (dx, dy)
        for f in futs:
            dx, dy = futs[f]
            results[(dx, dy)] = Image.open(io.BytesIO(f.result())).convert("RGB")
    S = 256 * (2 * n + 1)
    canvas = Image.new("RGB", (S, S), (0, 0, 0))
    for (dx, dy), im in results.items():
        canvas.paste(im, ((dx + n) * 256, (dy + n) * 256))
    return canvas, tile_m


def make_geo(canvas, z, clat, clon, n):
    cx, cy = slippy(clon, clat, z)
    tile_m = W2 / 2 ** z
    X0 = (cx - n) * tile_m - W2 / 2
    Y0 = W2 / 2 - (cy - n) * tile_m  # canvas TOP = northernmost tile (cy-n)
    R = W2 / (2 * math.pi)
    pxm = tile_m / 256  # meters (3857) per pixel

    def to_px(lon, lat):
        mx = (lon + 180) / 360 * W2 - W2 / 2
        my = R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
        return (mx - X0) / pxm, (Y0 - my) / pxm

    return to_px


def render(canvas, to_px, title, res_label, pins, target, src_note, out,
           grid_major=500, grid_minor=100):
    W, H = canvas.size
    # dim slightly for label contrast
    ov = Image.new("RGB", (W, H), (25, 27, 32))
    canvas = Image.blend(canvas, ov, 0.10)
    dr = ImageDraw.Draw(canvas)
    fs = max(18, int(W / 90))
    try:
        f_t = ImageFont.load_default(size=int(fs * 1.5))
        f_s = ImageFont.load_default(size=fs)
        f_xs = ImageFont.load_default(size=int(fs * 0.85))
        f_pin = ImageFont.load_default(size=int(fs * 0.9))
    except TypeError:
        f_t = f_s = f_xs = f_pin = ImageFont.load_default()

    # grid around window center (from pins, plus target if present)
    lats = [p[1] for p in pins] + ([target[1]] if target else [])
    lons = [p[2] for p in pins] + ([target[2]] if target else [])
    clat = (max(lats) + min(lats)) / 2
    clon = (max(lons) + min(lons)) / 2
    step = grid_major / 60 / 111.0  # degrees (approx)
    la0 = math.floor(clat / step) * step
    la = la0
    while True:
        y = to_px(clon, la)[1]
        if y < -50:
            break
        if 0 <= y < H:
            dr.line([(0, y), (W, y)], fill=(230, 230, 230), width=1)
            dr.text((6, y + 3), f"{la:.3f}N", font=f_xs, fill=(255, 255, 0))
        la += step
    step_lo = grid_major / 60 / (111.0 * math.cos(math.radians(clat)))
    lo0 = math.floor(clon / step_lo) * step_lo
    lo = lo0
    while True:
        x = to_px(lo, clat)[0]
        if x > W + 50:
            break
        if 0 <= x < W:
            dr.line([(x, 0), (x, H)], fill=(230, 230, 230), width=1)
            dr.text((x + 3, H - int(fs * 1.2)), f"{abs(lo):.3f}W", font=f_xs, fill=(255, 255, 0))
        lo += step_lo

    # scale bar
    sb_m = grid_major
    p1 = to_px(clon, clat)
    p2 = to_px(clon - (200 / (111319.49 * math.cos(math.radians(clat)))), clat)
    mpp = abs(p1[0] - p2[0]) / 200  # px per meter
    sb_px = sb_m * mpp
    x0s, y0s = int(fs * 1.2), H - int(fs * 2.6)
    dr.rectangle([x0s, y0s, x0s + sb_px, y0s + int(fs * 0.5)], outline=(255, 255, 255), width=2)
    halfp = x0s + sb_px / 2
    dr.rectangle([x0s, y0s, halfp, y0s + int(fs * 0.5)], fill=(255, 255, 255))
    dr.text((x0s, y0s - int(fs * 1.1)), f"0 — {sb_m//2} — {sb_m} m", font=f_xs, fill=(255, 255, 255))
    # north arrow
    na = int(fs * 3)
    dr.polygon([(W - int(fs*2), na - int(fs*1.5)), (W - int(fs*3.2), na + int(fs*1.5)),
                (W - int(fs*2), na + int(fs*0.6)), (W - int(fs*0.8), na + int(fs*1.5))],
               fill=(255, 255, 255), outline=(0, 0, 0))
    dr.text((W - int(fs*2.6), na + int(fs*1.8)), "N", font=f_s, fill=(255, 255, 255))

    # pins
    r = int(fs * 1.15)
    for pid, plat, plon, kind, label, note in pins:
        x, y = to_px(plon, plat)
        if not (0 <= x < W and 0 <= y < H):
            print(f"  WARN pin {pid} off-canvas")
            continue
        col = {"pale": (190, 110, 200), "struct": (255, 60, 160), "sed": (60, 200, 60),
               "out": (255, 150, 0), "mine": (255, 70, 70)}[kind]
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(250, 250, 250), outline=col, width=4)
        dr.text((x - fs * 0.4, y - fs * 0.75), pid.split("-")[-1], font=f_pin, fill=(20, 20, 20))
        lx = x + r + 6
        if lx + fs * len(label) > W - 10:
            lx = x - r - 6 - fs * len(label)
        dr.text((lx + 2, y - fs * 0.5 + 2), label, font=f_s, fill=(0, 0, 0))
        dr.text((lx, y - fs * 0.5), label, font=f_s, fill=(255, 255, 255))

    # target cross (if any)
    if target:
        x, y = to_px(target[2], target[1])
        t = int(fs * 1.6)
        dr.rectangle([x - t, y - t, x + t, y + t], outline=(255, 0, 0), width=5)
        dr.line([(x - t * 1.7, y), (x + t * 1.7, y)], fill=(255, 0, 0), width=4)
        dr.line([(x, y - t * 1.7), (x, y + t * 1.7)], fill=(255, 0, 0), width=4)
        dr.text((x + t + 8, y - int(fs * 1.4)), "TARGET", font=f_s, fill=(255, 80, 80))

    # title bar
    tb = int(fs * 2.4)
    dr.rectangle([0, 0, W, tb], fill=(20, 22, 28))
    dr.text((14, int(fs * 0.35)), title, font=f_t, fill=(255, 210, 90))
    dr.text((14, int(fs * 1.55)), f"{res_label}  ·  grid {grid_major} m  ·  {src_note}", font=f_xs, fill=(200, 205, 215))

    out_j = out[:-4] + ".jpg" if out.endswith(".png") else out
    canvas.save(out_j, quality=88, optimize=True)
    print(f"saved {out_j} ({W}x{H})")


# ----------------------------------------------------------------------
# PIN DATA: (id, lat, lon, kind, label, field_note)
PINS = {
 "T1": {
  "title": "T1 PIN MAP — Arroyo San Isidro (29.9036, -115.3837)",
  "center": (29.9030, -115.3840), "provider": "esri", "z": 17, "n": 5,
  "target": ("TGT", 29.903605, -115.383656),
  "pins": [
   ("T1-1", 29.906097, -115.390962, "pale", "P1 WNW pale cluster", "outcrop check + rock chips; look for alteration colour zoning"),
   ("T1-2", 29.897790, -115.381181, "pale", "P2 S pale patch", "map extent; chips; gully walls"),
   ("T1-3", 29.904306, -115.379883, "pale", "P3 E pale patch", "map extent; chips"),
   ("T1-5", 29.905147, -115.384249, "sed", "P4 arroyo N", "sediment pair (2 bags) — N relay"),
   ("T1-6", 29.902032, -115.385183, "sed", "P5 arroyo S", "sediment pair — S relay"),
  ],
 },
 "T2": {
  "title": "T2 PIN MAP — Cerro la Turquesa (30.0485, -115.2362)",
  "center": (30.0455, -115.2415), "provider": "esri", "z": 17, "n": 5,
  "target": ("TGT", 30.048522, -115.236173),
  "pins": [
   ("T2-1", 30.0502, -115.2466, "pale", "P1 pale mass CENTER", "map the mass; identify rock; 100m chip grid; hunt blue-green"),
   ("T2-2", 30.0490, -115.2428, "pale", "P2 mass E edge", "alteration front — sample both sides of contact"),
   ("T2-4", 30.0445, -115.2360, "struct", "P3 band @ arroyo", "ROAD or FAULT SCARP? measure, sample gouge"),
   ("T2-5", 30.0405, -115.2265, "struct", "P4 band 1.5km E", "trace lineament; look for 2nd scarp"),
   ("T2-6", 30.0440, -115.2470, "sed", "P5 arroyo below mass", "sediment pair — mass catchment"),
   ("T2-7", 30.0440, -115.2330, "out", "P6 summit 740m", "Cerro la Turquesa: lithology + structural grain"),
  ],
 },
 "T2i": {
  "title": "T2 DETAIL — pale argillic mass, z18 (0.37 m/px)",
  "center": (30.0498, -115.2458), "provider": "esri", "z": 18, "n": 5,
  "target": ("TGT", 30.048522, -115.236173),
  "pins": [
   ("T2-1", 30.0502, -115.2466, "pale", "P1 mass center", "outcrop + chips"),
   ("T2-2", 30.0490, -115.2428, "pale", "P2 E edge", "alteration front"),
   ("T2-6", 30.0455, -115.2485, "sed", "P5 gully mouth", "sediment — fresh wall sample"),
  ],
 },
 "T3": {
  "title": "T3 PIN MAP — Cerro la Palmita (30.0257, -115.2869)",
  "center": (30.0245, -115.2815), "provider": "esri", "z": 17, "n": 5,
  "target": ("TGT", 30.025725, -115.286885),
  "pins": [
   ("T3-2", 30.017216, -115.271919, "out", "P2 ridge high 808m", "Cerro la Palmita: outcrop map + grain"),
   ("T3-3", 30.022132, -115.293371, "out", "P3 steepest 36°", "857m W — first bedrock, sample + structure"),
   ("T3-4", 30.017932, -115.285430, "sed", "P4 arroyo S", "sediment pair"),
   ("T3-5", 30.024154, -115.289239, "sed", "P5 arroyo W", "sediment pair"),
   ("T3-6", 30.0305, -115.2745, "out", "P6 MEX 2 cut-bank", "road cut NE — free outcrops + any old works"),
  ],
 },
 "ZA": {
  "title": "ZONE A — El Cardonal / La Prieta / Esperanza (documented TURQUOISE)",
  "center": (30.0690, -115.3830), "provider": "esri", "z": 17, "n": 5,
  "target": None,
  "pins": [
   ("A-1", 30.0670, -115.3760, "mine", "A1 El Cardonal", "TURQUOISE doc. — walk N82°E fault scarp; sample all blue-green"),
   ("A-2", 30.0700, -115.3920, "mine", "A2 La Prieta pit", "walk pit walls — fresh oxidized Cu surfaces"),
   ("A-3", 30.0675, -115.3800, "mine", "A3 Esperanza", "N65-75°E vein convergence — trace trenches"),
   ("A-4", 30.0765, -115.3805, "struct", "A4 fault trace N", "map N82°E scarp 1 km north"),
   ("A-5", 30.0605, -115.3795, "struct", "A5 fault trace S", "map scarp 1 km S toward corridor"),
   ("A-6", 30.0685, -115.3865, "sed", "A6 arroyo", "sediment pair"),
  ],
 },
 "ZB": {
  "title": "ZONE B — San Martín (Cu oxidation: chrysocolla/azurite/malachite)",
  "center": (30.1465, -115.3740), "provider": "s2", "z": 16, "n": 2,
  "target": None,
  "pins": [
   ("B-1", 30.1460, -115.3750, "mine", "B1 San Martín", "old drift/catas: sample wall chrysocolla/azurite"),
   ("B-2", 30.1410, -115.3780, "pale", "B2 S argillic slope", "survey for blue-green on eroded slopes"),
   ("B-3", 30.1490, -115.3700, "sed", "B3 arroyo", "sediment pair"),
  ],
 },
 "ZC": {
  "title": "ZONE C — La Turquesa core + El Hormiguero (massive argillic)",
  "center": (30.0710, -115.4200), "provider": "s2", "z": 16, "n": 5,
  "target": None,
  "pins": [
   ("C-1", 30.0710, -115.4460, "mine", "C1 La Turquesa core", "zone type locality: survey for turquoise"),
   ("C-2", 30.0710, -115.3910, "pale", "C2 El Hormiguero", "massive argillic + Fe-oxide: gully walls"),
   ("C-3", 30.0620, -115.4200, "pale", "C3 argillic slope", "fresh gully walls; chips"),
   ("C-4", 30.0750, -115.4100, "sed", "C4 arroyo", "sediment pair"),
  ],
 },
}

OUTDIR = "maps/pins"


def main():
    import os
    os.makedirs(OUTDIR, exist_ok=True)
    files = {"T1": "t1_pins.jpg", "T2": "t2_pins.jpg", "T2i": "t2_mass_inset_z18.jpg",
             "T3": "t3_pins.jpg", "ZA": "zoneA_pins.jpg", "ZB": "zoneB_pins.jpg",
             "ZC": "zoneC_pins.jpg"}
    rows = []
    for key, d in PINS.items():
        print(f"building {key} ...")
        canvas, tile_m = fetch_mosaic(d["provider"], d["z"], d["center"][0], d["center"][1], d["n"])
        to_px = make_geo(canvas, d["z"], d["center"][0], d["center"][1], d["n"])
        ground_mpx = tile_m / 256 * math.cos(math.radians(d["center"][0]))
        res = f"{ground_mpx:.2f} m/px"
        src = ("Esri World Imagery (© Esri/Maxar — research use)" if d["provider"] == "esri"
               else "Copernicus S2 2020 (CC BY-NC-SA 4.0)")
        gm = 500 if ground_mpx < 1.0 else 1000
        render(canvas, to_px, d["title"], res, d["pins"], d["target"],
               src, f"{OUTDIR}/{files[key]}", grid_major=gm,
               grid_minor=gm // 5)
        for pid, plat, plon, kind, label, note in d["pins"]:
            rows.append([pid, d["title"].split(" — ")[0].strip(), f"{plat:.6f}", f"{plon:.6f}",
                         kind, label, note])
        if d["target"]:
            rows.append([d["target"][0], d["title"].split(" — ")[0].strip(),
                         f"{d['target'][1]:.6f}", f"{d['target'][2]:.6f}", "target", "TARGET", "reference point"])
    with open(f"{OUTDIR}/PIN_POINTS.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "area", "lat", "lon", "type", "label", "field_note"])
        w.writerows(rows)
    print(f"saved {OUTDIR}/PIN_POINTS.csv ({len(rows)} rows)")


if __name__ == "__main__":
    main()
