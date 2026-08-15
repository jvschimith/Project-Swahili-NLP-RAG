# English, SQLite, and Provenance Session Report

## Starting State

The worktree was clean at `0e8e8c2`, with the completed acquisition branch as the
starting point. Remotes were inspected and not changed.

## Git Branch

Work was isolated on `chore/english-sqlite-provenance`.

## Baseline Validation

Baseline measurement on Python 3.12.3 collected 162 tests: 161 passed, one optional
network test skipped, and none failed. Global branch-aware coverage was 69% in 12.81s.

## Language Policy

English is the active engineering and international scientific language; Portuguese
records Brazilian provenance; Swahili remains the linguistic object and data language.

## Repository Language Findings

The active repository was already predominantly English. Accidental Portuguese was
limited to headings in migration/raw-data guides and SQL placeholder identifiers.
Historical material was retained as lower-priority archival content.

## Portuguese Legacy Removed

`Estrutura`, `nova_tabela`, and `nova_coluna` were normalized to English. Stale RAG
labels were removed from active environment, API, dashboard, test, and migration prose.

## Intentional Portuguese Provenance Preserved

The requested Portuguese statement is present in the README and a concise Portuguese
statement is present in `docs/PROJECT_PROVENANCE.md`.

## Swahili Content Preserved

No Swahili examples, fixtures, corpus sentences, markers, lexicon content, proper names,
or linguistic identifiers were translated.

## Brazilian Scientific Provenance

The repository now explicitly records its Brazilian academic, intellectual, and
technological origin in professional, non-partisan language while remaining open to
international collaboration.

## README Changes

The README gained database architecture and bilingual scientific-provenance sections.

## CITATION Metadata

`CITATION.cff` was absent. It was not created because the repository contains no
sufficiently verified, non-sensitive author identity; GitHub account naming alone was
not treated as authoritative personal metadata.

## API / CLI Changes

FastAPI, CLI, scripts, and Streamlit text audited as active English. No behavior or
public route semantics required normalization.

## SQLite Architecture

SQLite is documented as the official default and tested relational backend. The
project-relative default requires no external server. Foreign-key enforcement is now
enabled on every pooled SQLite connection.

## SQLAlchemy Boundary

Domain entities and repository contracts remain independent of SQLAlchemy and SQLite.
Concrete infrastructure repositories and connection/session management own persistence.

## SQLite-Specific Behavior

The connection layer localizes a 30-second timeout, cross-thread connection use, and
foreign-key PRAGMA configuration.

## Database Portability Risks

The manual baseline migration uses SQLite-specific schema/version inspection and
types/keywords. Legacy ORM mappings are untyped and datetimes are naive. No alternative
backend is claimed as tested.

## Raw SQL Findings

Runtime repositories use SQLAlchemy expressions. Raw SQL is confined mainly to the
SQLite baseline migration, documented migration commands, and the foreign-key PRAGMA.

## Database Tests

Temporary file-backed SQLite tests cover round trips, uniqueness, rollback, grouped
queries, repeated sessions, and foreign-key configuration.

## Corpus / Database Separation

Structured application records use SQLite/SQLAlchemy. Web corpus documents remain
content-addressed filesystem JSON plus JSONL manifest storage.

## Test Results

Final suite: **163 collected, 162 passed, 1 optional-network skip, 0 failed** in
12.87 seconds. The added test verifies SQLite foreign-key enforcement.

## Coverage

Global branch-aware coverage remained **69%**.

## Ruff Status

The new database connection code and persistence test pass Ruff. A repository check
also reports 52 pre-existing findings in legacy API, Streamlit, and diagnostic files
whose public-facing labels were normalized; none is on a changed line. They were not
silenced or expanded into unrelated refactoring.

## Mypy Status

Touched database connection code passes targeted mypy. Repository-wide existing debt is
reported without suppression: 76 errors in 11 files, unchanged from baseline.

## Git Commits

Persistence correctness: `4cf2593 fix: enforce SQLite foreign key constraints`.
Language, architecture, and provenance documentation follows in a second local commit.
Nothing is pushed.

## Remaining Intentional Non-English Content

Portuguese provenance, Swahili data, proper names, bibliographic/source provenance, and
historical archived material remain intentionally.

## Known Limitations

SQLite tests do not certify PostgreSQL or any other backend. Migration tooling remains
lightweight, persistence remains partly term-centric, and naive datetime debt remains.

## Recommended Next Task

Modernize the legacy SQLAlchemy mappings and timezone handling in a dedicated,
behavior-preserving persistence session; do not add another backend without a concrete
deployment requirement and integration-test plan.
