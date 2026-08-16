# Responsible Crawl Orchestration v1 Session Report

## Starting State and Git

Work began from clean commit `1dec3d6` on `chore/english-sqlite-provenance`, whose
recorded validation was 163 collected, 162 passed, one optional-network skip, zero
failed, and 69% branch-aware coverage. The dedicated local branch is
`feat/responsible-crawl-orchestration-v1`. The remote configuration was inspected but
not changed, and nothing was pushed.

## Implementation

The new Crawl Orchestration bounded context is implemented in `src/crawl/`:

- `domain.py`: the `CrawlJob` aggregate, `FrontierEntry` entity, `CrawlUrl` and
  `CrawlBudget` value objects, state/termination enums, robots and rate policies, and
  the aggregate repository contract.
- `application.py`: robots cache/parser, deterministic origin scheduler, acquisition,
  safety, retrieval and clock ports, typed status snapshots, and start/run/inspect/
  interrupt/resume/stop use cases.
- `infrastructure.py`: SQLAlchemy repository, safe URL and robots adapters, system
  clock, and the anti-corruption adapter around Web Corpus Acquisition v1.

No FastAPI route or CLI was added. The application service is the conservative internal
capability boundary for v1; a public interface can be designed after pilot limits are
measured. No crawl behavior was placed in routes or linguistic modules.

## Persistence

`crawl_jobs` stores aggregate configuration, state, counters, timestamps, and explicit
termination. `crawl_frontier` stores the job foreign key, canonical URL, origin,
parent URL, depth, state, reasons, attempts, and timestamps. The schema enforces
`UNIQUE(job_id, canonical_url)` and `crawl_frontier.job_id` uses `ON DELETE CASCADE`.
The existing SQLite connection hook continues to enforce foreign keys.

`SqlAlchemyCrawlRepository` maps between domain objects and ORM rows; ORM models never
cross the repository boundary. Completion/failure/skip checkpoints persist the current
entry and job counters in one database transaction. Dequeue is ordered by depth then
integer identity. Schema initialization follows the repository's existing
`Base.metadata.create_all` convention; no new database server or migration framework
was added.

Operational crawl state remains in SQLite. Corpus documents remain content-addressed
JSON plus the JSONL manifest. Those stores have deliberately separate transaction
boundaries.

## Crawl Semantics

- **Robots:** safely retrieved through the existing SSRF-aware fetcher and cached per
  origin; 404/410 allows as missing, while unreachable/malformed fails closed. Core
  user-agent, longest-match Allow/Disallow, wildcard/end-anchor, and crawl-delay
  semantics are supported.
- **Scope:** seed origins are allowed by default; additional origins require explicit
  configuration.
- **Scheduler:** the greater of the persisted job minimum and robots crawl delay is
  enforced independently per origin through an injectable monotonic clock.
- **Frontier:** conservative canonical URL identity and deterministic breadth-first
  ordering prevent cycles and duplicate enqueue. Parent discovery URLs are retained.
- **Budgets:** total page attempts, depth, failures, and attempts per origin are bounded.
  Page/failure exhaustion is an explicit terminal outcome; policy rejections are
  explicit skipped entries.
- **Checkpoint/resume:** configuration, counters, and every frontier state are durable.
  Resume is limited to interrupted jobs, recovers only orphaned `processing` entries to
  `queued`, and never resets completed entries.
- **Interruption window:** acquisition may succeed immediately before its relational
  checkpoint. A resumed retry remains safe because the acquisition corpus store is
  exactly deduplicated.

## Integration

`WebAcquisitionAdapter` performs the existing bounded safe fetch, then delegates HTML
to `AcquisitionPipeline`. Orchestration does not implement extraction, Swahili
validation, content hashing, corpus deduplication, provenance, or artifact layout.
Adapter coverage confirms a repeat delegates to and is deduplicated by the existing
corpus manifest.

## Tests

Sixteen crawl-focused tests were added across domain, application, infrastructure, and
adapter boundaries. They cover robots decisions/cache/safety, deterministic pacing,
URL canonicalization, state invariants, persistent identity/order, parent provenance,
scope, cycles, fragments, unsafe and disallowed pages, depth/page/failure/per-origin
budgets, acquisition failure, explicit termination, interruption recovery, resume, and
delegated corpus deduplication. Tests use fake adapters and temporary SQLite/corpus
directories; no live Internet or private data is required.

Final measured repository result: **179 collected, 178 passed, 1 optional-network
skip, 0 failed**. Global branch-aware coverage is **72%**. Crawl modules measured
approximately 78–90% file coverage, with the domain at 90%, application at 85%, and
infrastructure at 78%.

## Quality and Sanity Checks

- Ruff on all changed Python and crawl tests: clean.
- isort on all changed Python and crawl tests: clean.
- Black check with the installed Python 3.12 target: clean. The project metadata also
  requests Python 3.13, which Black 26 cannot safety-parse under the active 3.12 runtime;
  the explicit `py312` check avoids misreporting that tool/runtime limitation.
- Targeted mypy over all three crawl modules: clean.
- Full-project mypy: 76 pre-existing errors remain across 11 legacy export,
  morphology, repository, use-case and old-style ORM files; they are reported rather
  than changed in this feature sprint.
- FastAPI `/health` import/request sanity: passed (with the existing Starlette/httpx
  deprecation warning).
- In-memory SQLite initialization: passed; both crawl tables were created and
  `PRAGMA foreign_keys` returned `1`.
- Existing acquisition inspector/ingestion module smoke invocations: passed.
- `git diff --check`: clean.

The full suite still reports known `datetime.utcnow()` deprecations and the optional
FastAPI dependency warning. They are outside this crawl feature and were not hidden.

## Documentation and Architecture Audit

`docs/RESPONSIBLE_CRAWL_ORCHESTRATION.md` documents the problem, ubiquitous language,
bounded context, aggregate and persistence models, invariants, state diagrams, layers,
ports, policies, budgets, checkpoint semantics, scientific reproducibility, security,
agent compatibility, rejected alternatives, and evolution path. README now exposes
the implemented capability.

The final audit confirmed that the domain imports no SQLAlchemy, SQLite, FastAPI, or
acquisition implementation; acquisition is reused through a narrow port; operational
and scientific stores remain distinct; SQLite and foreign keys remain authoritative;
budgets and robots checks precede acquisition; completed entries remain terminal; and
the code introduces no PostgreSQL, browser automation, agent framework, distributed
queue, RAG terminology, linguistic changes, private data, or changes to Brazilian
scientific provenance.

## Limitations

V1 is synchronous and single-worker. It has no distributed claim/lease, automatic
retry schedule for failed entries or robots retrieval, persisted rate timestamp,
robots extensions beyond the documented core, feed/sitemap orchestration, semantic
link ranking, CLI/API interface, rendered DOM, JavaScript, browser inspection, or live-
web reproducibility guarantee.

## Recommended Next Milestone

Run a tightly bounded **Public Swahili Corpus Pilot** using conservative job limits and
record policy/extraction/failure metrics. The pilot should validate real publisher
robots behavior, link quality, and operational observability before any crawler scope or
browser capability is expanded.
