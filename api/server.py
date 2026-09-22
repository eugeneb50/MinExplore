#!/usr/bin/env python3
"""Baja Mineral Explorer API + static server (stdlib only, no third-party deps).

Serves ../site/ and exposes:
  GET  /api/health                       -> {ok, pipeline_version}
  POST /api/analyze {lat, lon}           -> coordinate evidence pack
                                           (same payload as `evidence-pack` mode)
  POST /api/jobs {lat, lon, sku, consent} -> create paid-analysis job (queued)
  GET  /api/jobs/{id}                    -> job status
  POST /api/webhooks/payments            -> STUB: shared-secret placeholder only.
      Requires FEE_WEBHOOK_SECRET env and X-Webhook-Secret match; replace with
      provider signature verification before accepting money (docs/FEE_FLOW.md).

Free-tier rate limit: 30 /api/analyze calls per IP per hour (in-memory).
Paid deliverables must use commercially-clean inputs only (docs/TERMS.md).

Run:  python3 api/server.py [--port 8080]
Test: python3 -m unittest tests.test_api  (spins up localhost server)
"""
import argparse
import csv
import json
import math
import os
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DIR = os.path.join(ROOT, "site")
JOBS_PATH = os.environ.get("MINEXPLORE_JOBS",
                            os.path.join(ROOT, "jobs", "jobs.jsonl"))
RATE_LIMIT = 30
RATE_WINDOW_S = 3600

import sys
sys.path.insert(0, ROOT)
from src.frontier import all_frontier  # noqa: E402
from src.scores import EVIDENCE, PIPELINE_VERSION, all_split  # noqa: E402
from src.uncertainty import all_coverage  # noqa: E402

MIME = {".html": "text/html", ".js": "text/javascript", ".css": "text/css",
        ".json": "application/json", ".geojson": "application/geo+json",
        ".csv": "text/csv", ".png": "image/png", ".jpg": "image/jpeg",
        ".webp": "image/webp", ".xml": "text/xml", ".txt": "text/plain"}

TARGETS = {"T1": (29.903605, -115.383656), "T2": (30.048522, -115.236173),
           "T3": (30.025725, -115.286885)}
SKUS = ("tier1-pack", "tier2-frontier")

_hits = {}


def _haversine_km(a, b, c, d):
    p1, p2 = math.radians(a), math.radians(c)
    dp, dl = p2 - p1, math.radians(d - b)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def _bearing(a, b, c, d):
    p1, p2 = math.radians(a), math.radians(c)
    dl = math.radians(d - b)
    y = math.sin(dl) * math.cos(p2)
    x = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360


