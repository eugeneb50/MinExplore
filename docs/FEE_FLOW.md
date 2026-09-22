# Paid deeper analysis — fee flow (no payments wired yet)

## SKUs (fixed fee, defined deliverables)

- **Tier-1 Evidence Pack** — full coordinate evidence pack (six systems),
  prospectivity/feasibility/uncertainty tables, VOI-ranked field plan, GPS
  field package. Built from **commercially-clean inputs only** (the builder
  rejects NC/research-use derivations).
- **Tier-2 Frontier Review** — everything in Tier-1 plus Monte Carlo rank
  distributions, frozen-prompt frontier review with calibration log, and
  analyst notes. Pilot numbers labeled uncalibrated.

Prices, refund terms, and fulfillment SLA are set before any payment link goes
live. Suggested starting point: fixed fee per coordinate, published on the
results page next to exactly what is (and is not) included.

## Flow

1. Free results page (`site/coordinate.html`) shows public-data results + maps.
2. "Deeper analysis — fixed fee" panel lists SKUs, includes the
   not-investment-advice consent checkbox (see `docs/TERMS.md`).
3. Buyer pays via **payment link** (Stripe Payment Links proposed — no card data
   touches our code). Webhook marks the job paid.
4. Job enters `jobs/jobs.jsonl` (`queued → paid → running → delivered`), the
   pipeline runs the paid builder, the package is delivered by email/download.
5. Refunds: full refund if the paid builder cannot produce a package
   (e.g. missing inputs); otherwise per published terms.

## Implementation status

- `api/server.py`: `POST /api/jobs` (create), `GET /api/jobs/{id}` (status),
  `POST /api/webhooks/payments` (stub — verifies nothing yet; wire provider
  signature check before accepting money).
- `src/export.py`: paid field-package builder (to be extended with the
  commercial-clean input gate — currently builds from canonical records; the
  NC-exclusion check lands with the first paid SKU).
- Manual fulfillment is acceptable for the first sales; automate after demand.

## Hard rules

- No paid deliverable contains EOX/Esri derivations. Ever. Audit each SKU.
- No "probability of mineralization" in any paid output without a calibration
  study. Relative evidence scores + VOI field plan are the product.
- Ley Minera gates (tender-only concessions, ANP/water prohibitions, prior
  consultation) ship in every package footer.
