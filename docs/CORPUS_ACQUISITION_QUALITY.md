# Corpus Acquisition Observability & Quality Hardening v1

## Context and empirical baseline

Live Crawl Demonstration v1 found 305 canonical URLs while attempting nine pages at depth one: four acquisitions completed, five failed, three new artifacts were stored, one canonical duplicate reached acquisition, and 80 URLs were skipped. Arabic and Chinese language-selector routes, category pages, video routes, and weak static pages competed for the deliberately tiny budget. Acquisition failures exposed only a status string.

This increment optimizes that observed behavior. It does not move scientific corpus acceptance into crawling.

```text
crawl orchestration: is this URL worth attempting under policy and budget?
web acquisition: is fetched content acceptable for the corpus?
linguistic intelligence: analyze accepted linguistic content
```

An expected-language path is routing evidence, never proof of page language. Every fetched candidate still passes static extraction and the existing heuristic Swahili validator before storage.

## DDD ownership

- **Domain (`src/crawl/domain.py`)** owns `CandidateDecision`, `CandidateEvidence`, `CandidatePriority`, `ResourceKind`, and `LinkEligibilityPolicy`. They express stable frontier semantics and invariants independently of SQLAlchemy, FastAPI, and terminal output.
- **Application (`src/crawl/application.py`)** applies candidate decisions after canonical URL creation and preserves scope, depth, safety, per-origin, robots, rate, and budget policy. It exposes lifecycle metrics through `CrawlSnapshot` and carries structured acquisition outcomes through the anti-corruption port.
- **Acquisition (`src/acquisition/models.py`, `pipeline.py`)** owns `AcquisitionObservation`, stages, reasons, extraction evidence, language evidence, deduplication, and final corpus acceptance.
- **Infrastructure (`src/crawl/infrastructure.py`)** maps durable frontier values to SQLAlchemy and translates the Web Acquisition result into the crawl port without discarding evidence.
- **Interface/demonstration (`src/demo/live_crawl.py`)** renders typed decisions, bounded examples, outcomes, and summaries. Browser viewing remains presentation-only.

No linguistic model, morphology contract, corpus artifact format, or provenance field was changed.

## Candidate eligibility and priority

The policy is deterministic and site-neutral. It uses exact path segments/tokens, a small set of explicit language routes, extensions, date paths, and common editorial identifiers. It does not use probabilities.

Positive evidence:

- `expected_language_path`: exact `/sw/`, `/swahili/`, or `/kiswahili/` segment;
- `article_like_path`: article/story tokens, a dated route, or common `/a-<id>` / `/a/...<id>.html` editorial identity;
- `date_like_path`: year/month route.

Negative evidence:

- `competing_language_path`: a deliberately small set of clear selector routes (`ar`, `arabic`, `zh`, `chinese`, `en`, `english`);
- `category_like_path`: category, section, tag, author, archive, account, search, or share route;
- `video_like_path` and `audio_like_path`: video/player/embed/vidio/watch or audio/podcast/sauti tokens and explicit video query evidence;
- `unsupported_resource_kind`: obvious image, media, PDF, stylesheet, script, feed/XML, or archive suffix.

Clear competing-language paths and unsupported files are ineligible. Category, video, audio, and unknown HTML routes remain eligible at low or normal priority when uncertain. A target-language path alone is normal priority; it becomes high only with article/date/editorial-ID evidence. This avoids treating all `/sw/` navigation as articles.

The domain returns an explainable decision containing eligibility, integer priority, resource kind, evidence, and an optional machine-readable skip reason. Scores are internal ordering weights, not confidence or language probabilities.

## Frontier semantics and persistence

Previous ordering was:

```text
depth ASC, discovery id ASC
```

Current ordering is:

```text
depth ASC, priority DESC, discovery id ASC
```

Depth remains primary and the autoincrement identity remains the stable tie-breaker. Checkpoint/reload therefore reproduces ordering. Priority never bypasses origin scope, depth, URL safety/SSRF controls, per-origin limits, robots, rate scheduling, or budgets.

The `crawl_frontier` SQLAlchemy mapping adds:

- `priority` (non-null integer, default 50);
- `resource_kind` (non-null string, default `unknown`);
- `candidate_evidence_json` (non-null compact JSON text, default `[]`);
- terminal acquisition stage/reason, artifact identity/creation flag, and duplicate reason;
- composite next-entry index `(job_id, state, depth, priority, id)`.

The existing `(job_id, canonical_url)` uniqueness constraint and crawl-job foreign key remain. SQLite foreign-key enforcement remains enabled and tested. Operational state stays relational; scientific artifacts stay content-addressed JSON plus JSONL manifest. These additive columns apply to newly initialized frontier databases; no runtime crawl database is committed, and old disposable demo state should be recreated because this repository does not pretend that `create_all` is a migration system.

