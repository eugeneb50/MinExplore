# Frontier review protocol

## Reviewer backends (config flag, never a dependency)

- **Hosted frontier API** (default): `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`, model
  pinned (e.g. `claude-opus-4-6`, `gpt-5.2`), temperature 0. Pay-per-review; use
  `--dry-run` to inspect packets before spending.
- **Local kev** (fallback): System One-compatible `noul`/`choice`/`score` endpoint
  at `http://127.0.0.1:8009`. Pretrained zero-shot only — 3 targets can never
  fine-tune anything.

## Frozen prompt (versioned; bump version on any wording change)

`PROMPT_VERSION = "review_v1"`. Packet per target = committed rank + all seven
factor rows (score, confidence, tag, note verbatim from `src/scores.py`) + Tier 1
flip paths. The model is asked for, per factor: `agree | challenge` + one-sentence
reason + revised score *if challenge*; plus an overall rank distribution
(p10/p50/p90). It is instructed that it receives no imagery and must not supply
geology — only judge the stated reasoning.

## Recording (verbatim + parsed)

- Save the raw response text untouched: `predictive/frontier_<target>_<model>_<ts>.json`.
- Append one JSONL line per (target, reviewer) to `predictive/calibration_log.jsonl`
  with exactly these fields (see `examples/calibration-log-example.jsonl`):

```json
{"ts": "2026-09-21T00:00:00Z", "prompt_version": "review_v1",
 "reviewer": {"backend": "anthropic|openai|kev-local", "model": "claude-opus-4-6", "temperature": 0},
 "target": "T2", "tier0_rank": 6.3,
 "challenges": [{"factor": "structural_context", "tier0_score": 7, "proposed": 5, "reason": "..."}],
 "reviewer_p50": 6.0, "delta_vs_tier0": -0.3,
 "disposition": "confirm|challenge|dissent",
 "notes": "pilot, uncalibrated (n=0 field validations)"}
```

## Reading the log

- Recurring challenges to one factor across reviewers = candidate evidence revision
  (human decides; Tier 1 VOI absorbs it as a field test).
- Systematic reviewer-vs-Tier-0 drift = bump `PROMPT_VERSION`, never silently reweight.
- With n=0 outcomes, calibration statistics (Brier etc.) are *agreement* metrics
  between reviewer and Tier 0 — label them as such.
