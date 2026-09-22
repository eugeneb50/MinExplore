#!/usr/bin/env python3
"""Build small WebP/AVIF previews for the gallery (Workstream 9).

Gallery thumbs + lightbox load `*-preview.webp` (~800 px, q70);
full-resolution JPGs stay linked as separate downloads.
PNG layer products are small enough to serve directly (no preview).
Requires Pillow (WebP support included in modern wheels).
"""
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPS = os.path.join(ROOT, "site", "maps")

TARGETS = ["t1_pins", "t2_pins", "t2_mass_inset_z18", "t3_pins",
           "zoneA_pins", "zoneB_pins", "zoneC_pins",
           "t1_spread", "t2_spread", "t3_spread", "turquoise_map"]


def main():
    for name in TARGETS:
        src = os.path.join(MAPS, name + ".jpg")
        dst = os.path.join(MAPS, name + "-preview.webp")
        if not os.path.exists(src):
            print(f"SKIP {name} (no source)")
            continue
        im = Image.open(src).convert("RGB")
        im.thumbnail((800, 800), Image.Resampling.LANCZOS)
        im.save(dst, "WEBP", quality=70, method=6)
        s0 = os.path.getsize(src) / 1024
        s1 = os.path.getsize(dst) / 1024
        print(f"{name}: {s0:.0f} KB -> preview {s1:.0f} KB ({100*s1/s0:.0f}%)")


if __name__ == "__main__":
    main()
