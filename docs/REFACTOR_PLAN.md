# Refactor Plan

## P0 — Correctness, reproducibility, and security

1. Establish a safe Git baseline and measured quality baseline.
2. Classify and resolve existing test failures against `LINGUISTIC_SPEC.md`.
3. Consolidate packaging metadata and remove unsupported claims/placeholders.
4. Harden arbitrary URL fetching against SSRF and add deterministic fixture tests.
5. Validate database lifecycle, API import/startup, and core morphology behavior.

## P1 — Portfolio-quality engineering

1. Add meaningful application, persistence, and API regression tests.
2. Document actual architecture, data provenance, limitations, and API surface.
3. Resolve root-level debugging clutter and competing current documentation.
4. Rebuild the README around implemented, experimental, and planned capability.

## P2 — Web acquisition foundation

1. Add static-first page inspection only after P0/P1 stability.
2. Extract canonical/language/semantic/JSON-LD metadata with local fixtures.
3. Provide an independently testable developer-facing inspection command.

## P3 — Research directions

- Evaluate morphology against annotated Swahili data and publish error analyses.
- Explore corpus deduplication, confidence calibration, and richer derivational modeling.

