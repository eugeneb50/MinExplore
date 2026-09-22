# Terms of use — research demo and paid deeper analysis

## What this is

Baja Mineral Explorer is a desk-study research demo. Outputs are **relative
evidence scores** — explicit, field-testable hypotheses assembled from public
sources. They are **not** investment advice, drilling recommendations, or legal
opinions, and no output is a "probability of mineralization" unless a calibration
study against held-out outcomes exists (none does as of PIPELINE_VERSION 3.0.0).

## Research (free) use

- Content: CC BY-NC-SA 4.0 (see `LICENSE`). Imagery/data keep provider terms
  (`DATA_PROVENANCE.md`).
- Quotas are browser-local by design (static host, no backend for the demo page).

## Paid deeper analysis (`docs/FEE_FLOW.md`)

- Before paying, the buyer checks a box confirming they understand the above:
  scores are uncalibrated desk rankings, field validation is still required.
- Paid deliverables are built **only** from commercially-clean inputs
  (`commercial_use_allowed: true` in `sources/registry.json`). Nothing derived
  from EOX (NC) or Esri (research-use) sources ships in a paid package — the
  builder enforces this; see `src/export.py` + `docs/FEE_FLOW.md`.
- Mexican mining activity is governed by the Ley Minera (2023 reform):
  public-tender concessions, ANP and water-availability prohibitions, prior
  consultation. Water availability in this arid corridor is the principal
  regulatory risk and is scored separately as feasibility, never blended away.

## Third-party and AI use

- Mindat: reference/discovery only under a future written agreement (see
  `docs/MINDAT_REQUEST_TEMPLATE.md`). No scraping, no bulk extraction, no
  embeddings/RAG/training on Mindat material without prior written permission.
- Historical documents: metadata + page citations + minimal excerpts; rights
  verified per item (see `docs/IA_PIPELINE.md`).
