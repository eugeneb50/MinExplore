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
2. **Source repo link**: the hero “View source code” button still points at `https://github.com/example/baja-mineral` — replace with the real repo URL (also linked from the scores/build sections).
3. **CDN/cache**: serve `maps/*-preview.webp` with long `Cache-Control: public, max-age=31536000, immutable` (content-hashed by regeneration); full-res JPGs `max-age=86400`. Any static host or CDN works — no server config required beyond headers.

## What's inside
```
index.html        single page: hero (pipeline framing + reviewer links), 3 target cards,
                   method (resolution truth), published scoring model, data (CSV+GeoJSON),
                   engineering tradeoffs, FAQ (AEO), public demo (runner + gallery), footer.
                   i18n: EN (default) / ES / 中文 / РУ (switcher, ?lang= param,
                   persisted, html lang + title + meta description localized;
                   EN leads after the 2026-09 pass, other locales pending)
vendor/leaflet.js  Leaflet 1.9.4 (offline-capable map library)
vendor/leaflet.css
maps/              14 images (pin sheets, 0.52 m/px rendered detail, 4×4 km
                    field sheets, corridor overview, T1 layer products)
                    + *-preview.webp gallery thumbnails (~5% weight, see
                    ../scripts/make_previews.py)
maps/PIN_POINTS.{csv,geojson}        36 field pins, v2 unique IDs + provenance
maps/mine_inventory_elaguajito.{csv,geojson}  14 documented SGM Cu–Fe workings
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

## Coordinate runner (public demo, no login)

- 5 analyses/visitor, browser-local quota (`localStorage bme_demo_count`) + “Load example coordinate” (T2)
- Leaflet map: Esri World Imagery (default) / OpenTopoMap / Sentinel-2 2020 viewing composite + low-bandwidth toggle (S2 only)
- Layers: 3 targets (squares), 14 documented workings (triangles), 36 pins v2 IDs (colored circles)
- Per point: elevation (open-elevation API, with loading/error states), nearest target/pin/work with distance + bearing, corridor distance, JSON + GeoJSON output, downloadable field package (JS Blob)
- Deep links: `?lat=..&lon=..` and `#m=lat,lon` (share button copies)
- Gallery serves `*-preview.webp` first; full-res JPGs are separate download links (lazy-loaded)

## API key vault (bring-your-own-key, local-only)

- Settings panel at the bottom of `#demo`: provider select (OpenRouter / OpenAI / custom OpenAI-compatible endpoint), obscured key entry with show/hide toggle, optional passphrase, Save / Test / Lock / Forget.
- Storage: `localStorage bme_key_<provider>` holds `{enc, salt, iv, data}` — AES-256-GCM (WebCrypto, PBKDF2-SHA-256 100k iterations) with a passphrase, XOR-pad **obfuscation** without one (UI labels this honestly: obfuscated ≠ encrypted). Plaintext keys live only in page memory, cleared on Lock/pagehide; key/password fields are cleared from the DOM after Save.
- No backend exists, so keys never leave the browser except inside a Test call's `Authorization` header straight to the provider (`/auth/key` on OpenRouter, `/models` on OpenAI). No consumer is wired yet — future callers must use `Vault.withKey(provider, fn)`, never storage directly.
- Advise scoped/limited keys (OpenRouter supports per-key spend caps) and revocation on shared machines.

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