Canonical tracking removal and uniqueness still prevent duplicate frontier entries. Additionally, when a short URL redirects to a final URL already queued, that queued alias is marked `duplicate` before acquisition, preserving page budget.

## Acquisition outcome and rejection telemetry

`AcquisitionObservation` retains evidence already produced by `PageInspector`, `StaticArticleExtractor`, and `validate_language`:

- stage and reason;
- extraction strategy;
- HTML language;
- article/main container and JSON-LD article evidence;
- paragraph and extracted-character counts;
- dynamic-page signal;
- language status, heuristic evidence score, and evidence strings.

Implemented terminal reasons are:

- `accepted`;
- `insufficient_static_content`;
- `dynamic_browser_required`;
- `likely_non_swahili`;
- `uncertain_language`;
- `duplicate_canonical_url`;
- `duplicate_content`;
- adapter-level `network_failure`.

The fetch API does not currently distinguish every unsupported content-type failure from other safe-fetch failures, so no unsupported-content category was fabricated. Storage exceptions remain exceptional rather than being mislabeled.

A rejected fetched page may still supply links to crawl orchestration. This is intentional separation: rejection means its content did not become an artifact, not that its safe HTML links cease to exist. UN News demonstrated why this matters: its index had insufficient static corpus text but led to article candidates.

## Metrics

`CrawlSnapshot` exposes:

- **discovered**: durable frontier identities, including pre-acquisition skips;
- **eligible candidates**: identities not rejected by eligibility/scope/depth/safety classification;
- **skipped before acquisition**: all frontier skips, including eligibility and later crawl policy exclusions;
- **high/low priority candidates**: durable candidate priority counts;
- **attempted acquisitions**: fetch/acquisition calls charged to page budget;
- **completed**: accepted acquisition outcomes, including an acquisition-level duplicate when content was scientifically acceptable;
- **acquisition rejections**: failed post-attempt outcomes;
- **artifacts created**: newly stored corpus documents;
- **duplicates**: pre-acquisition redirect aliases plus acquisition canonical/content duplicates;
- **skip/failure reasons**: machine-readable reason counters.

Derived measures used in the pilot are:

```text
acceptance rate = completed / attempted
artifact yield per attempted page = artifacts created / attempted
artifact yield per discovered URL = artifacts created / discovered
article-like candidate ratio = high-priority candidates / discovered
```

These are operational acquisition measures, not claims of scientific corpus accuracy.

## Testing strategy

Deterministic tests cover target, neutral, competing-language, article/date/editorial-ID, category, video, audio, file, and unknown paths; relative normalization; tracking deduplication; priority/depth/stable ordering; reload/resume; redirect aliases; robots/scope/safety invariants; accepted, language, static, dynamic, network, and duplicate telemetry; metric separation; bounded demo output; and browser independence. Tests use generic fixtures and do not require Internet, Firefox, or WSLg.

## Live validation — 2026-08-17

The final run used fresh `/tmp` corpus/frontier state, `max_pages_per_site=3`, `max_depth=1`, two-second effective pacing, and no browser executable on `PATH`. Robots was fetched again for every origin and allowed the attempted routes. No live output was added to Git.

| Site | Origin | Robots | Discovered | Eligible | Skipped before acquisition | Attempted | Accepted | Rejected after acquisition | New artifacts | Duplicates | Termination |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| VOA Swahili | `https://www.voaswahili.com` | allowed | 184 | 84 | 102 | 3 | 3 | 0 | 3 | 2 redirect aliases | page budget |
| DW Kiswahili | `https://www.dw.com` | allowed | 105 | 61 | 44 | 3 | 3 | 0 | 3 | 0 | page budget |
| UN News Kiswahili | `https://news.un.org` | allowed | 138 | 78 | 60 | 3 | 1 | 2 | 1 | 0 | page budget |
| **Total** | — | — | **427** | **223** | **206** | **9** | **7** | **2** | **7** | **2 redirect aliases** | — |

Final derived measures: 77.8% acceptance rate, 77.8% artifact yield per attempt, 1.64% artifact yield per discovered identity, and 36.8% high-priority/discovered ratio (157/427). Higher discovery and skip counts are partly caused by preserving links from rejected pages and recording depth-one page outlinks; they are not alone evidence of improvement.

## Before/after interpretation

| Measure | Previous | Final |
|---|---:|---:|
| Discovered | 305 | 427 |
| Attempted | 9 | 9 |
| Completed | 4 | 7 |
| Rejected/failed attempts | 5 | 2 |
| New artifacts | 3 | 7 |
| Acquisition duplicate attempts | 1 | 0 |

