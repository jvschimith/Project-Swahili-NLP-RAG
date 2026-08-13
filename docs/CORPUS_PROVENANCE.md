# Corpus Provenance and Storage

Each accepted document is stored as `documents/<content-id>.json`; a compact
`manifest.jsonl` permits inspection without loading full text. IDs derive from
the normalized-content SHA-256 digest and cannot inject paths. Manifest entries
contain document ID, canonical URL, domain, title, publication/retrieval times,
language, hash, extraction method and relative storage path.

Raw extracted text and normalized text are distinct. Normalization preserves
case, punctuation and paragraph boundaries while applying Unicode NFC, removing
zero-width characters, collapsing horizontal whitespace and identical repeated
paragraphs. Web content remains untrusted data and is serialized only as JSON;
page scripts are never evaluated.

Exact URL/content deduplication is implemented. Near-duplicate detection and
same-URL historical versioning are planned. Feed and sitemap parsers preserve
their discovery source, enforce result limits/domain filters, bound XML size and
reject DTD/entity declarations; discovered URLs still require safe fetching and
full page inspection.
