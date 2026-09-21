# Baja Mineral Explorer — site

Self-contained static site (no build step, no backend).

## Run locally
```bash
cd site
python3 -m http.server 8080
# open http://localhost:8080
```
Or open `index.html` directly (map tiles need internet; everything else works offline).

## Deploy
Upload the whole `site/` folder to any static host (Netlify, Vercel, GitHub Pages, S3, cPanel). No server config needed.

## Before going live — edit these
1. **Domain** (for SEO to actually work):
   - `index.html`: the `SITE_URL` constant in the `<script>` block (top of the first JS section)
   - `index.html` `<head>`: the `<link rel="canonical">` + 5 `<link rel="alternate" hreflang=...>` lines
   - `index.html` JSON-LD blocks (the two `application/ld+json` scripts): every `https://bajamineral.example.org/...` URL
   - `robots.txt` and `sitemap.xml`
2. **Member access key**: `MEMBER_KEY` constant in `index.html` (currently `BAJA-PROSPECT-2026`).
   Members unlock the coordinate runner + full map gallery by entering it (stored in their browser localStorage).

## What's inside
```
index.html        single page: hero, 3 target cards, method, data, FAQ (AEO),
                  members (gate + coordinate runner + gallery), footer.
                  i18n: EN (default) / ES / 中文 / РУ (switcher, ?lang= param,
                  persisted, html lang + title + meta description localized)
vendor/leaflet.js  Leaflet 1.9.4 (offline-capable map library)
vendor/leaflet.css
maps/              14 images (pin sheets 1.03 m/px, 0.52 m/px detail, 4×4 km
                   field sheets, corridor overview, T1 layer products)
maps/PIN_POINTS.csv                    36 field pins (GPS-importable)
maps/mine_inventory_elaguajito.csv     14 documented SGM Cu–Fe workings
llms.txt           plain-text summary for LLM/AEO/GEO crawlers
robots.txt         crawler rules + sitemap pointer
sitemap.xml        URL sitemap with hreflang alternates
```

## SEO / AEO / GEO features
- Canonical + hreflang (en/es/zh/ru) + sitemap
- Open Graph + Twitter cards
- JSON-LD: Organization, WebSite (SearchAction for coordinates), WebApplication, ItemList (targets), BreadcrumbList
- JSON-LD FAQPage (6 Q&A) mirroring the visible FAQ — answer-first phrasing for answer engines
- Semantic HTML5, single H1, descriptive alt text, lazy-loaded gallery
- llms.txt for generative-engine consumption

## Coordinate runner (member feature)
- Leaflet map: Esri World Imagery (default) / OpenTopoMap / Sentinel-2 2020 layers
- Layers: 3 targets (squares), 14 documented workings (triangles), 36 pins (colored circles)
- Per point: elevation (open-elevation API), nearest target/pin/work with distance + bearing, corridor distance
- Deep links: `?lat=..&lon=..` and `#m=lat,lon` (share button copies)

## Regenerate maps
Maps are outputs of the pipeline in `../mineral_pipeline.py`:
```bash
cd ..
python3 mineral_pipeline.py spread --lat <LAT> --lon <LON> --half-km 2 --outdir maps/<t>
python3 mineral_pipeline.py pins        # -> maps/pins/  (then copy to site/maps/)
python3 mineral_pipeline.py turquoise   # -> maps/turquoise_prospect_map.jpg
```

## License
Content: CC BY-NC-SA 4.0. Imagery © source providers (Copernicus S2 CC BY-NC-SA; Esri World Imagery research use; SRTM public domain). Not affiliated with SGM/CONAGUA/Government of Mexico.