Article-like pages reached acquisition earlier. DW used its two non-seed attempts on full semantic articles rather than video/audio sections. UN excluded Arabic, Chinese, and English selectors before acquisition and selected dated story routes even though its seed itself was rejected. VOA selected distinct `/a/...` report routes; redirect aliases were removed before reacquisition. No child category/index route consumed an attempt. Policy and safety remained ahead of acquisition.

The result supports improvement because the selected pages were inspected, not merely because totals rose. Rejection explanations identified UN's seed and one story as `static_extraction / insufficient_static_content` with containers, paragraph counts, and character counts.

## Manual artifact review

The seven-artifact sample is too small for accuracy claims. The two DW article artifacts and the UN story contain substantial Swahili report prose with sensible title/text pairs; semantic article or main-content extraction was appropriate and navigation did not dominate. The two VOA `/a/` artifacts are short Swahili media-report prose with an English media placeholder, but their titles match the text. The VOA and DW landing artifacts contain Swahili editorial material, yet also include media prompts or mixed landing-page content; they are weaker corpus artifacts than the full articles. This reveals a remaining acquisition-acceptance limitation rather than a crawler responsibility.

## Architecture decisions

### Deterministic heuristics instead of ML

- **Context:** nine-page budgets need transparent selection.
- **Decision:** small URL evidence rules and stable integer priorities.
- **Rationale:** explainable, reproducible, cheap, testable.
- **Consequences:** some unknown routes remain normal and site layouts can limit recall.
- **Alternatives:** LLM classification, embeddings, and agent selection were rejected as opaque and unnecessary.

### URL language evidence is not content validation

- **Context:** language selectors led to Arabic and Chinese routes.
- **Decision:** clear route markers affect eligibility/order only.
- **Rationale:** URL paths are not linguistic observations of fetched prose.
- **Consequences:** neutral paths remain possible; every candidate still passes acquisition validation.
- **Alternative:** crawler-owned language acceptance was rejected because it collapses bounded contexts.

### Priority modifies ordering, not policy

- **Context:** breadth-first link order selected weak routes.
- **Decision:** order by depth, priority, stable identity.
- **Rationale:** improve budget use without weakening responsible crawling.
- **Consequences:** a high candidate can still be denied or skipped by every existing policy.
- **Alternative:** priority bypassing robots or budgets was rejected as unsafe.

### Acquisition owns final corpus acceptance

- **Context:** an index can be a useful link source but unacceptable corpus text.
- **Decision:** rejected fetched pages may contribute links, while only Acquisition creates artifacts.
- **Rationale:** navigation value and scientific content value are distinct.
- **Consequences:** failed acquisition and crawler skip remain separate lifecycle outcomes.
- **Alternative:** requiring seed acceptance before discovery was rejected after the UN live evidence.

### Structured telemetry instead of generic failures

- **Context:** status strings hid where and why rejection occurred.
- **Decision:** typed stages/reasons and existing inspection/language fields cross the adapter boundary.
- **Rationale:** terminal output, tests, and metrics can explain decisions without re-inspection.
- **Consequences:** telemetry is compact and not an event warehouse.
- **Alternatives:** generic exceptions and permanent storage of every event in SQLite were rejected.

### Browser Inspector remains deferred

- **Context:** dynamic signals exist, but this run's two failures were insufficient static extraction and no measured dynamic-browser bottleneck appeared.
- **Decision:** preserve the signal but add no browser automation.
- **Rationale:** Playwright/Selenium/rendered DOM complexity is not justified by current evidence.
- **Consequences:** truly dynamic pages can still be rejected explicitly.
- **Alternatives:** browser-first crawling and site-specific browser scraping were rejected.

## Limitations and rejected infrastructure

- URL rules are conservative and lexical; they do not understand link-anchor semantics.
- VOA short media-report routes are article-like and accepted, although prose can be short.
- Landing pages can pass the existing acquisition validator and contain boilerplate; acceptance hardening remains an acquisition concern.
- A UN article with an article container and two paragraphs still failed minimum extraction rules; telemetry now makes that visible.
- Existing disposable frontier databases need recreation for the additive columns; a production migration framework remains future work.
- The current safe-fetch return contract cannot precisely categorize every content-type rejection.
- No site-specific scraper rules, LLMs, embeddings, agents, rendered browsers, message queues, Redis, Celery, PostgreSQL, distributed telemetry, or permanent event warehouse were introduced.

## Next milestone recommendation

Proceed to **Public Swahili Corpus Pilot v1** with bounded sources and manual sampling. The tiny live run selected materially more useful article routes, eliminated acquisition attempts for clear language selectors and redirect aliases, and explained the remaining failures. The pilot should measure the weaker landing/media artifacts and decide whether a narrowly scoped acquisition-acceptance refinement is warranted. Browser Inspector is not recommended: this run did not show dynamic-page loss as the important bottleneck.
