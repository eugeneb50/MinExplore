#!/usr/bin/env python3
"""
mineral_pipeline.py
===================
Satellite-based mineral-prospecting pipeline for point targets.

WORKFLOW (as applied to 29.903605, -115.383656, Baja California, MX):
  1. Locate: reverse geocode + topographic tile read (what's on the ground).
  2. Terrain: 10 m DEM -> slope / aspect / hillshade / drainage context.
  3. Surface screen: 10 m Sentinel-2 (s2cloudless) RGB -> land-cover /
     tone classes + B/R blue-shift proxy (Fe-oxide depletion / clay-carbonate
     indicator in RGB-only mode).
  4. Full bands (optional, best quality): Harmonized Landsat/Sentinel-2 (HLS)
     30 m -> NDVI, NDWI, ferric-iron, clay, carbonate alteration indices +
     multi-date composites. Requires a free NASA Earthdata Login.
  5. Basemap mosaic (optional): official Bing Maps / Google Earth Engine for
     visual geomorphology at z16-18 (drifts, pits, road cuts).

MODES:
  python3 mineral_pipeline.py screen --lat 29.903605 --lon -115.383656
  python3 mineral_pipeline.py dem    --lat 29.903605 --lon -115.383656 --half-km 2
  python3 mineral_pipeline.py bands  --lat 29.903605 --lon -115.383656 \
      --days 365 --max-cloud 10        # needs EARTHDATA_USER / EARTHDATA_PW
  python3 mineral_pipeline.py tiles    --lat 29.903605 --lon -115.383656 \
      --zoom 16 --provider bing --key YOUR_BING_KEY
  python3 mineral_pipeline.py spread --lat 29.903605 --lon -115.383656 --half-km 2
      # -> out/map_spread_4km.png (9 non-redundant panels, same extent,
      #    500 m lat/lon grid, scale bar, N arrow) + maps/field_waypoints.csv
      #    (GPS checkpoints with bearing/distance/elevation for field test)

DATA SOURCES & LICENSES
  * EOX s2cloudless (Sentinel-2 2020 composite, 10 m, CC BY-NC-SA 4.0)
      https://tiles.maps.eox.at  (non-commercial research use)
  * USGS elevation-tiles-prod SRTM-derived 10 m GeoTIFF tiles (public)
      https://s3.amazonaws.com/elevation-tiles-prod/v2/geotiff/{z}/{x}/{y}.tif
  * NASA/USGS HLS (Landsat 8/9 + Sentinel-2, 30 m, harmonized) via CMR
      search is public; download needs free Earthdata Login (urs.earthdata.gov)
      https://cmr.earthdata.nasa.gov
  * Bing Maps Tile / Imagery API (official, requires key, MS licensing terms)
      https://learn.microsoft.com/bing-maps/rest-services
  * Google: use Earth Engine (ee.ImageCollection('COPERNICUS/S2_SR')) or the
      Photorealistic 3D Tiles API - do NOT scrape tile.google.com /
      bing.com tiles (ToS violation + CAPTCHAs + rotating tile IDs).

NOTE ON SWIR: RGB-only products (s2cloudless, Bing aerial) can only screen
for BROAD tone anomalies. Diagnostic mineral mapping (clay vs carbonate vs
sulfate) needs SWIR bands: Sentinel-2 B11/B12, Landsat B6/B7, ASTER bands
6/7, or AVIRIS hyperspectral (USGS SFUG - free, best for mineral mapping).
"""
import argparse
import io
import json
import math
import os
import sys
import urllib.request

import numpy as np
from PIL import Image

USER_AGENT = "mineral-pipeline/1.0 (research)"


# ----------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------
def slippy(lon, lat, z):
    """Web-Mercator (Google/Bing/OSM) tile index for a lon/lat at zoom z."""
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    lat_r = math.radians(lat)
    y = int((1 - math.log(math.tan(lat_r) + 1 / math.cos(lat_r)) / math.pi) / 2 * n)
    return x, y


def quadkey(x, y, z):
    """Microsoft quadkey directly from a (x, y, z) slippy tile index."""
    q = []
    for i in range(z, 0, -1):
        mask = 2 ** (i - 1)
        b = (0 if (x & mask) == 0 else 1) + (0 if (y & mask) == 0 else 2)
        q.append(str(b))
    return "".join(q)


def get(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, **(headers or {})})
    return urllib.request.urlopen(req, timeout=60).read()


