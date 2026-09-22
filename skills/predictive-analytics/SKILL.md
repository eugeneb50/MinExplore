---
name: predictive-analytics
description: Tiered predictive analytics for MinExplore mineral targets — Tier 1 what-if sensitivity over the deterministic factor model, Tier 2 Monte Carlo rank distributions, and frontier-model review protocol. Use when asked to forecast, stress-test, or review target ranks, quantify uncertainty, rank field tests by value-of-information, or run/extend the predictive pipeline. Never rewrites committed ranks.
---

# Predictive Analytics

Turn the deterministic desk-screening model into **explicit, testable forecasts** — without ever overwriting it.

## Doctrine (non-negotiable)

1. **Tier 0 is read-only.** `src/scores.py` v3 split (prospectivity T1 5.3 / T2 7.2 / T3 5.7; feasibility T1 6.0 / T2 4.3 / T3 5.7) is the sole authority for published ranks. This skill only *reads* weights, `EVIDENCE`, and the split functions. A "prediction" that edits Tier 0 is a bug, not a forecast.
2. **No mineralization probabilities.** Zero field validations exist (no survey, geochemistry, spectroscopy, drilling). Tier 2 may emit *rank distributions* and explicitly labeled *pilot* probabilities with a calibration log — never "P(deposit)".
3. **Evidence tags drive uncertainty.** `observed`/`derived`/`inferred`/`not-yet-assessed`/`requires-field-validation` (see `src/scores.py`) set the noise scale. Low-confidence factors move; observed SGM facts barely do.
4. **Every forecast ships with its own falsification.** Report what field observation would overturn it (Tier 1 VOI list). A prediction without a kill-criterion is commentary.
5. **Frontier models judge, they don't retrieve.** Review prompts carry all evidence inline; the model challenges factor scores, it never supplies geology.

## Workflows

| Ask | Run | Output |
|---|---|---|
| "What flips the ranking?" | `scripts/sensitivity.py --target T2` | Tornado table: rank response to ±2 per factor; weight-robustness; flip thresholds |
| "What should we test first in the field?" | `scripts/sensitivity.py --voi` | Factors ranked by max rank movement across their plausible range |
| "How uncertain is T2's lead?" | `scripts/rank_distributions.py --n 10000 --seed 7` | Mean/std/P5–P95 per target, P(each ranks first), pairwise P(A>B) |
| "Get a second opinion" | `references/frontier-review.md` protocol | Frozen prompt + verbatim response + calibration-log entry |

## Tier map

- **Tier 0 deterministic** → `src/scores.py` v3 split (don't touch). Frontier-priority formula lives in `src/frontier.py`: priority = prospectivity × info-gain × feasibility − penalties (relative evidence score, never a probability).
- **Tier 1 prospective** → `scripts/sensitivity.py` in this skill (stdlib only). Safe for CI and site display ("what would change the rank").
- **Tier 2 predictive** → `scripts/rank_distributions.py` in this skill (numpy). Local-only; outputs stay in-repo under gitignored `predictive/` until a calibration story exists.
- **Review** → `references/frontier-review.md` (hosted frontier APIs or local kev; reviewer backend is a config flag, never a dependency).

## Guardrails

- Seeds are mandatory (`--seed`; default 7). Same seed + same evidence = byte-identical output. Record seed with every result.
- Noise scales: `Low → N(0,2)`, `Medium → N(0,1)`, truncated to [0,10]. These are documented conventions, not measured errors — say so in every report.
- Pilot probabilities get a `calibration_log.jsonl` entry per `references/frontier-review.md` schema, including prompt hash, temperature, and Tier 0 delta.
- Never present P(first) as P(mineralized). The correct sentence is: *"Under confidence-scaled noise, T2 ranks first in X% of simulations."*
- B/R heuristic stays an *unvalidated RGB visual-screening heuristic*. No forecast upgrades it to a mineral ID.

## Repo file map (truth hierarchy)

`src/scores.py` + `scripts/build_data.py` + `schemas/` outrank everything, including this skill. Site copy (`site/index.html`) is a mirror. `maps/` + `*.md` reports are generated artifacts. ±10–20 m horizontal caveat on coordinates. Never scrape `tile.google.com`/`bing.com`.
