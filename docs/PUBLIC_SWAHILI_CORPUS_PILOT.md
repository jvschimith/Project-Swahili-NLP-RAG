# Public Swahili Corpus Pilot v1

## Objective and research question

This bounded experiment asks whether the deterministic crawl and acquisition architecture can produce a small, diverse, inspectable, provenance-preserving public Swahili corpus with useful operational yield and understandable failures across publishers. It is not a representative corpus, production crawl, language-accuracy evaluation, or linguistic gold standard.

The empirical starting point was the quality-hardening run: 427 discovered, 223 eligible, 206 skipped before acquisition, 9 attempted, 7 accepted/artifacts, 2 rejected, and 2 redirect aliases (77.8% yield).

## Source selection and preflight

Preflight was repeated on 2026-08-17. It checked public URL safety, current robots policy, seed retrieval, static inspection, language route, link availability, and obvious dynamic dependence. No disallowed route was bypassed.

| Source | Category | Seed | Preflight and rationale |
|---|---|---|---|
| VOA Swahili | international news | `https://www.voaswahili.com/` | Robots allowed; 170 static links; established public Swahili reporting. |
| DW Kiswahili | international news | `https://www.dw.com/sw/` | Robots allowed; 144 static links; long-form semantic articles. |
| UN News Kiswahili | institutional/public information | `https://news.un.org/sw/` | Robots allowed; 190 links; humanitarian/development vocabulary; seed itself had weak static evidence. |
| Global Voices Kiswahili | public cultural media | `https://sw.globalvoices.org/` | Robots allowed; 446 static links; distinct civic/translation publisher model. |
| Vatican News Kiswahili | public cultural institution | `https://www.vaticannews.va/sw.html` | Robots allowed; 211 static links; institutional/cultural diversity. |
| BBC News Swahili | international news | `https://www.bbc.com/swahili` | Robots allowed; 85 static links; independent extraction comparison. |
| HabariLEO | national news | `https://habarileo.co.tz/` | Robots allowed; 125 static links; Tanzanian regional publisher diversity. HTML declared `en-US`, so acquisition remained authoritative for content language. |

Swahili Wikipedia was considered for public-knowledge diversity but returned a conservative malformed/deny robots result and was excluded. This demonstrates policy preservation rather than a workaround.

## Experiment configuration

- Pilot ID: `92ed98c0-e0a6-4919-ae91-7f74d5241bd5`
- Seven sources; ten attempts per source; seventy maximum attempts
- Maximum depth 1; minimum same-origin delay 2 seconds
- Expected language `sw`
- Candidate policy `candidate-quality-v1`; acquisition `web-acquisition-v1`
- Started and completed on 2026-08-17/18 UTC
- Every source terminated with `page_budget_exhausted`
- Git branch, commit, initial dirty state, Python version, configuration, job IDs, artifact IDs, metrics, and review sample are recorded in the generated pilot JSON manifest. Generated databases, manifests, and corpus documents remain outside Git.

## Architecture and ownership

The crawl domain remains independent of FastAPI, SQLAlchemy, and Streamlit. `CrawlJob`, eligibility, priority, robots, safety, rate, and budgets remain authoritative. Acquisition remains authoritative for extraction, normalized-text language validation, deduplication, provenance, and corpus acceptance.

`CorpusPilotRun`, `PilotConfiguration`, and `PilotSource` are research/application experiment models rather than linguistic-domain or crawl aggregates. They associate multiple existing crawl jobs and snapshot reproducibility metadata. `ArtifactReview` is research evaluation, stored separately from immutable scientific artifacts. SQLAlchemy adapters persist operational/evaluation records. `CorpusResearchQueryService` joins bounded operational state with the JSONL corpus manifest for both reports and UI. Streamlit is only an interface consumer.

Storage remains deliberately split:

```text
operational crawl + experiment + evaluation -> SQLite
accepted scientific corpus                 -> JSON documents + JSONL manifest
temporary presentation                     -> Streamlit
```

SQLite additions are `corpus_pilots`, `corpus_pilot_sources`, and `corpus_artifact_reviews`. Pilot sources have a unique `(pilot_id, origin)` constraint and ordered index. Reviews have a unique `(pilot_id, artifact_id)` constraint, allowing an explicit update. Both child tables have foreign keys to the pilot; the source optionally references its crawl job. Frontier adds final URL and structured acquisition-details JSON for durable inspection. Foreign-key enforcement remains enabled per connection.

## Aggregate results

| Metric | Result |
|---|---:|
| Sources | 7 |
| URLs discovered | 1,937 |
| Eligible candidates | 630 |
| Pre-acquisition skips | 1,309 |
| Attempts | 70 |
| Accepted / artifacts | 52 |
| Rejected after acquisition | 18 |
| Duplicate/redirect aliases | 2 |
| Acceptance and artifact yield / attempt | 74.3% |
| Artifacts / discovered URL | 2.68% |
| Normalized characters | 204,627 |
| Mean / median artifact length | 3,935 / 2,772 characters |
| Minimum / maximum artifact length | 254 / 14,403 characters |

These are operational and pilot review measures, not linguistic accuracy. `discovered` counts durable canonical frontier entries. `eligible` counts entries not rejected by candidate eligibility. A pre-acquisition skip never reaches acquisition. `attempted` means acquisition budget was spent. `accepted` is acquisition completion; `artifacts` is new immutable storage. `rejected` is an attempted acquisition with a structured failure. Duplicates include canonical/redirect duplicate outcomes.

## Source comparison