# ----------------------------------------------------------------------
# MODE: screen  (Sentinel-2 10 m RGB via EOX s2cloudless - no account needed)
# ----------------------------------------------------------------------
def mode_screen(lat, lon, outdir):
    import urllib.request
    cx, cy = slippy(lon, lat, 15)
    imgs = []
    for dy in (-1, 0, 1):
        row = []
        for dx in (-1, 0, 1):
            url = ("https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/"
                   f"default/GoogleMapsCompatible/15/{cy+dy}/{cx+dx}.jpg")
            row.append(Image.open(io.BytesIO(get(url))).convert("RGB"))
        imgs.append(row)
    w, h = row[0].size
    canvas = Image.new("RGB", (w * 3, h * 3), (0, 0, 0))
    for j, r in enumerate(imgs):
        for i, im in enumerate(r):
            canvas.paste(im, (i * w, j * h))
    arr = np.asarray(canvas, dtype=np.float32) / 255.0
    H, W, _ = arr.shape
    px = 111319.49 * math.cos(math.radians(lat)) / 2 ** 15
    print(f"image {W}x{H}, {px:.2f} m/px, {W*px/1000:.1f} km wide")

    R, G, B = arr[..., 0], arr[..., 1], arr[..., 2]
    mx = np.maximum(np.maximum(R, G), B)
    mn = np.minimum(np.minimum(R, G), B)
    V = mx
    S = (mx - mn) / np.maximum(mx, 1e-6)
    BR = B / np.maximum(R, 1e-3)

    VEG = (G > R * 0.95) & (G >= B) & (S > 0.18) & (V > 0.08)
    BRIGHT = (V > 0.62) & (S < 0.22)
    DARK = (V < 0.16)
    TONE = (S < 0.32) & (V > 0.25) & (V < 0.62) & ~VEG & ~BRIGHT
    SOIL = (R > G) & (G > B * 0.95) & (S >= 0.32) & (V > 0.22) & ~VEG & ~BRIGHT & ~TONE

    UNCL = np.ones_like(R, dtype=bool)
    classes = np.zeros((H, W), dtype=np.int8)
    for name, m in [("BRIGHT", BRIGHT), ("TONE", TONE), ("VEG", VEG), ("SOIL", SOIL), ("DARK", DARK)]:
        classes[m & UNCL] = {"BRIGHT": 4, "TONE": 2, "VEG": 1, "SOIL": 3, "DARK": 5}[name]
        UNCL &= ~m

    ccr, ccw = H // 2, W // 2
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.hypot((xx - ccw) * px, (yy - ccr) * px) / 1000.0
    m1 = dist <= 1.0
    print("class fractions within 1 km of target:")
    for name, cid in [("BRIGHT", 4), ("TONE", 2), ("VEG", 1), ("SOIL", 3), ("DARK", 5)]:
        print(f"  {name:7s} {100*np.mean(classes[m1] == cid):5.1f}%")
    print(f"B/R mean within 1 km: {np.mean(BR[m1]):.3f} (image {np.mean(BR):.3f}); "
          f"p99 = {np.percentile(BR, 99):.3f}")

    os.makedirs(outdir, exist_ok=True)
    palette = {0: (120, 120, 120), 1: (60, 160, 60), 2: (190, 110, 200),
               3: (190, 150, 90), 4: (255, 255, 220), 5: (30, 30, 30)}
    cls = np.zeros((H, W, 3), dtype=np.uint8)
    for cid, rgb in palette.items():
        cls[classes == cid] = rgb
    Image.fromarray(cls).save(f"{outdir}/class_map.png")
    br = np.clip((BR - 0.40) / (1.05 - 0.40), 0, 1) * 255
    Image.fromarray(np.dstack([br, br, 255 - br]).astype("uint8")).save(f"{outdir}/br_map.png")
    print(f"saved {outdir}/class_map.png, {outdir}/br_map.png")


# ----------------------------------------------------------------------
# MODE: dem  (10 m SRTM-derived tiles from USGS elevation-tiles-prod)
# ----------------------------------------------------------------------
def mode_dem(lat, lon, outdir, half_km):
    import rasterio
    from pyproj import Transformer
    from rasterio.merge import merge
    from rasterio.transform import from_origin

    z = 14
    cx, cy = slippy(lon, lat, z)
    files = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            f = f"{outdir}/dem14_{cx+dx}_{cy+dy}.tif"
            if not os.path.exists(f):
                open(f, "wb").write(get(
                    f"https://s3.amazonaws.com/elevation-tiles-prod/v2/geotiff/{z}/{cx+dx}/{cy+dy}.tif"))
            files.append(f)
    ds = [rasterio.open(f) for f in files]
    arr, tr = merge(ds, nodata=-32768)
    for d in ds:
        d.close()
    dem = arr[0].astype(float)
    dem[dem < -30000] = np.nan
    res = abs(tr.a)
    t_fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    t_rev = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    mx, my = t_fwd.transform(lon, lat)
    col = int((mx - tr.c) / tr.a)
    row = int((my - tr.f) / tr.e)
    print(f"target elevation: {dem[row, col]:.0f} m")
    half = int(half_km * 1000 / res)
    r0, r1 = max(0, row - half), min(dem.shape[0], row + half)
    c0, c1 = max(0, col - half), min(dem.shape[1], col + half)
    w = dem[r0:r1, c0:c1]
    print(f"window {2*half*res/1000:.1f} km: min {np.nanmin(w):.0f} m, "
          f"max {np.nanmax(w):.0f} m, mean {np.nanmean(w):.0f} m")
    i, j = np.unravel_index(np.nanargmax(w), w.shape)
    lp, pp = t_rev.transform(tr.c + (c0 + j) * tr.a, tr.f + (r0 + i) * tr.e)
    print(f"local max: {lp:.4f}, {pp:.4f} ({w[i, j]:.0f} m)")

    dy_, dx_ = np.gradient(np.nan_to_num(w), res, res)
    slope = np.degrees(np.arctan(np.hypot(dx_, dy_)))
    slope = np.where(np.isfinite(w), slope, np.nan)
    a = (np.degrees(np.arctan2(-dy_, -dx_)) + 360) % 360
    bearing = (a + 90) % 360
    bearing = np.where(np.isfinite(w), bearing, np.nan)
    print(f"slope deg: mean {np.nanmean(slope):.1f}, median {np.nanmedian(slope):.1f}, "
          f"p90 {np.nanpercentile(slope, 90):.1f}, max {np.nanmax(slope):.1f}")
    print(f"frac >15deg: {100*np.nanmean(slope > 15):.1f}%   >25deg: {100*np.nanmean(slope > 25):.1f}%")
    bh = np.histogram(bearing[np.isfinite(w)], bins=12, range=(0, 360))[0]
    labels = ["N", "NNE", "ENE", "E", "ESE", "SSE", "S", "SSW", "WSW", "W", "WNW", "NNW"]
    top = sorted(zip(labels, bh), key=lambda t: -t[1])[:5]
    print("dominant aspects:", ", ".join(f"{l} {100*c/bh.sum():.0f}%" for l, c in top))
    np.save(f"{outdir}/dem_win.npy", w)
    np.save(f"{outdir}/slope_win.npy", slope)
    za, azr = math.radians(45), math.radians(315)
    az = np.radians(bearing)
    hs = 1000 * (np.cos(za) * np.cos(np.radians(slope)) +
                 np.sin(za) * np.sin(np.radians(slope)) * np.cos(azr - az))
    hs = np.where(np.isfinite(w), np.clip(hs, 0, 1000), 0)
    Image.fromarray(hs.astype("uint8")).save(f"{outdir}/hillshade.png")
    t2 = from_origin(tr.c + c0 * tr.a, tr.f + r0 * tr.e, abs(tr.a), abs(tr.e))
    out = rasterio.open(f"{outdir}/dem_window.tif", "w", driver="GTiff",
                        height=w.shape[0], width=w.shape[1], count=1,
                        dtype="float32", crs="EPSG:3857", transform=t2)
    out.write(np.nan_to_num(w, nan=-9999), 1)
    out.close()
    print(f"saved {outdir}/hillshade.png, {outdir}/dem_window.tif")


