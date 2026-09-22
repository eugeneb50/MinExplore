# Tier doctrine: deterministic → prospective → predictive

## Tier 0 — Deterministic (read-only)

`src/scores.py` v3: prospectivity (T1 5.3 / T2 7.2 / T3 5.7) vs feasibility
(T1 6.0 / T2 4.3 / T3 5.7), shown side by side, never blended. v2 blended mean
(5.4/6.3/5.5) frozen for history.
Same evidence in, same rank out. CI-enforced via `tests/test_scores.py`.
**You do not edit it, reweight it, or "improve" it.** If evidence changes, a human
commits a new `EVIDENCE` entry and the tests ratify the new ranks.

## Tier 1 — Prospective (what-if; stdlib; CI-safe)

Question: *"What would have to be true for the ranking to change, and what field
test answers that cheapest?"* Tools: `scripts/sensitivity.py`.

- **Tornado**: each factor ±2 (clamped [0,10]). Rank moves are small by design —
  weights damp single-factor swings. A factor with swing ≥1.0 is decision-relevant.
- **Weight robustness**: each weight ±5, renormalized. If the leader survives all
  single-weight shifts (current state: it does), say so — that *is* the finding.
- **Flip paths**: cheapest symmetric move for the runner-up to tie. Report the
  top-3 paths with magnitudes; these are the model's stated falsifiers.
- **VOI ranking**: Low-confidence factors swept across [0,10], ranked by swing.
  Each row carries its `field_test` note verbatim from `EVIDENCE` — that note is
  the recommended next observation.

Tier 1 output may be displayed publicly ("what would change the rank") because it
is a deterministic transform of published evidence.

## Tier 2 — Predictive (rank distributions; numpy; local-only)

Question: *"Given stated confidence per factor, how often does each target lead?"*
Tool: `scripts/rank_distributions.py --n 10000 --seed 7`.

- Noise: Low → N(0,2), Medium → N(0,1), truncated [0,10]. Convention, not measurement.
- Report: mean/std/P5–P95, P(ranks first), pairwise P(A>B), evidence fingerprint,
  seed. Sanity check: means must ≈ committed ranks (zero-mean noise); if not, the
  script is broken, not the model.
- Correct sentence: *"Under confidence-scaled noise, T2 ranks first in 76% of
  simulations."* Wrong sentence: anything containing "probability of mineralization".
- Outputs go to gitignored `predictive/` until a calibration story exists. Never
  into `maps/`, `site/`, or committed data.

## Review tier (second opinion, never a vote)

Frontier models and kev judge the *reasoning*, not the rocks. See
`frontier-review.md`. Review output can (a) confirm, (b) challenge a factor score
(routed back as a Tier 1 field-test candidate), or (c) dissent (logged). It cannot
(d) change a committed rank — that requires a human evidence commit.