| Source | Attempts | Artifacts | Yield | Avg chars | Main rejection | Manual sample |
|---|---:|---:|---:|---:|---|---|
| VOA | 10 | 6 | 60% | 1,869 | uncertain language | 2 good; 3 media-heavy |
| DW | 10 | 10 | 100% | 2,367 | none | 1 good; 1 acceptable; 1 media-heavy |
| UN News | 10 | 7 | 70% | 1,925 | insufficient static content | 1 good; 3 too short |
| Global Voices | 10 | 10 | 100% | 6,138 | none | 3 boilerplate-heavy |
| Vatican News | 10 | 0 | 0% | 0 | uncertain language | no accepted sample |
| BBC | 10 | 10 | 100% | 7,518 | none | 3 good |
| HabariLEO | 10 | 9 | 90% | 2,189 | insufficient static content | 2 good; 1 wrong type |

Vatican failures were six `uncertain_language`, one `likely_non_swahili`, and three `insufficient_static_content`. VOA had two uncertain-language and two insufficient-static failures. UN had three and HabariLEO one insufficient-static failure. No dynamic-browser-required rejection was recorded. Pre-acquisition skips included scope, depth, three UN competing-language routes, two Vatican competing-language routes, one unsupported Vatican resource, and two VOA duplicate aliases. Robots excluded no selected frontier entry after all seven origins passed preflight.

## Deterministic manual review

Sampling sorts artifacts by source and document ID, takes three per contributing source, then adds up to five globally shortest artifacts not already selected. This produced 21 artifacts. Review examined observable language, content type, extraction cleanliness, title/URL sense, and obvious boilerplate; it did not annotate linguistic structure.

| Label | Count | Pilot sample proportion |
|---|---:|---:|
| good_article | 9 | 42.9% |
| acceptable | 1 | 4.8% |
| boilerplate_heavy | 3 | 14.3% |
| too_short | 3 | 14.3% |
| media_placeholder_heavy | 4 | 19.0% |
| wrong_content_type | 1 | 4.8% |
| mixed_language / needs_review | 0 | 0% |

Good or acceptable was 47.6% of this deliberately weakness-enriched sample, not an estimate of population accuracy. Strong examples included BBC artifact `072804db455999ed6422`, Global Voices contained substantial prose but all three samples began with repeated English publisher notices, and VOA artifact `b17cae930a69469bc3d2` was a short missing-media profile. UN artifact `6c9bfe06404230237ded` contained only 253 characters plus share controls. HabariLEO artifact `11e5e8ac0dcc44bd4670` was an accepted publisher “about” page. No large copyrighted passage is reproduced here.

Reviews record artifact ID, pilot ID, controlled label, bounded note, and timestamp in SQLite. They never mutate or re-hash corpus JSON.

## Provenance and reproducibility

Artifact inspection exposes document ID, requested/final/canonical URL, source domain, retrieval timestamp, HTTP metadata when present, extraction and language evidence, acquisition version, content SHA-256, relative corpus path, crawl job, and parent URL. The pilot manifest duplicates no corpus text. It records configuration, environment-safe Git/Python metadata, source and job associations, artifact IDs, metrics, deterministic sample IDs, and review summary.

## Architecture decisions

### Streamlit is temporary research infrastructure

**Context:** researchers need live inspection before a production frontend exists. **Decision:** local Streamlit consumes application queries. **Rationale:** rapid, bounded observability without defining product architecture. **Consequences:** manual polling and local-only assumptions. **Migration:** Next.js may later consume stable API/query contracts; Streamlit can be removed.

### UI observes application state

**Decision:** the headless CLI owns execution and checkpoints; UI never owns crawler logic. This preserves reproducibility and allows closed-console operation. Direct ORM use throughout UI and UI-triggered arbitrary URLs were rejected.

### Pilot is separate from CrawlJob

One experiment associates multiple independently bounded crawl jobs and adds configuration/version traceability without weakening job invariants or forcing research vocabulary into the crawl domain.

### Manual evaluation is separate from immutable artifacts

Human judgments are mutable evaluations, whereas content-addressed artifacts are immutable scientific records. Editing artifact JSON would corrupt identity/provenance and was rejected.

### SQLite state remains separate from corpus JSON

Relational operational/evaluation state needs constraints and queries; scientific documents need content-addressed JSON/JSONL portability. SQLite is sufficient. PostgreSQL and a telemetry warehouse are unjustified.

### Browser Inspector remains deferred

No dynamic-browser-required rejection occurred. Browser-first extraction, Playwright, Selenium, rendered DOM/network capture, and browser dependence add complexity without measured benefit. Existing optional Firefox visualization remains page-level only.

## Rejected alternatives

Building Next.js now would conflate research instrumentation with public product work. Power BI is premature for a single bounded experiment. LLM scoring and agent review would be opaque and non-reproducible. Site-specific rules could raise short-term yield but overfit publishers. Distributed crawling, message queues, Redis, Celery, Kafka, and PostgreSQL do not solve a measured bottleneck. RAG, embeddings, vector stores, and browser automation are outside this acquisition experiment.

## Limitations and recommendation

The pilot is only seventy attempts and publisher contribution is not representative. Depth one and article priority influence which content appears. Validator scores are heuristics, not probabilities. Current artifacts sometimes omit extraction-strategy metadata. The deterministic sample intentionally overrepresents short artifacts. Acceptance currently permits publisher pages, short briefs, media placeholders, and repeated boilerplate. Transient allow decisions are not fully persisted, although denials are machine-readable and policy ordering is tested.

The next milestone should be **Corpus Acceptance Quality v1**: use the observed about-page, short-brief, media-placeholder, and repeated-boilerplate cases to improve generic inspection/extraction acceptance without moving final language/content acceptance into the crawler. Browser Inspector is not recommended because dynamic loss was not material. Expansion should wait until the 47.6% good/acceptable weakness-enriched sample improves under deterministic review.
