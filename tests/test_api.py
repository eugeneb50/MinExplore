"""API contract tests: spin up api/server.py on localhost (stdlib only)."""
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import sys
import os
import tempfile
os.environ["MINEXPLORE_JOBS"] = os.path.join(tempfile.mkdtemp(), "jobs.jsonl")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.server import Handler  # noqa: E402


def _call(method, path, body=None, port=18311):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=data,
                                 method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = ThreadingHTTPServer(("127.0.0.1", 18311), Handler)
        cls.t = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.t.start()

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()

    def test_health(self):
        code, body = _call("GET", "/api/health")
        self.assertEqual(code, 200)
        self.assertTrue(body["ok"])

    def test_analyze_contract(self):
        code, pack = _call("POST", "/api/analyze",
                           {"lat": 30.048522, "lon": -115.236173})
        self.assertEqual(code, 200)
        for key in ("coordinate", "pipeline_version", "nearest_target",
                    "nearest_pin", "targets", "provenance_trail", "disclaimer"):
            self.assertIn(key, pack)
        self.assertEqual(pack["nearest_target"]["id"], "T2")
        t2 = pack["targets"]["T2"]
        self.assertIn("prospectivity", t2)
        self.assertIn("feasibility", t2)
        self.assertNotIn("probability", json.dumps(pack).lower().replace(
            "not a probability", "").replace("not probabilities", ""))

    def test_analyze_bad_input(self):
        code, _ = _call("POST", "/api/analyze", {"lat": 999, "lon": 0})
        self.assertEqual(code, 400)
        code, _ = _call("POST", "/api/analyze", {})
        self.assertEqual(code, 400)

    def test_jobs_require_consent_and_sku(self):
        code, _ = _call("POST", "/api/jobs",
                        {"lat": 30.0, "lon": -115.0, "sku": "tier1-pack"})
        self.assertEqual(code, 400)
        code, _ = _call("POST", "/api/jobs",
                        {"lat": 30.0, "lon": -115.0, "sku": "nope", "consent": True})
        self.assertEqual(code, 400)

    def test_jobs_roundtrip(self):
        code, job = _call("POST", "/api/jobs",
                          {"lat": 30.0, "lon": -115.0, "sku": "tier1-pack",
                           "consent": True})
        self.assertEqual(code, 200)
        self.assertEqual(job["status"], "queued")
        code, got = _call("GET", f"/api/jobs/{job['id']}")
        self.assertEqual(code, 200)
        self.assertEqual(got["id"], job["id"])

    def test_webhook_unwired(self):
        code, _ = _call("POST", "/api/webhooks/payments", {"event": "paid"})
        self.assertEqual(code, 403)


if __name__ == "__main__":
    unittest.main()
