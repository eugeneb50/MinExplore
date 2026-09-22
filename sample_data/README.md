# Sample DataKit

Tiny runnable subset: 6 T2 pin records (CSV+GeoJSON), 2 mine records, and the published scoring model with evidence.

```bash
python3 -m unittest         # runs scorer + validator tests
python3 src/validate.py sample_data/pins_sample.csv
```
Full data: `maps/PIN_POINTS.*`. Schema: `schemas/pins.schema.json`.
