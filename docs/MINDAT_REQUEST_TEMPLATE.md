# Mindat authorized-use request — TEMPLATE (do not send as-is)

> Status: **scaffold only.** No request has been sent; no Mindat content is
> ingested. Fill the bracketed fields, then send through Mindat's
> research-partnership channel. Mindat terms (effective 2026-08-21) prohibit
> systematic scraping, bulk extraction, database replication, and any use of
> Mindat material for embeddings, vector DBs, RAG, AI grounding, training or
> evaluation without prior written permission — even indirectly acquired.

## Terms to comply with (summary, not legal advice)

- Register for a Mindat account; apply for authorized API access.
- State whether Baja Mineral Explorer is noncommercial, public, monetized, or
  potentially commercial (note: the planned paid deeper-analysis tier likely
  counts as commercial — ask explicitly).
- Request **separate written permission** for embeddings / private retrieval
  index / ML use; ask about quotas, caching, derived features, redistribution.
- No photo ingestion (photographer rights). Link every record to the locality page.
- Noncommercial API access is available by application under CC BY-NC-SA 4.0;
  commercial licensing is separate.

## Draft body (fill brackets, keep the provenance commitments)

> Subject: Authorized API and analytical-use request — Baja Mineral Explorer
>
> I am developing Baja Mineral Explorer, a [noncommercial research demonstration
> / commercial service — DELETE ONE AND EXPLAIN] that combines public
> geological, remote-sensing and historical sources for the El Aguajito area,
> Baja California, Mexico.
>
> I would like to use authorized Mindat locality identifiers, coordinates where
> permitted, reported mineral associations and bibliographic references. I would
> store provenance (`mindat_locality_id`, `original_references`,
> `mindat_page_reference`, `last_retrieved_at`, `license`,
> `coordinate_precision`, `verification_status` per
> `schemas/mindat_reference.schema.json`) and link every displayed record back
> to Mindat. I would not copy photographs or substantial locality descriptions.
>
> Please advise (1) whether this use is considered noncommercial or requires a
> commercial license, (2) whether I may create embeddings or a private retrieval
> index for source discovery, and (3) guidance on API quotas, caching and
> publication of derived — not replicated — results.

## Record schema

See `schemas/mindat_reference.schema.json`. Follow cited references back to the
original SGM report, article, or map whenever possible.
