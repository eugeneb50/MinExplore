#!/usr/bin/env python3
"""Build the turquoise-prospect corridor map (La Turquesa Cu-Fe belt + user targets).

Wide S2 2020 mosaic (~29 km, z10 3x3) with:
- 14 documented SGM El Aguajito workings (red triangles, ranked)
- 3 surveyed user targets (blue squares)
- recommended prospect zones (polygons)
- El Aguajito sheet boundary + La Bonita->T2 corridor line
- lat/lon grid, legend, title
"""
import io
import math
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def slippy(lon, lat, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    lat_r = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_r) + 1 / math.cos(lat_r)) / math.pi) / 2 * n)
    return x, y


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "arena-agent/1.0 (research)"})
    return urllib.request.urlopen(req, timeout=60).read()


CENTER_LAT, CENTER_LON = 30.02, -115.38
z = 10
cx, cy = slippy(CENTER_LON, CENTER_LAT, z)
TILE = 256
W2 = 40075016.686 / 2

imgs = []
for dy in (-1, 0, 1):
    row = []
    for dx in (-1, 0, 1):
        url = (f"https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/"
               f"default/GoogleMapsCompatible/{z}/{cy+dy}/{cx+dx}.jpg")
        row.append(Image.open(io.BytesIO(fetch(url))).convert("RGB"))
    imgs.append(row)
canvas = Image.new("RGB", (TILE * 3, TILE * 3), "black")
for j, r in enumerate(imgs):
    for i, im in enumerate(r):
        canvas.paste(im, (i * TILE, j * TILE))
SCALE = 2.5  # upscale
canvas = canvas.resize((int(TILE * 3 * SCALE), int(TILE * 3 * SCALE)), Image.LANCZOS)

# --- geo <-> pixel (Web Mercator) ---
pxm = (TILE * SCALE) / (W2 / 2 ** z)  # pixels per meter (output scale)
X0 = (cx - 1) * (W2 / 2 ** z) - W2 / 2  # canvas left edge, meters 3857
Y0 = W2 / 2 - (cy - 1) * (W2 / 2 ** z)  # canvas top edge (north), meters 3857


def to_px(lon, lat):
    R = W2 / (2 * math.pi)  # 6378137
    mx = (lon + 180) / 360 * W2 - W2 / 2
    lat_r = math.radians(lat)
    my = R * math.log(math.tan(math.pi / 4 + lat_r / 2))
    return (mx - X0) * pxm, (Y0 - my) * pxm


def to_latlon(px, py):
    R = W2 / (2 * math.pi)
    mx = X0 + px / pxm
    my = Y0 - py / pxm
    lon = (mx + W2 / 2) / W2 * 360 - 180
    lat = math.degrees(2 * math.atan(math.exp(my / R)) - math.pi / 2)
    return lat, lon


W, H = canvas.size
dr = ImageDraw.Draw(canvas)
try:
    f_t = ImageFont.load_default(size=30)
    f_s = ImageFont.load_default(size=20)
    f_xs = ImageFont.load_default(size=16)
except TypeError:
    f_t = f_s = f_xs = ImageFont.load_default()

# dim the background a bit for label contrast
ov = Image.new("RGB", (W, H), (20, 20, 25))
canvas = Image.blend(canvas, ov, 0.18)
dr = ImageDraw.Draw(canvas)

# --- grid every 10' ---
def grid_lines():
    lat0 = math.floor(29.85 * 6 / 10) * 10 / 6
    la = lat0
    while to_px(-115.55, la)[1] < H + 40:
        y = to_px(-115.55, la)[1]
        if 0 < y < H:
            dr.line([(0, y), (W, y)], fill=(255, 255,255, 60) if False else (210, 210, 210), width=1)
            dr.text((6, y + 2), f"{int(la*60//1)}'{int((la*60)%1):02d}" if False else f"{la:.2f}N", font=f_xs, fill=(255, 255, 0))
        la += 1 / 6
    lo = -115.55
    while to_px(lo, 30.15)[0] < W + 40:
        x = to_px(lo, 30.15)[0]
        if 0 < x < W:
            dr.line([(x, 0), (x, H)], fill=(210, 210, 210), width=1)
            dr.text((x + 3, H - 22), f"{abs(lo):.2f}W", font=f_xs, fill=(255, 255, 0))
        lo += 1 / 6

