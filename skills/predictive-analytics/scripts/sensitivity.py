#!/usr/bin/env python3
"""Tier 1 prospective analysis: what-if sensitivity over the deterministic model.

Reads src/scores.py (never writes it) and reports, per target:
  - one-factor perturbations (+/-2, clamped to [0,10])
  - weight robustness (+/-5 per weight, renormalized)
  - flip thresholds (how far one factor must move to change the leader)
  - value-of-information ranking (--voi): max rank movement when a
    Low-confidence factor sweeps its full plausible range

Stdlib only. Deterministic. Safe for CI.
Runs on one side of the v3 split at a time (--side prospectivity|feasibility;
legacy --side blended runs the frozen v2 mean).
Usage: python3 skills/predictive-analytics/scripts/sensitivity.py [--target T2] [--voi] [--json] [--side prospectivity]
"""
import argparse
import copy
import json
import sys

sys.path.insert(0, ".")
from src.scores import (COMMITTED_SCORES, COMMITTED_V3, EVIDENCE,
                        FEASIBILITY_WEIGHTS, PROSPECTIVITY_WEIGHTS, WEIGHTS)

SIDES = {
    "prospectivity": (PROSPECTIVITY_WEIGHTS,
                      {t: v["prospectivity"] for t, v in COMMITTED_V3.items()}),
    "feasibility": (FEASIBILITY_WEIGHTS,
                    {t: v["feasibility"] for t, v in COMMITTED_V3.items()}),
    "blended": (WEIGHTS, dict(COMMITTED_SCORES)),  # v2 legacy
}


def rescored(evidence, weights):
    out = {}
    for t, ev in evidence.items():
        total = sum(weights[f] for f in weights)
        out[t] = round(sum(weights[f] * ev[f]["score"] for f in weights) / total, 1)
    return out


def leader(scores):
    return max(scores, key=lambda t: scores[t])


def perturb(evidence, target, factor, delta):
    ev = copy.deepcopy(evidence)
    s = ev[target][factor]["score"]
    ev[target][factor]["score"] = max(0, min(10, s + delta))
    return ev


def tornado(target, weights, committed):
    base = committed[target]
    rows = []
    for f in weights:
        lo = rescored(perturb(EVIDENCE, target, f, -2), weights)[target]
        hi = rescored(perturb(EVIDENCE, target, f, +2), weights)[target]
        rows.append({"factor": f, "base": base, "minus": lo, "plus": hi,
                     "swing": round(hi - lo, 2)})
    return sorted(rows, key=lambda r: -r["swing"])


def weight_robustness(weights, delta=5):
    base = rescored(EVIDENCE, weights)
    out = []
    for f in weights:
        for d in (-delta, delta):
            w = dict(weights)
            w[f] = max(1, w[f] + d)
            s = rescored(EVIDENCE, w)
            out.append({"weight": f, "delta": d, "scores": s,
                        "leader": leader(s),
                        "leader_changed": leader(s) != leader(base)})
    return out


def flip_threshold(target, weights, committed, challenger=None):
    """Min single-factor move needed for `challenger` to tie/beat `target`."""
    base = rescored(EVIDENCE, weights)
    chal = challenger or max([t for t in base if t != target],
                             key=lambda t: base[t])
    gap = round(base[target] - base[chal], 2)
    results = []
    for f in weights:
        # move challenger up and target down symmetricSearch
        for step in range(1, 21):
            ev = perturb(perturb(EVIDENCE, chal, f, step * 0.5), target, f, -step * 0.5)
            s = rescored(ev, weights)
            if s[chal] >= s[target]:
                results.append({"factor": f, "move_each_way": round(step * 0.5, 1),
                                "note": f"{chal} up / {target} down on {f}"})
                break
    return {"gap": gap, "challenger": chal, "paths": sorted(results, key=lambda r: r["move_each_way"])}


def voi_ranking(weights):
    """Rank Low-confidence factors by max rank swing across [0,10]."""
    rows = []
    for t, ev in EVIDENCE.items():
        for f, meta in ev.items():
            if meta["confidence"] != "Low":
                continue
            lo = rescored(perturb(EVIDENCE, t, f, -10), weights)[t]
            hi = rescored(perturb(EVIDENCE, t, f, 10), weights)[t]
            rows.append({"target": t, "factor": f, "tag": meta["tag"],
                         "swing": round(hi - lo, 2),
                         "field_test": meta["note"]})
    return sorted(rows, key=lambda r: -r["swing"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="T2")
    ap.add_argument("--voi", action="store_true",
                    help="value-of-information ranking across all targets")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--side", default="prospectivity",
                    choices=sorted(SIDES),
                    help="v3 split side to analyze (default: prospectivity)")
    a = ap.parse_args()
    t = a.target
    weights, committed = SIDES[a.side]
    if a.voi:
        report = {"side": a.side, "voi_ranking": voi_ranking(weights),
                  "committed": committed}
    else:
        report = {"side": a.side, "target": t, "committed": committed,
                  "tornado_pm2": tornado(t, weights, committed),
                  "weight_robustness_pm5": weight_robustness(weights),
                  "flip": flip_threshold(t, weights, committed)}
    if a.json:
        print(json.dumps(report, indent=1))
    else:
        if a.voi:
            print(f"VALUE OF INFORMATION [{a.side}] (Low-confidence factors by max rank swing):")
            for r in report["voi_ranking"]:
                print(f"  {r['target']} {r['factor']:20s} swing {r['swing']:4.1f} [{r['tag']}]")
                print(f"    -> test: {r['field_test']}")
        else:
            print(f"TORNADO [{a.side}] for {t} (factor +/-2, committed {committed[t]}):")
            for r in report["tornado_pm2"]:
                print(f"  {r['factor']:20s} {r['minus']:4.1f} .. {r['plus']:4.1f}  (swing {r['swing']:.1f})")
            print("WEIGHT ROBUSTNESS (+/-5, leader changes only):")
            for r in report["weight_robustness_pm5"]:
                if r["leader_changed"]:
                    print(f"  {r['weight']} {r['delta']:+d}: leader -> {r['leader']} {r['scores']}")
            if not any(r["leader_changed"] for r in report["weight_robustness_pm5"]):
                print("  leader stable under all single-weight +/-5 shifts")
            f = report["flip"]
            if f["gap"] <= 0:
                print(f"FLIP: {f['challenger']} already leads by {-f['gap']} — no flip needed on this side.")
            else:
                print(f"FLIP: {f['challenger']} trails by {f['gap']}; cheapest single-factor paths:")
                for p in f["paths"][:3]:
                    print(f"  {p['note']} (±{p['move_each_way']})")


if __name__ == "__main__":
    main()
