# Web Acquisition Worklog

## New-machine baseline

- Date: 2026-08-15; WSL2 kernel 6.18.33.2, repository on native `/home` storage.
- 12 logical CPUs, 3.8 GiB RAM, 1.0 GiB swap, and 952 GiB filesystem space available.
- Python 3.12.3 from the project-local Linux `.venv`; pip 26.2.1; Git 2.43.0.
- Starting commit `373aa9c` on clean `main`; work continues on local branch
  `feat/web-corpus-acquisition-v1`. Remotes were inspected and not modified.
- Baseline: 155 collected, 154 passed, 1 optional-network skip, 0 failed, 68%
  global branch-aware coverage in 12.95 seconds. `pip check` passed.
- Black's repository-wide safety check cannot parse Python 3.13-only syntax while
  running on Python 3.12, and focused retry processes stalled until interrupted.
  Ruff, isort, tests and manual diff review cover touched files; this is recorded as
  an interpreter/tooling difference rather than hidden as a passing Black result.

## Existing components

- SSRF-aware bounded `URLNewsAnalyzer` fetcher with redirect revalidation.
- Static `PageInspector` with canonical, language, title, OpenGraph, JSON-LD,
  semantic container, feed/sitemap, and dynamic-content evidence.
- Structure-first extraction, normalization, heuristic Swahili validation,
  SHA-256 identity, `WebDocument`, provenance, content-addressed JSON storage,
  JSONL manifest, exact deduplication, RSS/Atom and sitemap parsing, and one-page CLI.

## Missing components

- Calibrated language identification and near-duplicate detection.
- Historical version storage for changed content at one canonical URL.
- Robots-policy/rate scheduler and recursive crawl orchestration.
- Optional browser inspection and public structured-endpoint inspection.

## Decisions

- Preserve `fetch_url()` compatibility while adding a metadata-rich `FetchResult`.
- Require explicit domains and a positive maximum for seed-page link discovery;
  discovery parses one page and never recursively fetches.
- Treat page-declared canonicals as untrusted identity hints: accept absolute,
  credential-free HTTP(S) URLs and otherwise fall back to the final fetched URL.
- Scan manifests incrementally during deduplication instead of loading them into RAM.
- Keep browser tooling deferred; static P0/P1 remains sufficient and dependency-light.

## Tests

- New focused cases cover redirect metadata, timezone-aware retrieval, bounded and
  domain-scoped seed links, tracking/canonical deduplication, invalid canonical
  schemes/credentials/ports, and unsafe declared-canonical fallback.
- Focused result after implementation: 31 passed, 0 failed.

## Security findings

- Redirect targets continue to receive DNS/public-address validation.
- Canonical links are never fetched automatically and can no longer inject unsafe URL
  schemes or credentials into corpus identity.
- Content-derived document identifiers remain path-safe; remote filenames are unused.
- Application-level checks do not eliminate DNS rebinding; deployment egress controls
  remain required for public operation.

## Current task

P0/P1 final validation, offline demonstration, adversarial review and the implementation
commit are complete. Finalize the documentation commit and terminal summary.

## Next task

Add an explicit robots policy and conservative rate scheduler before any multi-page
network crawl orchestration. Browser inspection remains P2.
