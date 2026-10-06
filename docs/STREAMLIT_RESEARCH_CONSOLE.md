# Streamlit Corpus Research Console

## Purpose and status

The Swahili Linguistic Intelligence Corpus Research Console is a temporary local research and engineering interface over persisted pilot state. **Streamlit is a research and engineering observability interface and is not the intended production frontend of Swahili Linguistic Intelligence.** The future public product remains Next.js and TypeScript.

Streamlit owns no crawl, acquisition, language-validation, or corpus-acceptance rule. The headless CLI works when the console is closed. The console reads narrow application query services over SQLite checkpoints and JSON/JSONL corpus storage:

```text
Crawl domain -> application orchestration -> SQLite / corpus JSON
                                              ^
                                              |
                                    research query service
                                              ^
                                              |
                                     Streamlit interface
```

Firefox page visualization remains optional and independent: Firefox answers which public page is visible; Streamlit answers what the deterministic system recorded. Neither browser performs scientific extraction.

## Running locally

Terminal A:

```bash
python -m src.research.run_corpus_pilot
```

Terminal B:

```bash
CORPUS_PILOT_DB=data/corpus-pilot/pilot.sqlite \
CORPUS_PILOT_ROOT=data/corpus-pilot/corpus \
streamlit run src/research_ui/corpus_pilot.py \
  --server.address 127.0.0.1
```

The UI is local-only by assumption. It displays no credentials or environment values. The CLI, not the UI, starts the bounded crawl. Refresh is manual, so there is no busy loop and reads cannot advance crawl state.

## Views

- **Overview & Current Activity**: status, operational metrics, rates, current persisted entry, lifecycle projection, and corpus growth.
- **Frontier & Candidate Inspector**: bounded/filterable frontier and deterministic eligibility evidence.
- **Acquisition Inspector**: persisted stage, reason, title, final URL, extraction, language, duplicate, and artifact data when available.
- **Corpus & Provenance Explorer**: read-only bounded text, hashes, requested/final/canonical URLs, retrieval and crawl linkage.
- **Source Comparison**: yield, rejection, text-length, and contribution differences by publisher.
- **Rejection Analysis**: pre-acquisition skips separated from post-acquisition rejection reasons.
- **Quality Review**: deterministic sample and separately persisted label/note workflow.
- **Experiment Metadata**: configuration, Git snapshot, Python version, paths, timestamps, and state.

The pipeline diagram is a projection of persisted facts. It does not execute pipeline behavior. Per-request robots and safety decisions are shown as `not exposed` because current operational persistence records their resulting skips, not transient allow decisions. The configured rate and budget consumption are exposed.

## Read and write boundaries

Frontier, acquisition, experiment, and artifact operations are read-only. A review is the sole UI write. It goes through `CorpusResearchQueryService` to the evaluation repository and is stored in `corpus_artifact_reviews`; content-addressed corpus JSON is never edited.

The query service limits frontier and artifact reads to 200 rows, resolves artifact paths beneath the configured corpus root, and avoids loading all text during ordinary dashboard refreshes.

## Limitations

- Manual refresh only; no push events or WebSockets.
- A currently processing URL is checkpoint-granular rather than event-stream granular.
- Transient allow decisions for robots and URL safety are not persisted.
- Extraction strategy is absent in older/current artifacts where acquisition provenance did not expose it.
- No authentication is provided; do not bind beyond localhost.
- No arbitrary crawl controls, browser extraction, rendered DOM inspection, or production frontend behavior are present.

Power BI, distributed telemetry, Redis, queues, Celery, and a production Next.js UI were deferred because bounded SQLite polling is sufficient for this experiment.
