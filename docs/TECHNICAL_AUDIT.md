# Technical Audit

Status: active audit, updated 2026-08-12.

## Scope

This audit treats reproducible runtime behavior and automated tests as stronger evidence than historical documentation. It covers linguistic correctness, architecture, packaging, persistence, APIs, URL acquisition, security, and research-data provenance.

## Initial Findings

- No Git repository existed at session start.
- The active interpreter is Python 3.13; no `python` executable is available.
- Historical documentation contains claims that have not yet been substantiated.
- The project has a lexeme-first domain contract but also retains term-centric compatibility models and repositories.

## Measured Baseline

- Interpreter: CPython 3.13.5. The system initially had no `pip`, `pytest`, or quality tools.
- Test discovery: 106 tests before changes.
- Focused baseline result: 77 passed and 10 failed across application/domain tests. Failures covered `cha`, noun-prefix extraction for `mtu`, conjugated-verb misclassification, polarity propagation, `wasoma` root/stem terminology, empty input, and a property/method mismatch.
- Initial total branch-aware coverage: 35% (2,461 statements, 1,448 missed; 510 branches, 12 partial branches).
- API `TestClient` deadlocked in this restricted runtime; direct in-process HTTPX ASGI transport succeeded. Deterministic tests now use that transport without sockets.
- Pydantic emitted class-based `Config`, field-name shadowing, collection-bound, and naive-UTC deprecation warnings.

## Failure Classification

- CODE BUG: `cha` missing from the function-word list used by keyword filtering.
- CODE BUG: nominal prefix data omitted `m` and incorrectly included lexical strings `mtu`/`mti`.
- CODE BUG: noun-class prefix evidence took precedence over strong verbal marker chains, classifying `ninasoma` as a class 9/10 noun.
- SPEC/IMPLEMENTATION ISSUE: affirmative surface verbs did not consistently expose the frozen contract's polarity.
- TEST BUG: `wasoma` expected `soma` in the radical field while the frozen contract separates `som` and final `a`.
- LEGACY API INCONSISTENCY: `SentimentScore.is_confident` was decorated as a property despite accepting a threshold and being called as a method.
- TEST/API CONTRACT BUG: empty input cannot construct the non-empty `MorphologicalRoot`; the service now rejects it explicitly.

## Architecture Findings

- Domain modules do not import application, infrastructure, or web modules.
- Application services depend on domain objects, while ingestion use cases also consume repository contracts.
- Infrastructure implements legacy term/dictionary/news repositories with SQLAlchemy.
- `src/web/api.py` is oversized and holds transport schemas, dependency wiring, application orchestration, placeholder trend data, and in-memory batch state. Router extraction is P1/P2 work, not required for correctness.
- Persistence remains term-first even though the domain contract is lexeme-first; this is a documented migration boundary rather than being hidden.
- No query → retrieval → evidence-conditioned generation pipeline exists. The implementation is not currently RAG.

## URL and Security Findings

The baseline URL analyzer used unrestricted `requests.get`, followed redirects automatically, accepted arbitrary content types, had no response-size limit, and concatenated all paragraphs. This was an SSRF and acquisition-quality risk.

The hardened baseline now permits HTTP(S) only, rejects URL credentials and local hostnames, resolves and rejects non-global IP addresses, revalidates redirect destinations, bounds redirects and response size, enforces HTML content types, and uses an identifiable user agent. Remaining limitation: application validation cannot fully prevent DNS rebinding between validation and connection; public deployment needs network egress controls or connection-level address pinning.

## Packaging Findings

- `setup.py`, `pyproject.toml`, and a fully pinned monolithic `requirements.txt` duplicated and contradicted metadata.
- Placeholder author/email/repository values existed in `setup.py`.
- Torch, Transformers, Datasets, Jupyter, dashboard, and scraping dependencies were all installed by default.
- `pyproject.toml` is now authoritative, with `web`, `dashboard`, `research`, and `dev` groups. `requirements.txt` is a small compatibility entry point.

## Data Findings

- Only small seed JSON files, migration SQL, and raw-data instructions were present; no unique bulk corpus was found.
- Databases, downloaded raw corpora, processed outputs, embeddings, logs, reports, backups, coverage, bytecode, and local environments are ignored.
