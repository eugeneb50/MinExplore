# Internet Archive document pipeline

Historical reports, mining journals, government bulletins, travel accounts and
scanned maps via the official `ia` tool. Records follow
`schemas/document_record.schema.json`.

## Search (English + Spanish, historical terminology)

```bash
pipx install internetarchive

ia search \
  'mediatype:texts AND ("Baja California" OR "Lower California") AND
   (mining OR geology OR mineral OR mines)' \
  --field=identifier --field=title --field=date --field=creator \
  --field=licenseurl

ia search \
  '"Baja California" AND (gold OR silver OR copper OR pegmatite)' \
  --fts --field=identifier --field=title --field=date

ia metadata ITEM_IDENTIFIER
ia download ITEM_IDENTIFIER --glob='*_djvu.txt' --glob='*_djvu.xml' \
  --glob='*.pdf' --checksum
```

Terms: `Baja California`, `Lower California`, `península de California`,
`minas`, `distrito minero`, `criadero mineral`, `veta`, `placer`,
`placeres auríferos`, `labores mineras`, `memoria minera`,
`boletín geológico`, `informe de reconocimiento`. Also historic ranch, arroyo,
sierra, mission, municipality and mining-district names.

## Per-document procedure

1. Capture item metadata + rights. 2. Hash the original file. 3. Preserve raw
   OCR. 4. Map OCR text to page numbers. 5. Extract candidate place / geology /
   commodity / assay / structural references. 6. Assign extraction confidence.
7. Human inspects the page image. 8. Save a page-level citation.
9. Geocode uncertain names as **polygons or approximate areas with
   `geometry_precision_m`** — never invented exact points.

## Rights rule

Availability on IA ≠ permission to republish. Retain metadata, page references
and minimal supporting excerpts; verify each item's rights. Same pattern for
USGS Publications Warehouse (REST-like JSON) and Library of Congress
(structured + geospatial APIs): for old maps record control points,
transformation type, residual error, final RMSE, and unreliable areas.
