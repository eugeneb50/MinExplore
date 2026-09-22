"""Validator + export tests (Workstream 7)."""
import unittest

from src.export import build_field_package, records_to_geojson
from src.validate import find_duplicate_locations, validate_records


GOOD = [
    {"record_id": "T1-TGT", "target_id": "T1", "latitude": 29.903605,
     "longitude": -115.383656, "crs": "EPSG:4326", "feature_type": "target",
     "source": "SGM H11-B85", "source_page": "sheet", "source_date": "2009",
     "coordinate_accuracy_m": "20", "derivation_method": "desk pick",
     "confidence": "Medium", "field_action": "verify", "license": "CC BY-NC-SA 4.0",
     "created_at": "2026-08-25", "pipeline_version": "2.0.0"},
    {"record_id": "T1-01", "target_id": "T1", "latitude": 29.906097,
     "longitude": -115.390962, "crs": "EPSG:4326", "feature_type": "pale",
     "source": "EOX S2", "source_page": "tile", "source_date": "2020",
     "coordinate_accuracy_m": "20", "derivation_method": "RGB heuristic",
     "confidence": "Low", "field_action": "chips", "license": "CC BY-NC-SA 4.0",
     "created_at": "2026-08-25", "pipeline_version": "2.0.0"},
]


class TestValidate(unittest.TestCase):
    def test_good_passes(self):
        errs = validate_records(GOOD, check_scores=False)
        self.assertEqual(errs, [])

    def test_duplicate_id(self):
        recs = GOOD + [dict(GOOD[0])]
        errs = validate_records(recs, check_scores=False)
        self.assertTrue(any("duplicate record_id" in e for e in errs))

    def test_bad_coords(self):
        recs = [dict(GOOD[0], latitude=999)]
        errs = validate_records(recs, check_scores=False)
        self.assertTrue(any("latitude" in e for e in errs))

    def test_missing_provenance(self):
        recs = [dict(GOOD[0], source="")]
        errs = validate_records(recs, check_scores=False)
        self.assertTrue(any("provenance" in e or "required column" in e for e in errs))

    def test_unknown_feature_type(self):
        recs = [dict(GOOD[0], feature_type="gold")]
        errs = validate_records(recs, check_scores=False)
        self.assertTrue(any("feature_type" in e for e in errs))

    def test_duplicate_location_is_warning(self):
        recs = GOOD + [dict(GOOD[1], record_id="T1-99")]
        self.assertEqual(validate_records(recs, check_scores=False), [])
        self.assertTrue(find_duplicate_locations(recs))


class TestExport(unittest.TestCase):
    def test_geojson_coords_order(self):
        gj = records_to_geojson(GOOD)
        self.assertEqual(gj["features"][0]["geometry"]["coordinates"],
                         [-115.383656, 29.903605])

    def test_field_package_filters_target(self):
        blob = build_field_package("T1", GOOD, "test note")
        self.assertTrue(blob.startswith(b"PK"))
        import io
        import zipfile
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            self.assertEqual(set(z.namelist()),
                             {"T1_pins.geojson", "T1_pins.csv", "README.txt"})


if __name__ == "__main__":
    unittest.main()