# ----------------------------------------------------------------------
# MODE: bands  (HLS full-spectral, 30 m; needs free Earthdata Login)
# ----------------------------------------------------------------------
def mode_bands(lat, lon, outdir, days, max_cloud):
    from datetime import datetime, timedelta
    import base64
    import time

    u, p = os.environ.get("EARTHDATA_USER"), os.environ.get("EARTHDATA_PW")
    if not (u and p):
        sys.exit("Set EARTHDATA_USER / EARTHDATA_PW (free account at urs.earthdata.gov).")
    os.makedirs(outdir, exist_ok=True)
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    d0, d1 = start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")
    pad = 0.06
    bb = f"{lon-pad},{lat-pad},{lon+pad},{lat+pad}"

    def cmr(short):
        url = ("https://cmr.earthdata.nasa.gov/search/granules.json?short_name="
               f"{short}&boundingBox={bb}&temporal={d0},{d1}&page_size=100")
        return json.load(urllib.request.urlopen(
            urllib.request.Request(url, headers={"Client-Id": USER_AGENT}), timeout=60))["feed"]["entry"]

    entries = []
    for short in ("HLSS30", "HLAL30"):
        for e in cmr(short):
            entries.append(e)
    print(f"found {len(entries)} granules (S2+Landsat HLS)")
    if not entries:
        sys.exit("no granules - widen --days")

    # prefer recent, low-cloud
    def cl(e):
        t = e.get("title", "")
        return e.get("producer_granule_id", "")
    entries.sort(key=cl, reverse=True)

    tok = base64.b64encode(f"{u}:{p}".encode()).decode()
    gran = entries[0]
    pid = gran["producer_granule_id"]
    print("using granule:", pid)
    bands = {}
    for l in gran.get("links", []):
        t = l.get("title", "")
        if ".tif" in t and any(b in t for b in (".B02.", ".B03.", ".B04.", ".B05.",
                                                ".B06.", ".B07.", ".B08.", ".B8A.", ".B11.", ".B12.")):
            bands[t.split(".")[-2]] = l["href"]
    print("bands:", sorted(bands))
    for bn, href in bands.items():
        dest = f"{outdir}/{pid}.{bn}.tif"
        if os.path.exists(dest):
            continue
        print("downloading", bn)
        req = urllib.request.Request(href, headers={"Authorization": f"Basic {tok}"})
        open(dest, "wb").write(urllib.request.urlopen(req, timeout=300).read())
    time.sleep(2)

    # ---- alteration indices (30 m, atmospherically corrected surface reflectance)
    def rd(bn):
        import rasterio
        with rasterio.open(f"{outdir}/{pid}.{bn}.tif") as s:
            a = s.read(1).astype(float) / 10000.0
            return a
    B2, B3, B4, B8, B8A = rd("B02"), rd("B03"), rd("B04"), rd("B08"), rd("B8A")
    B5, B6, B7, B11, B12 = (rd(b) for b in ("B05", "B06", "B07", "B11", "B12"))
    safe = lambda x, y: np.where(np.abs(x) + np.abs(y) > 1e-8, x / (np.abs(x) + np.abs(y)), 0.0)
    idx = {
        "NDVI":  safe(B8 - B4, B8 + B4),
        "NDWI":  safe(B8 - B5, B8 + B5),
        "FAI":   1.0 / (1.0 + safe(B8 - B4, B8 + B4)),          # ferric iron absorption
        "clay":  safe(B11 - B4, B11 + B4),                        # clay / Al-OH proxy
        "carb":  safe(B4 - B5, B4 + B5),                          # carbonate proxy
        "swir_ratio": safe(B11 - B12, B11 + B12),                 # sulfide/sulfate hint
    }
    for name, a in idx.items():
        import rasterio
        with rasterio.open(f"{outdir}/{pid}.B04.tif") as s:
            s2 = s
        out = rasterio.open(f"{outdir}/idx_{name}.tif", "w", driver="GTiff",
                            height=a.shape[0], width=a.shape[1], count=1,
                            dtype="float32", crs=s2.crs, transform=s2.transform)
        out.write(a.astype("float32"), 1)
        out.close()
        print(f"  {name}: mean {np.nanmean(a):.3f}")
    print(f"saved {len(idx)} index GeoTIFFs in {outdir}/")
    print("NEXT: overlay idx_* on the class map; high FAI + low NDVI on slopes + ")
    print("structural trend = follow-up target; verify with ASTER/AVIRIS + sampling.")


