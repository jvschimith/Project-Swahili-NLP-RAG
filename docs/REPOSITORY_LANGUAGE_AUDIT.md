# Repository Language Audit

## Language Policy

Engineering and international scientific communication use English. Portuguese is
reserved for explicit Brazilian scientific provenance. Swahili is the object language
and remains unchanged in linguistic examples, lexica, corpora, and tests.

## Areas Audited

The audit covered the primary README, active documentation, Python source, tests,
scripts, SQL and migration documentation, data/references READMEs, `.env.example`,
Makefile, project/test configuration, FastAPI metadata, CLI text, and Streamlit UI.
Generated files, environments, caches, downloaded corpora, and ignored artifacts were
excluded. Historical documents were classified separately.

## Portuguese Legacy Found

The active migration and raw-data guides used the Portuguese heading `Estrutura`; the
migration template also used `nova_tabela` / `nova_coluna`. These were engineering
examples rather than research data and were translated to English.

## Changes Made

- Normalized active migration/raw-data guides and the environment template to English.
- Replaced legacy product labels in API documentation, the dashboard, and test guidance.
- Replaced stale RAG product labels in `.env.example` and migration attribution.
- Added an explicit English/Portuguese/Swahili language policy.
- Added intentional Brazilian scientific provenance in English and Portuguese.

## Intentional Portuguese Preserved

Portuguese remains only in the README and `docs/PROJECT_PROVENANCE.md`, classified as
`BRAZILIAN_SCIENTIFIC_PROVENANCE`. These passages must not be removed by future
language cleanup.

## Swahili Data Preserved

All Swahili surface forms, sentences, dictionary content, morphological markers,
noun-class examples, fixtures, corpus material, and official source names are
classified as `SWAHILI_DATA` and were not translated.

## Remaining Non-English Content

- `BRAZILIAN_SCIENTIFIC_PROVENANCE`: the two intentional public provenance statements.
- `SWAHILI_DATA`: linguistic examples, fixtures, lexica, and source/corpus material.
- `PROPER_NAME`: personal and project/source names.
- `BIBLIOGRAPHIC_SOURCE`: cited publication titles and source terminology.
- `SOURCE_PROVENANCE`: official dataset names such as Masakhane and Kamusi.
- `HISTORICAL_CONTENT`: lower-priority archived material under `docs/history/`.

The active technical repository has zero identified accidental Portuguese engineering
prose after this audit.