grid_lines()

# --- El Aguajito sheet boundary (30°00'-30°15'N, 115°20'-115°40'W) ---
a = to_px(-115 + 40 / 60, 30 + 15 / 60)  # NE corner
b = to_px(-115 + 40 / 60, 30 + 0 / 60)   # SE corner
c = to_px(-115 + 20 / 60, 30 + 0 / 60)   # SW
d = to_px(-115 + 20 / 60, 30 + 15 / 60)  # NW
dr.polygon([a, b, c, d], outline=(255, 220, 0), width=2)
dr.text((a[0] - 380, a[1] + 6), "SGM El Aguajito H11-B85 sheet (1:50,000, 2009)", font=f_s, fill=(255, 220, 0))

# --- documented SGM workings (ranked for turquoise) ---
# name, lat, lon, label, color
workings = [
    ("EL CARDONAL", 30.067, -115.376, "TURQUOISE doc. - 'main mine of region' - N82E normal fault", (255, 60, 60)),
    ("SAN MARTIN", 30.146, -115.375, "chrysocolla + azurite + malachite (Cu oxidation)", (255, 60, 60)),
    ("LA TURQUESA", 30.071, -115.446, "zone core - massive argillic alteration", (255, 60, 60)),
    ("EL HORMIGUERO", 30.071, -115.391, "intense clay + Fe-oxide + calcite alteration", (255, 140, 60)),
    ("LA PRIETA", 30.070, -115.392, "open pit; NE trend", (255, 140, 60)),
    ("ESPERANZA", 30.067, -115.376, "veins N65-75E converging", (255, 140, 60)),
    ("LA BONITA", 30.048, -115.412, "brecha N53E/69NW 0.7m", (255, 140, 60)),
    ("5 MINAS", 30.124, -115.344, "Fe-Cu tabular brecha", (255, 200, 90)),
    ("EL SACRIFICIO", 30.124, -115.352, "occurrence, tabular brecha", (255, 200, 90)),
    ("JOSEFINA", 30.122, -115.360, "Cu-Fe brecciated granodiorite", (255, 200, 90)),
    ("SANTA MARTHA", 30.147, -115.357, "epithermal fissure-fills", (255, 200, 90)),
    ("SANTA LUCIA", 30.158, -115.454, "drift + catas", (255, 200, 90)),
    ("LA VIBORA", 30.171, -115.524, "vein-fault N35E", (255, 200, 90)),
    ("EL MORO", 30.220, -115.396, "occurrence", (200, 200, 200)),
]
for name, la, lo, note, col in workings:
    x, y = to_px(lo, la)
    if 0 < x < W and 0 < y < H:
        dr.polygon([(x, y - 10), (x - 9, y + 7), (x + 9, y + 7)], fill=col, outline=(0, 0, 0))
        dr.text((x + 12, y - 8), name, font=f_s, fill=col)

# --- user targets ---
targets = [
    ("T1", 29.903605, -115.383656, "Arroyo San Isidro (5.4)"),
    ("T2", 30.048522, -115.236173, "Cerro la Turquesa (6.3)"),
    ("T3", 30.025725, -115.286885, "Cerro la Palmita (5.5)"),
]
for name, la, lo, note in targets:
    x, y = to_px(lo, la)
    if 0 < x < W and 0 < y < H:
        dr.rectangle([x - 9, y - 9, x + 9, y + 9], fill=(60, 160, 255), outline=(255, 255, 255), width=2)
        dr.text((x + 13, y - 10), f"{name} {note}", font=f_s, fill=(120, 200, 255))

# --- recommended prospect zones ---
def zone(latS, latN, lonW, lonE, label, col, fill=None):
    p = [to_px(lonW, latN), to_px(lonE, latN), to_px(lonE, latS), to_px(lonW, latS)]
    if fill:
        dr.polygon(p, fill=fill)
    dr.polygon(p, outline=col, width=3)
    dr.text((p[0][0] + 6, p[0][1] + 4), label, font=f_s, fill=col)