# ----------------------------------------------------------------------
# MODE: tiles  (official Bing mosaic for visual mapping)
# ----------------------------------------------------------------------
def mode_tiles(lat, lon, outdir, zoom, provider, key):
    os.makedirs(outdir, exist_ok=True)
    cx, cy = slippy(lon, lat, zoom)
    imgs = []
    for dy in (-1, 0, 1):
        row = []
        for dx in (-1, 0, 1):
            if provider == "bing":
                # style=2 = Aerial; g=1780 is a common generation - for production
                # resolve the current generation + submap via the official REST:
                #   https://dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial?lat=..&long=..&key=..
                q = quadkey(cx + dx, cy + dy, zoom)
                url = (f"https://t0.tile.bing.net/t?a=0&g=1780&r=1"
                       f"&url=R{q}&style=2&lvl={zoom}")
                if key:
                    url += f"&key={key}"
            elif provider == "osm":
                url = f"https://tile.openstreetmap.org/{zoom}/{cx+dx}/{cy+dy}.png"
            else:
                sys.exit("provider must be bing|osm (Google: use Earth Engine, not scraping)")
            row.append(Image.open(io.BytesIO(get(url))).convert("RGB"))
        imgs.append(row)
    w, h = row[0].size
    canvas = Image.new("RGB", (w * 3, h * 3), "white")
    for j, r in enumerate(imgs):
        for i, im in enumerate(r):
            canvas.paste(im, (i * w, j * h))
    canvas.save(f"{outdir}/mosaic_z{zoom}.jpg", quality=92)
    print(f"saved {outdir}/mosaic_z{zoom}.jpg")
    if provider == "bing":
        print("NOTE: for production Bing use the official Imagery Metadata REST call")
        print("(dev.virtualearth.net/REST/v1/Imagery/Metadata/Aerial) to get the")
        print("current quadkey subdomain and submap metadata, then fetch tiles from")
        print("t{0-3}.tile.bing.net with your key - see MS Learn docs.")


# ----------------------------------------------------------------------
# MODE: spread  (field map sheet + GPS waypoints)
# ----------------------------------------------------------------------
def _bilinear(src, xs, ys):
    """Bilinear-sample 2-D array `src` at float pixel coords xs/ys."""
    H, W = src.shape
    xi = np.clip(np.floor(xs).astype(np.int64), 0, W - 2)
    yi = np.clip(np.floor(ys).astype(np.int64), 0, H - 2)
    fx = (xs - xi)[..., None] if xs.ndim == 1 else xs - xi
    fy = ys - yi
    top = src[yi, xi] * (1 - fx) + src[yi, xi + 1] * fx
    bot = src[yi + 1, xi] * (1 - fx) + src[yi + 1, xi + 1] * fx
    return (top * (1 - fy) + bot * fy).astype(np.float32)


