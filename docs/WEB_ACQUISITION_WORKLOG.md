# Web Acquisition Worklog

## Existing

Bounded HTTP(S) fetching already rejected credentials, unsafe schemes/addresses,
unsafe redirects, wrong content types and oversized HTML. `PageInspector`
provided static semantic, JSON-LD, OpenGraph, feed, sitemap and dynamic signals.

## Missing at baseline

No canonical document, extractor strategy layer, language gate, normalization,
hashing, deduplication, provenance store, manifest, discovery parsers or ingestion
CLI existed.

## Architectural decisions

- Network fetching remains in the application service; the deterministic corpus
  pipeline consumes HTML and never imports morphology.
- Structure precedes paragraph fallback.
- Language confidence is explicitly heuristic.
- Storage is content-addressed JSON plus JSONL, not a new database.
- Browser inspection is deferred because static P0/P1 is complete and useful.

## Tests

Offline fixtures cover semantic/JSON-LD articles, noise, misleading language
metadata, tracking URLs, duplicate URL/content, changed content, dynamic pages,
RSS, sitemap bounds and hostile XML declarations.

## Live-network limitations

Normal tests perform no network calls. The CLI uses the existing safe fetcher;
robots policy remains a documented caller/deployment responsibility in v1.

## Next task

Add a fetch result model exposing final URL/status/content type directly, then
implement bounded seed-page link discovery with an explicit robots policy.
