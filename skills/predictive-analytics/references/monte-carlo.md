# Monte Carlo recipe (Tier 2)

## Why this shape

Factor scores are point judgments with stated confidences. The cheapest honest
uncertainty model: perturb each score with zero-mean noise scaled by its
confidence, recompute the deterministic rank, repeat. No fitting, no hidden
parameters beyond the two documented scales.

## Procedure (`scripts/rank_distributions.py`)

1. Fix `--seed` (default 7) and `--n` (default 10000). Record both.
2. Per draw, per factor: `score + N(0, σ)`, σ = 2.0 (Low) / 1.0 (Medium) / 0.5
   (High), clip to [0,10]. Recompute weighted mean with Tier 0 weights.
3. Summarize: mean/std/P5/P50/P95, P(ranks first), all pairwise P(A>B).
4. Emit the SHA-256 `evidence_fingerprint` of scores+confidences+tags. If the
   fingerprint in a saved report doesn't match current `src/scores.py`, the
   report is stale — rerun, don't quote it.
5. Sanity gate: means must reproduce committed ranks within ~0.05 (zero-mean
   noise). Current: 5.39/6.31/5.50 vs 5.4/6.3/5.5. ✓

## Reading results

- Overlapping P5–P95 bands (current: T1 4.42–6.35 vs T3 4.55–6.46) mean the
  T1/T3 ordering is noise — say that plainly; don't rank them.
- P(T2>T3) = 0.839 is *rank robustness under stated confidence*, not a
  discovery claim. Pair every number with the kill-criterion from Tier 1 VOI
  (e.g. "resolving the T2 lineament as a road collapses the structural factor").
- Changing noise scales is a sensitivity experiment, not a calibration: report
  both scales side by side, never silently swap.