def _bilinear3(src, xs, ys):
    out = np.empty(ys.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = _bilinear(src[..., c], xs, ys)
    return out


def _ramp(v, stops):
    """Map values v through color stops [(val, (r,g,b)), ...] -> HxWx3 uint8."""
    v = np.clip(v, stops[0][0], stops[-1][0])
    out = np.empty(v.shape + (3,), np.uint8)
    for k in range(len(stops) - 1):
        v0, c0 = stops[k]
        v1, c1 = stops[k + 1]
        m = (v >= v0) & (v <= v1)
        t = ((v[m] - v0) / (v1 - v0))[:, None]
        out[m] = (np.array(c0) * (1 - t) + np.array(c1) * t).astype(np.uint8)
    return out


def mode_spread(lat, lon, outdir, half_km):
    os.makedirs(outdir, exist_ok=True)
    import rasterio
    from pyproj import Transformer
    from rasterio.merge import merge
    from PIL import ImageDraw, ImageFont

    N = 1000                      # panel pixels
    half = half_km * 1000         # meters
    s = 2 * half / N              # m per pixel (2.5 at 2 km)
    t_fwd = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
    t_rev = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    t_utm = Transformer.from_crs("EPSG:3857", "EPSG:32611", always_xy=True)
    mx, my = t_fwd.transform(lon, lat)

    # ---- common output grid (x east, y north in 3857) ----
    J, I = np.mgrid[0:N, 0:N]
    X = mx - half + (I + 0.5) * s
    Y = my + half - (J + 0.5) * s

    # ---- Sentinel-2 2020 (3x3 z14, ~5.9 m/px) resampled to grid ----
    z = 14
    W2 = 40075016.686 / 2
    cx, cy = slippy(lon, lat, z)
    t4 = 40075016.686 / 2 ** z
    xc = (cx + 0.5) * t4 - W2          # tile center in EPSG:3857
    yc = W2 - (cy + 0.5) * t4
    imgs = []
    for dy in (-1, 0, 1):
        row = []
        for dx in (-1, 0, 1):
            url = ("https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/"
                   f"default/GoogleMapsCompatible/{z}/{cy+dy}/{cx+dx}.jpg")
            row.append(np.asarray(Image.open(io.BytesIO(get(url))).convert("RGB"),
                                  dtype=np.float32))
        imgs.append(row)
    s2c = np.concatenate([np.concatenate(r, axis=1) for r in imgs], axis=0)
    m2p = 256.0 / t4  # canvas px per meter
    xs = (X - xc) * m2p + s2c.shape[1] // 2
    ys = (yc - Y) * m2p + s2c.shape[0] // 2
    rgb = _bilinear3(s2c, xs, ys) / 255.0
    print(f"S2 grid: {rgb.shape[1]}x{rgb.shape[0]} px, {s:.2f} m/px")

    # ---- DEM (3x3 z14 tiles, 9.55 m) resampled to grid ----
    files = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            f = f"{outdir}/../data/dem14_{cx+dx}_{cy+dy}.tif"
            f = os.path.normpath(f)
            if not os.path.exists(f):
                os.makedirs(os.path.dirname(f), exist_ok=True)
                open(f, "wb").write(get(
                    f"https://s3.amazonaws.com/elevation-tiles-prod/v2/geotiff/{z}/{cx+dx}/{cy+dy}.tif"))
            files.append(f)
    ds = [rasterio.open(f) for f in files]
    darr, dtr = merge(ds, nodata=-32768)
    for d in ds:
        d.close()
    dem0 = darr[0].astype(float)
    dem0[dem0 < -30000] = np.nan
    dcol = (X - dtr.c) / dtr.a
    drow = (Y - dtr.f) / dtr.e
    dem = _bilinear(np.nan_to_num(dem0, nan=0.0), dcol, drow)
    print(f"DEM: target {dem[N//2, N//2]:.0f} m, range {dem.min():.0f}-{dem.max():.0f} m")

    # ---- slope / aspect / hillshade (native res, then resampled) ----
    res0 = abs(dtr.a)
    dy_, dx_ = np.gradient(np.nan_to_num(dem0, nan=0.0), res0, res0)
    slope0 = np.degrees(np.arctan(np.hypot(dx_, dy_)))
    brg0 = ((np.degrees(np.arctan2(-dy_, -dx_)) + 360) % 360 + 90) % 360
    za, azr = math.radians(45), math.radians(315)
    az0 = np.radians(brg0)
    hs0 = 1000 * (np.cos(za) * np.cos(np.radians(slope0)) +
                  np.sin(za) * np.sin(np.radians(slope0)) * np.cos(azr - az0))
    slope = _bilinear(slope0, dcol, drow)
    hs = _bilinear(hs0, dcol, drow)
    a_sin = _bilinear(np.sin(np.radians(brg0)), dcol, drow)
    a_cos = _bilinear(np.cos(np.radians(brg0)), dcol, drow)
    bearing = (np.degrees(np.arctan2(a_sin, a_cos)) + 360) % 360

    # ---- surface screen on the common grid ----
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mxx = np.maximum(np.maximum(R, G), B)
    mnn = np.minimum(np.minimum(R, G), B)
    V, S = mxx, (mxx - mnn) / np.maximum(mxx, 1e-6)
    BR = B / np.maximum(R, 1e-3)
    VEG = (G > R * 0.95) & (G >= B) & (S > 0.18) & (V > 0.08)
    BRIGHT = (V > 0.62) & (S < 0.22)
    DARK = (V < 0.16)
    TONE = (S < 0.32) & (V > 0.25) & (V < 0.62) & ~VEG & ~BRIGHT
    SOIL = (R > G) & (G > B * 0.95) & (S >= 0.32) & (V > 0.22) & ~VEG & ~BRIGHT & ~TONE
    UNCL = np.ones_like(R, bool)
    classes = np.zeros((N, N), np.int8)
    for name, m in [("BRIGHT", BRIGHT), ("TONE", TONE), ("VEG", VEG), ("SOIL", SOIL), ("DARK", DARK)]:
        classes[m & UNCL] = {"BRIGHT": 4, "TONE": 2, "VEG": 1, "SOIL": 3, "DARK": 5}[name]
        UNCL &= ~m
    dist_t = np.hypot((I - N // 2) * s, (J - N // 2) * s) / 1000.0
    m1 = dist_t <= 1.0
    print("classes @1km: " + "  ".join(
        f"{n} {100*np.mean(classes[m1] == c):.1f}%"
        for n, c in [("SOIL", 3), ("VEG", 1), ("TONE", 2), ("BRIGHT", 4), ("DARK", 5)]))
    print(f"B/R @1km: {np.mean(BR[m1]):.3f} (p99 {np.percentile(BR, 99):.3f})")

    # ---- render panels ----
    P = {
        "true": np.clip(rgb * 255, 0, 255).astype("uint8"),
        "hill": np.stack([hs] * 3, axis=-1).astype("uint8"),
        "elev": _ramp(dem, [(213, (232, 224, 200)), (280, (206, 186, 141)),
                            (350, (161, 136, 91)), (420, (116, 86, 51)), (484, (79, 54, 30))]),
        "slope": _ramp(slope, [(0, (245, 245, 220)), (5, (240, 210, 130)),
                               (10, (230, 150, 90)), (15, (200, 70, 60)),
                               (20, (150, 30, 40)), (30, (90, 10, 30))]),
        "aspect": None,
        "class": None,
        "br": None,
        "overlay": None,
        "context": None,
    }
    asp_cols = {0: (160, 160, 180), 1: (190, 180, 140), 2: (210, 170, 110), 3: (220, 150, 90),
                4: (220, 130, 90), 5: (215, 105, 95), 6: (205, 85, 95), 7: (190, 80, 120),
                8: (150, 90, 150), 9: (110, 100, 160), 10: (95, 120, 150), 11: (110, 140, 150)}
    bin_idx = (bearing // 30).astype(np.int64) % 12
    asp_lut = np.array([asp_cols[i] for i in range(12)], dtype=np.uint8)
    P["aspect"] = asp_lut[bin_idx]
    cls_lut = np.array([(120, 120, 120), (60, 160, 60), (190, 110, 200),
                        (190, 150, 90), (255, 255, 220), (30, 30, 30)], dtype=np.uint8)
    P["class"] = cls_lut[classes]
    b = np.clip((BR - 0.40) / (1.05 - 0.40), 0, 1) * 255
    P["br"] = np.stack([b, b, 255 - b], axis=-1).astype("uint8")
    # overlay: true color + TONE highlight + ring
    ov = P["true"].copy()
    ov[TONE] = (ov[TONE] * 0.45 + np.array([190, 110, 200]) * 0.55).astype("uint8")
    P["overlay"] = ov

    # ---- context panel (3x3 z13 ~14.7 km) ----
    zc = 13
    cxc, cyc = slippy(lon, lat, zc)
    tc = 40075016.686 / 2 ** zc
    cimgs = []
    for dy in (-1, 0, 1):
        row = []
        for dx in (-1, 0, 1):
            url = ("https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless-2020_3857/"
                   f"default/GoogleMapsCompatible/{zc}/{cyc+dy}/{cxc+dx}.jpg")
            row.append(Image.open(io.BytesIO(get(url))).convert("RGB"))
        cimgs.append(row)
    w, h = row[0].size
    ctx = Image.new("RGB", (w * 3, h * 3), "black")
    for j, r in enumerate(cimgs):
        for i, im in enumerate(r):
            ctx.paste(im, (i * w, j * h))
    ctx_a = np.asarray(ctx)
    m2p = 256 / tc  # px per meter
    W2c = 40075016.686 / 2
    xl = (cxc - 1) * tc - W2c      # canvas top-left in 3857
    yt = W2c - (cyc - 1) * tc
    rx0 = ((mx - half) - xl) * m2p
    ry0 = (yt - (my + half)) * m2p
    rx1 = ((mx + half) - xl) * m2p
    ry1 = (yt - (my - half)) * m2p
    P["context"] = ctx_a
    P["rect"] = (int(rx0), int(ry0), int(rx1), int(ry1))

    # ---- waypoints ----
    wps = []

    def add_wp(name, xi, yi, note, kind):
        lo, la = t_rev.transform(xi, yi)  # returns (lon, lat)
        e, n = t_utm.transform(xi, yi)
        de, dn = xi - mx, yi - my
        brg = (90 - math.degrees(math.atan2(dn, de))) % 360
        d = math.hypot(de, dn)
        wps.append(dict(name=name, lat=la, lon=lo, e=e, n=n,
                        elev=dem[int((my + half - yi) / s), int((xi - mx + half) / s)],
                        brg=brg, dist=d, note=note, kind=kind))

    add_wp("TGT", mx, my, f"Target point ({dem[N//2, N//2]:.0f} m on 10 m DEM). Verify the mapped surface/terrain match on site.", "target")
    # anomaly groups (100 m cells, flood fill)
    cell = 40
    nb = N // cell
    gridb = TONE[:nb * cell, :nb * cell].reshape(nb, cell, nb, cell).sum(axis=(1, 3))
    hot = gridb >= 20
    seen = np.zeros_like(hot, bool)
    groups = []
    for r in range(nb):
        for c in range(nb):
            if not hot[r, c] or seen[r, c]:
                continue
            q = [(r, c)]
            seen[r, c] = True
            comp = []
            while q:
                rr, cc = q.pop()
                comp.append((rr, cc))
                for drr, dcc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = rr + drr, cc + dcc
                    if 0 <= nr < nb and 0 <= nc < nb and hot[nr, nc] and not seen[nr, nc]:
                        seen[nr, nc] = True
                        q.append((nr, nc))
            if len(comp) >= 3:
                cr = sum(r for r, c in comp) / len(comp)
                cc2 = sum(c for r, c in comp) / len(comp)
                yi_c = my + half - (cr * cell + cell / 2) * s
                xi_c = mx - half + (cc2 * cell + cell / 2) * s
                if math.hypot(xi_c - mx, yi_c - my) < 1800:
                    groups.append((len(comp) * 0.01, xi_c, yi_c))
    for k, (area, xi_c, yi_c) in enumerate(sorted(groups, reverse=True)[:4]):
        add_wp(f"ANOM-{k+1}", xi_c, yi_c,
               f"Pale-tone cluster (S2 2020), ~{area:.2f} km2. Expect pale grey/whitish soil or exposed weathered rock, less scrub.", "anomaly")
    # ridge max
    ri, rj = np.unravel_index(np.argmax(dem), dem.shape)
    add_wp("RIDGE", mx - half + (rj + 0.5) * s, my + half - (ri + 0.5) * s,
           f"Local high {dem[ri, rj]:.0f} m (E of target). Expect highest ground in 4 km, rocky outcrops likely.", "ridge")
    # drainage trace (valley minima, 250 m rows)
    for k, off in enumerate((-1000, -600, -200, 200, 600, 1000)):
        yi = my + off
        ri_ = int((my + half - yi) / s)
        c0 = max(0, int((half - 300) / s))
        c1 = min(N, int((half + 300) / s))
        strip = dem[ri_, c0:c1]
        ci = c0 + int(np.argmin(strip))
        add_wp(f"D-{k+1}", mx - half + (ci + 0.5) * s, my + half - (ri_ + 0.5) * s,
               "Drainage trace (DEM valley min). Expect dry gravel/cobble channel; sample stream sediment here.", "drainage")
    # steep outcrops
    sl = slope.copy()
    for k in range(3):
        si, sj = np.unravel_index(np.argmax(sl), sl.shape)
        if sl[si, sj] < 22:
            break
        add_wp(f"STEEP-{k+1}", mx - half + (sj + 0.5) * s, my + half - (si + 0.5) * s,
               f"Slope {sl[si, sj]:.0f} deg - steepest rocky ground, best outcrop candidate in window.", "steep")
        i0, i1 = max(0, si - 60), min(N, si + 60)
        j0, j1 = max(0, sj - 60), min(N, sj + 60)
        sl[i0:i1, j0:j1] = 0

    import csv
    with open(f"{outdir}/field_waypoints.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["id", "name", "lat", "lon", "utm_e_11N", "utm_n_11N", "elev_m",
                     "bearing_deg_from_TGT", "dist_m", "check_notes"])
        for i, w in enumerate(wps):
            wr.writerow([f"WP{i+1}", w["name"], f"{w['lat']:.6f}", f"{w['lon']:.6f}",
                         f"{w['e']:.0f}", f"{w['n']:.0f}", f"{w['elev']:.0f}",
                         f"{w['brg']:.0f}", f"{w['dist']:.0f}", w["note"]])
    print(f"waypoints: {len(wps)} -> {outdir}/field_waypoints.csv")

    # ---- compose sheet ----
    M, GAP, TH, TF = 40, 16, 90, 120
    PW = N
    W_tot = M + 3 * PW + 2 * GAP + M
    H_tot = TH + 3 * (PW + 44 + GAP) + TF
    sheet = Image.new("RGB", (W_tot, H_tot), (24, 26, 30))
    dr = ImageDraw.Draw(sheet)
    try:
        f_title = ImageFont.load_default(size=34)
        f_sub = ImageFont.load_default(size=22)
        f_edge = ImageFont.load_default(size=19)
        f_small = ImageFont.load_default(size=17)
    except TypeError:
        f_title = f_sub = f_edge = f_small = ImageFont.load_default()

    titles = [
        ("1 · TRUE COLOR", "Sentinel-2 2020 cloudless, 10 m (EOX s2cloudless, CC BY-NC-SA)"),
        ("2 · HILLSHADE", "10 m DEM (USGS elevation-tiles-prod), SW sun 45°"),
        ("3 · ELEVATION", "10 m DEM, hypsometric tint, 213–484 m"),
        ("4 · SLOPE", "degrees, from 10 m DEM (median 7°, p90 15°)"),
        ("5 · ASPECT", "12 compass classes (S/SSE/SSW dominant)"),
        ("6 · SURFACE CLASSES", "HSV rules: soil / veg / pale-tone / crust / dark"),
        ("7 · B/R BLUE-SHIFT", "pale & Fe-depleted = yellow (background = blue)"),
        ("8 · TARGET OVERLAY", "pale-tone + 500/1000 m rings + field waypoints A–K"),
        ("9 · CONTEXT", "Sentinel-2 2020, 14.7 km view; white rect = 4×4 km window"),
    ]
    panels = ["true", "hill", "elev", "slope", "aspect", "class", "br", "overlay", "context"]

    def draw_grid(px0, py0):
        for off in (-1500, -1000, -500, 0, 500, 1000, 1500):
            xp = int((off + half) / s)
            yp = int((off + half) / s)
            _, la = t_rev.transform(mx, my + off)   # (lon, lat)
            lo, _ = t_rev.transform(mx + off, my)   # (lon, lat)
            if 0 <= xp < N:
                dr.line([(px0 + xp, py0), (px0 + xp, py0 + N)], fill=(235, 235, 235), width=1)
                dr.text((px0 + xp + 3, py0 + N - 21), f"{lo:.3f}", font=f_edge, fill=(0, 0, 0))
                dr.text((px0 + xp + 4, py0 + N - 22), f"{lo:.3f}", font=f_edge, fill=(255, 255, 255))
            if 0 <= yp < N:
                dr.line([(px0, py0 + yp), (px0 + N, py0 + yp)], fill=(235, 235, 235), width=1)
                dr.text((px0 + 4, py0 + yp + 2), f"{la:.3f}", font=f_edge, fill=(0, 0, 0))
                dr.text((px0 + 3, py0 + yp + 1), f"{la:.3f}", font=f_edge, fill=(255, 255, 255))

    def draw_target(px0, py0):
        c = N // 2
        dr.rectangle([px0 + c - 8, py0 + c - 8, px0 + c + 8, py0 + c + 8], outline=(255, 255, 255), width=3)
        dr.rectangle([px0 + c - 5, py0 + c - 5, px0 + c + 5, py0 + c + 5], fill=(255, 0, 0))

    letters = "ABCDEFGHIJKLMNOPQR"
    for p in range(9):
        r, c = divmod(p, 3)
        x0 = M + c * (PW + GAP)
        y0 = TH + r * (PW + 44 + GAP)
        dr.text((x0 + 6, y0 + 6), titles[p][0], font=f_title, fill=(255, 210, 90))
        dr.text((x0 + 6, y0 + 44), titles[p][1], font=f_small, fill=(200, 205, 215))
        img = Image.fromarray(P[panels[p]])
        if panels[p] == "context":
            drc = ImageDraw.Draw(img)
            ax, ay, bx, by = P["rect"]
            drc.rectangle([ax, ay, bx, by], outline=(255, 255, 255), width=3)
            drc.rectangle([ax - 2, ay - 2, bx + 2, by + 2], outline=(255, 60, 60), width=1)
            drc.text((bx + 8, ay + 2), "4x4 km study window", font=f_edge, fill=(255, 255, 255))
            img = img.resize((N, N))
        sheet.paste(img, (x0, y0 + 64))
        draw_grid(x0, y0 + 64)
        draw_target(x0, y0 + 64)
        if panels[p] == "overlay":
            cxp, cyp = x0 + N // 2, y0 + 64 + N // 2
            for rr, colr in ((500, (0, 200, 255)), (1000, (0, 255, 120))):
                rad = int(rr / s)
                dr.ellipse([cxp - rad, cyp - rad, cxp + rad, cyp + rad], outline=colr, width=2)
            for k, w in enumerate(wps):
                if w["name"] == "TGT":
                    continue
                wx, wy = t_fwd.transform(w["lon"], w["lat"])
                xi = int((wx - mx + half) / s)
                yi = int((my + half - wy) / s)
                if 8 < xi < N - 8 and 8 < yi < N - 8:
                    L = letters[k - 1]
                    dr.ellipse([x0 + xi - 14, y0 + 64 + yi - 14, x0 + xi + 14, y0 + 64 + yi + 14],
                               fill=(0, 0, 0), outline=(255, 255, 0), width=2)
                    dr.text((x0 + xi - 7, y0 + 64 + yi - 11), L, font=f_edge, fill=(255, 255, 0))
            dr.polygon([(x0 + N - 60, y0 + 94), (x0 + N - 75, y0 + 139), (x0 + N - 60, y0 + 126),
                        (x0 + N - 45, y0 + 139)], fill=(255, 255, 255), outline=(0, 0, 0))
            dr.text((x0 + N - 70, y0 + 148), "N", font=f_sub, fill=(255, 255, 255))
            sb, sby = x0 + 20, y0 + 64 + N - 34
            dr.rectangle([sb, sby, sb + 4 * int(250 / s), sby + 12], outline=(255, 255, 255), width=2)
            for i in range(4):
                xx = sb + i * int(250 / s)
                dr.rectangle([xx, sby, xx + int(250 / s) // 2, sby + 12],
                             fill=(255, 255, 255) if i % 2 == 0 else (0, 0, 0))
            dr.text((sb, sby - 20), "0 / 500 / 1000 m", font=f_small, fill=(255, 255, 255))
            for k, (nm, rgb_t) in enumerate([("veg", (60, 160, 60)), ("soil", (190, 150, 90)),
                                             ("pale-tone", (190, 110, 200)), ("crust", (255, 255, 220))]):
                yy = y0 + 84 + k * 22
                dr.rectangle([x0 + N - 160, yy, x0 + N - 142, yy + 16], fill=rgb_t, outline=(0, 0, 0))
                dr.text((x0 + N - 136, yy), nm, font=f_small, fill=(255, 255, 255))

    # header + footer
    dr.text((M, 16), f"FIELD MAP SPREAD — {lat:.6f}, {lon:.6f} · Arroyo San Isidro, San Quintín, Baja California, MX",
            font=f_title, fill=(255, 255, 255))
    dr.text((M, 58), "4×4 km window · 2.5 m/px · 500 m lat/lon grid · red square = target (326 m a.s.l.) · "
            "verify with field_waypoints.csv (bearings from TGT)", font=f_sub, fill=(180, 190, 205))
    fy = H_tot - TF + 10
    dr.text((M, fy), "Sources: Copernicus Sentinel-2 2020 cloudless composite via EOX (CC BY-NC-SA 4.0); USGS "
            "elevation-tiles-prod (SRTM-derived 10 m DEM); OSM. Expected geolocation accuracy: ±10–20 m (imagery), "
            "±3–8 m vertical (DEM).", font=f_small, fill=(150, 160, 175))
    dr.text((M, fy + 26), "Generated 2026-08-25 · mineral_pipeline.py spread · panels are non-redundant: "
            "1 color context · 2 shading · 3 height · 4 steepness · 5 slope direction · 6 surface classes · "
            "7 blue-shift anomaly · 8 integrated target view · 9 wider context", font=f_small, fill=(150, 160, 175))
    out_jpg = f"{outdir}/map_spread_4km.jpg"
    sheet.convert("RGB").save(out_jpg, quality=88, optimize=True)
    print(f"saved {out_jpg} ({sheet.size[0]}x{sheet.size[1]})")


# ----------------------------------------------------------------------
# alias modes: run the map generators as subcommands of this pipeline
# ----------------------------------------------------------------------
def _run_script(name):
    import subprocess
    s = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", name)
    return subprocess.call([sys.executable, s],
                           cwd=os.path.dirname(os.path.abspath(__file__)))


def mode_pins(*a, **k):
    return _run_script("hires_pins.py")


def mode_turquoise(*a, **k):
    return _run_script("turquoise_map.py")


# ----------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    for m in ("screen", "dem", "bands", "tiles", "spread", "pins", "turquoise"):
        p = sub.add_parser(m)
        p.add_argument("--lat", type=float, required=True)
        p.add_argument("--lon", type=float, required=True)
        p.add_argument("--outdir", default="./maps")
        if m in ("dem", "spread"):
            p.add_argument("--half-km", type=float, default=2.0)
        if m == "bands":
            p.add_argument("--days", type=int, default=365)
            p.add_argument("--max-cloud", type=int, default=10)
        if m == "tiles":
            p.add_argument("--zoom", type=int, default=16)
            p.add_argument("--provider", default="osm", choices=["bing", "osm"])
            p.add_argument("--key", default="")
    a = ap.parse_args()
    if a.mode in ("pins", "turquoise"):
        {"pins": mode_pins, "turquoise": mode_turquoise}[a.mode]()
        return
    {"screen": mode_screen, "dem": mode_dem, "bands": mode_bands, "tiles": mode_tiles,
     "spread": mode_spread}[a.mode](
        a.lat, a.lon, a.outdir,
        **({"half_km": a.half_km} if a.mode in ("dem", "spread") else {}),
        **({"days": a.days, "max_cloud": a.max_cloud} if a.mode == "bands" else {}),
        **({"zoom": a.zoom, "provider": a.provider, "key": a.key} if a.mode == "tiles" else {}))


if __name__ == "__main__":
    main()
