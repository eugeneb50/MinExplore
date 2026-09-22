#!/usr/bin/env python3
"""Tier 2 predictive analysis: Monte Carlo rank distributions.

Samples factor scores with confidence-scaled Gaussian noise, truncated to
[0,10], and recomputes the deterministic weighted rank per draw:
  Low confidence    -> N(0, 2.0)
  Medium confidence -> N(0, 1.0)
(High would be N(0, 0.5); no High factors exist yet.)

These scales are DOCUMENTED CONVENTIONS, not measured errors — every report
must say so. Outputs are rank distributions, NOT probabilities of
mineralization. Requires numpy. Local-only; write results under predictive/
(gitignored) — never into maps/, site/, or committed data.

Usage: python3 skills/predictive-analytics/scripts/rank_distributions.py
         --n 10000 --seed 7 [--out predictive/t2_dist.json] [--json]
         [--side prospectivity|feasibility|blended]
Runs on one side of the v3 split at a time (default: prospectivity).
"""
import argparse
import hashlib
import json
import sys

sys.path.insert(0, ".")
from src.scores import (COMMITTED_SCORES, COMMITTED_V3, EVIDENCE,
                        FEASIBILITY_WEIGHTS, PROSPECTIVITY_WEIGHTS, WEIGHTS)

try:
    import numpy as np
except ImportError:
    sys.exit("numpy is required for Tier 2 (pip install numpy). Tier 1 needs stdlib only.")

NOISE = {"Low": 2.0, "Medium": 1.0, "High": 0.5}
SIDES = {
    "prospectivity": (PROSPECTIVITY_WEIGHTS,
                      {t: v["prospectivity"] for t, v in COMMITTED_V3.items()}),
    "feasibility": (FEASIBILITY_WEIGHTS,
                    {t: v["feasibility"] for t, v in COMMITTED_V3.items()}),
    "blended": (WEIGHTS, dict(COMMITTED_SCORES)),  # v2 legacy
}


def side_weights(side):
    weights, _ = SIDES[side]
    factors = list(weights)
    w = np.array([weights[f] for f in factors], dtype=float)
    return factors, w


def evidence_fingerprint(factors):
    h = hashlib.sha256()
    for t in sorted(EVIDENCE):
        for f in factors:
            m = EVIDENCE[t][f]
            h.update(f"{t}|{f}|{m['score']}|{m['confidence']}|{m['tag']}".encode())
    return h.hexdigest()[:16]


def simulate(n, seed, factors, w):
    rng = np.random.default_rng(seed)
    draws = {}
    for t, ev in EVIDENCE.items():
        base = np.array([ev[f]["score"] for f in factors], dtype=float)
        sig = np.array([NOISE[ev[f]["confidence"]] for f in factors])
        samp = np.clip(base + rng.normal(0, sig, size=(n, len(factors))), 0, 10)
        draws[t] = (samp @ w) / w.sum()
    return draws


def summarize(draws, seed, n, side, committed, factors):
    mat = np.stack([draws[t] for t in sorted(draws)])  # targets x n
    order = sorted(draws)
    winners = mat.argmax(axis=0)
    rep = {"side": side, "seed": seed, "n": n,
           "evidence_fingerprint": evidence_fingerprint(factors),
           "noise_convention": {k: f"N(0,{v}) truncated [0,10]" for k, v in NOISE.items()},
           "disclaimer": ("Rank distributions under confidence-scaled noise. "
                          "NOT probabilities of mineralization. Noise scales are "
                          "documented conventions, not measured errors."),
           "committed": committed, "targets": {}}
    for i, t in enumerate(order):
        d = mat[i]
        rep["targets"][t] = {
            "mean": round(float(d.mean()), 2), "std": round(float(d.std()), 2),
            "p5": round(float(np.percentile(d, 5)), 2),
            "p50": round(float(np.percentile(d, 50)), 2),
            "p95": round(float(np.percentile(d, 95)), 2),
            "p_ranks_first": round(float((winners == i).mean()), 3)}
    rep["pairwise"] = {}
    for i, a in enumerate(order):
        for j, b in enumerate(order):
            if i < j:
                rep["pairwise"][f"P({a}>{b})"] = round(float((mat[i] > mat[j]).mean()), 3)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--side", default="prospectivity", choices=sorted(SIDES))
    a = ap.parse_args()
    weights, committed = SIDES[a.side]
    factors, w = side_weights(a.side)
    rep = summarize(simulate(a.n, a.seed, factors, w), a.seed, a.n,
                    a.side, committed, factors)
    text = json.dumps(rep, indent=1)
    if a.out:
        with open(a.out, "w") as f:
            f.write(text + "\n")
        print(f"wrote {a.out} (seed {a.seed}, fingerprint {rep['evidence_fingerprint']})")
    if a.json or not a.out:
        print(text if a.json else _pretty(rep))


def _pretty(rep):
    lines = [f"TIER 2 RANK DISTRIBUTIONS [{rep['side']}] (n={rep['n']}, seed={rep['seed']}, evidence {rep['evidence_fingerprint']})"]
    for t, s in rep["targets"].items():
        lines.append(f"  {t}: mean {s['mean']} ± {s['std']}  P5–P95 {s['p5']}–{s['p95']}  "
                     f"P(ranks first) {s['p_ranks_first']}  (committed {rep['committed'][t]})")
    for k, v in rep["pairwise"].items():
        lines.append(f"  {k} = {v}")
    lines.append("NOTE: " + rep["disclaimer"])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