zone(30.050, 30.085, -115.398, -115.355, "ZONE A - El Cardonal/Esperanza/La Prieta complex\n(documented turquoise + fault + pit; BEST)", (255, 80, 80), (255, 80, 80, 40) if False else None)
zone(30.128, 30.165, -115.400, -115.345, "ZONE B - San Martin (Cu oxidation: chrysocolla/azurite)", (255, 80, 80))
zone(30.050, 30.090, -115.470, -115.370, "ZONE C - La Turquesa core + El Hormiguero (argillic)", (255, 160, 80))
zone(30.030, 30.070, -115.272, -115.212, "ZONE D - T2 Cerro la Turquesa (user area)\ntoponym + pale argillic mass + NE-SW lineament", (80, 200, 255))

# corridor line La Bonita -> T2
lb = to_px(-115.412, 30.048)
t2 = to_px(-115.236173, 30.048522)
dr.line([lb, t2], fill=(200, 255, 200), width=2)
mid = ((lb[0] + t2[0]) / 2, (lb[1] + t2[1]) / 2)
dr.text((mid[0] - 60, mid[1] - 26), "30.03-30.05N corridor (user T3 on it)", font=f_xs, fill=(200, 255, 200))

# --- MEX 2 note (visible in imagery; approximate along the north) ---
dr.text((W - 420, 12), "Carretera MEX 2 visible in imagery (NE-SE of zone A, ~2 km E of T2)", font=f_xs, fill=(255, 255, 200))

# --- title + legend ---
dr.rectangle([0, 0, W, 64], fill=(20, 22, 28))
dr.text((14, 10), "TURQUOISE PROSPECT MAP - La Turquesa Cu-Fe epithermal belt (SGM El Aguajito 1:50k, 2009) + surveyed targets", font=f_t, fill=(255, 210, 90))
dr.text((14, 42), "Model: low-sulfidation epithermal Cu-Fe (+/- Au) in brecciated granodiorite + Alisitos andesite; NE-SW normals + N65-75E veins + tabular brechas/sigmoids (Corbett)", font=f_xs, fill=(200, 205, 215))

lx, ly = W - 470, H - 210
dr.rectangle([lx - 10, ly - 10, W - 10, H - 10], fill=(20, 22, 28, 220) if False else (25, 27, 33))
dr.text((lx, ly), "LEGEND", font=f_s, fill=(255, 255, 255))
dr.polygon([(lx + 6, ly + 34), (lx - 2, ly + 46), (lx + 14, ly + 46)], fill=(255, 60, 60), outline=(0, 0, 0))
dr.text((lx + 24, ly + 32), "documented turquoise / Cu-oxidation work (ranked)", font=f_xs, fill=(255, 150, 150))
dr.polygon([(lx + 6, ly + 62), (lx - 2, ly + 74), (lx + 14, ly + 74)], fill=(255, 140, 60), outline=(0, 0, 0))
dr.text((lx + 24, ly + 60), "documented Cu-Fe work / alteration (SGM 2009)", font=f_xs, fill=(255, 200, 150))
dr.rectangle([lx - 2, ly + 88, lx + 12, ly + 102], fill=(60, 160, 255), outline=(255, 255, 255), width=2)
dr.text((lx + 24, ly + 88), "surveyed target (T1/T2/T3)", font=f_xs, fill=(150, 210, 255))
dr.rectangle([lx - 2, ly + 116, lx + 12, ly + 130], outline=(255, 220, 0), width=2)
dr.text((lx + 24, ly + 116), "SGM sheet boundary", font=f_xs, fill=(255, 230, 150))
dr.line([(lx - 2, ly + 152), (lx + 12, ly + 152)], fill=(200, 255, 200), width=2)
dr.text((lx + 24, ly + 144), "prospecting corridor 30.03-30.05N", font=f_xs, fill=(200, 255, 200))
dr.text((lx, ly + 170), "Imagery: Copernicus S2 2020 (CC BY-NC-SA 4.0, via EOX)", font=f_xs, fill=(150, 160, 175))
dr.text((lx, ly + 190), "Sourced: SGM Carta El Aguajito H11-B85 (2009) PDF", font=f_xs, fill=(150, 160, 175))

canvas.save("maps/turquoise_prospect_map.jpg", quality=88, optimize=True)
print("saved maps/turquoise_prospect_map.jpg", canvas.size)
