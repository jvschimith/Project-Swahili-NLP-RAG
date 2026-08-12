# Web Acquisition Roadmap

## Goal

Build a reproducible, public-content acquisition path for Swahili corpora without treating generic paragraph concatenation as robust article extraction.

## Planned Flow

URL → page inspection → extraction strategy → bounded fetch → extraction → normalization → language validation → deduplication → provenance → corpus storage → NLP

## Strategy Order

1. Static HTML and HTTP metadata.
2. Structured data: JSON-LD, OpenGraph, RSS/Atom, and semantic HTML.
3. Documented public data endpoints exposed by the page.
4. Browser-rendered DOM only when static evidence shows it is necessary.

## Safety and Reproducibility

- Permit only supported HTTP(S) schemes and reject loopback, private, link-local, and metadata destinations.
- Revalidate redirect destinations and resolved addresses.
- Use explicit timeouts, bounded retries/backoff, rate limits, size limits, and an identifiable user agent.
- Support allowed-domain policy for deployments.
- Store requested/final/canonical URLs, retrieval time, status, content type, extractor/version, and content hash.
- Respect access controls and site policies; do not bypass authentication, CAPTCHAs, paywalls, or private APIs.

## Page Inspection Evidence

An inspector should report HTTP metadata, canonical URL, HTML language, title, semantic containers, headings/paragraphs, JSON-LD types, OpenGraph values, feeds, sitemap hints, pagination, embedded state, script and public request hints, link count, static/dynamic indicators, and a heuristic extraction recommendation with an explanation.

## Deliberately Deferred

- Broad crawling and scheduling.
- Browser automation as a default.
- Site-specific circumvention logic.
- Claims that metadata language alone proves article language.