def _pins():
    with open(os.path.join(ROOT, "maps", "PIN_POINTS.csv"), newline="",
              encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _nearest(lat, lon, rows, la_key, lo_key, id_key):
    best, bd = None, float("inf")
    for r in rows:
        try:
            d = _haversine_km(lat, lon, float(r[la_key]), float(r[lo_key]))
        except (ValueError, TypeError):
            continue
        if d < bd:
            bd, best = d, r
    if best is None:
        return None
    return {"id": best[id_key], "dist_km": round(bd, 2),
            "bearing_deg": round(_bearing(lat, lon, float(best[la_key]),
                                          float(best[lo_key])))}


def build_evidence_pack(lat, lon):
    """Coordinate evidence pack (mirrors `evidence-pack` pipeline mode)."""
    split, cov, fro = all_split(), all_coverage(), all_frontier()
    pins = _pins()
    return {
        "coordinate": {"lat": lat, "lon": lon, "crs": "EPSG:4326"},
        "pipeline_version": PIPELINE_VERSION,
        "nearest_target": _nearest(
            lat, lon, [{"id": t, "la": la, "lo": lo} for t, (la, lo) in TARGETS.items()],
            "la", "lo", "id"),
        "nearest_pin": _nearest(lat, lon, pins, "latitude", "longitude", "record_id"),
        "targets": {t: {"prospectivity": s["prospectivity"],
                        "feasibility": s["feasibility"],
                        "uncertainty": cov[t], "frontier": fro[t],
                        "evidence": EVIDENCE[t]} for t, s in split.items()},
        "provenance_trail": "target -> derived evidence -> transformation -> "
                            "source asset -> publisher/license (sources/registry.json)",
        "disclaimer": "Desk-study evidence pack. Relative evidence scores only; "
                      "field validation required. Not investment advice.",
    }


def _read_jobs():
    if not os.path.exists(JOBS_PATH):
        return []
    with open(JOBS_PATH, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _append_job(job):
    os.makedirs(os.path.dirname(JOBS_PATH), exist_ok=True)
    with open(JOBS_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(job) + "\n")


def _set_job_status(job_id, status):
    jobs = _read_jobs()
    for j in jobs:
        if j["id"] == job_id:
            j["status"] = status
    os.makedirs(os.path.dirname(JOBS_PATH), exist_ok=True)
    with open(JOBS_PATH, "w", encoding="utf-8") as f:
        for j in jobs:
            f.write(json.dumps(j) + "\n")


def _rate_ok(ip):
    now = time.time()
    window = [t for t in _hits.get(ip, []) if now - t < RATE_WINDOW_S]
    _hits[ip] = window
    if len(window) >= RATE_LIMIT:
        return False
    window.append(now)
    return True


class Handler(BaseHTTPRequestHandler):
    server_version = "BajaMineralAPI/3.0"

    def log_message(self, format, *args):
        pass

    def _send(self, code, obj, ctype="application/json"):
        body = obj if isinstance(obj, bytes) else json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
        except ValueError:
            return {}
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n) or b"{}")
        except (ValueError, OSError):
            return {}

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/health":
            return self._send(200, {"ok": True, "pipeline_version": PIPELINE_VERSION})
        if path.startswith("/api/jobs/"):
            job_id = path.rsplit("/", 1)[-1]
            for j in _read_jobs():
                if j["id"] == job_id:
                    return self._send(200, j)
            return self._send(404, {"error": "unknown job"})
        # static files from site/
        rel = path.lstrip("/") or "index.html"
        if ".." in rel:
            return self._send(400, {"error": "bad path"})
        full = os.path.join(SITE_DIR, rel)
        if os.path.isdir(full):
            full = os.path.join(full, "index.html")
        if not os.path.exists(full):
            return self._send(404, {"error": "not found"})
        ext = os.path.splitext(full)[1].lower()
        with open(full, "rb") as f:
            self._send(200, f.read(), MIME.get(ext, "application/octet-stream"))

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        ip = self.client_address[0]
        if path == "/api/analyze":
            if not _rate_ok(ip):
                return self._send(429, {"error": "free-tier rate limit (30/hour)"})
            data = self._body()
            try:
                lat, lon = float(data["lat"]), float(data["lon"])
            except (KeyError, TypeError, ValueError):
                return self._send(400, {"error": "lat/lon required as numbers"})
            if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                return self._send(400, {"error": "coordinates out of range"})
            return self._send(200, build_evidence_pack(lat, lon))
        if path == "/api/jobs":
            data = self._body()
            if not data.get("consent"):
                return self._send(400, {"error": "consent checkbox required (docs/TERMS.md)"})
            if data.get("sku") not in SKUS:
                return self._send(400, {"error": f"sku must be one of {list(SKUS)}"})
            try:
                lat, lon = float(data["lat"]), float(data["lon"])
            except (KeyError, TypeError, ValueError):
                return self._send(400, {"error": "lat/lon required as numbers"})
            job = {"id": f"job-{int(time.time())}-{os.getpid()}",
                   "sku": data["sku"], "lat": lat, "lon": lon,
                   "status": "queued", "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "note": "Manual fulfillment until demand justifies automation (docs/FEE_FLOW.md)."}
            _append_job(job)
            return self._send(200, job)
        if path == "/api/webhooks/payments":
            # STUB — replace with provider signature verification before live use.
            secret = os.environ.get("FEE_WEBHOOK_SECRET", "")
            if not secret or self.headers.get("X-Webhook-Secret") != secret:
                return self._send(403, {"error": "webhook not wired (set FEE_WEBHOOK_SECRET + provider verification)"})
            data = self._body()
            if data.get("event") == "paid" and data.get("job_id"):
                _set_job_status(data["job_id"], "paid")
                return self._send(200, {"ok": True})
            return self._send(400, {"error": "event/job_id required"})
        return self._send(404, {"error": "not found"})

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Webhook-Secret")
        self.end_headers()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    a = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print(f"serving site/ + api on http://127.0.0.1:{a.port} (stdlib only)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
