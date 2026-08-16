# Live Crawl Demonstration v1

## Purpose

This interface makes Responsible Crawl Orchestration v1 and Web Corpus Acquisition v1
observable during a deliberately tiny, sequential crawl of exactly three public
Swahili-language sites. It is a portfolio demonstration, not a corpus-scale collector.

## Architecture and responsibility

The implementation is in `src/demo/live_crawl.py`, outside the domain. Its composition is:

```text
Live Demo CLI ──> Firefox/system viewer (human visualization only)
      |
      +──> CrawlOrchestrator ──> crawl domain and persistent SQLite frontier
                    |
                    +──> safe robots retrieval and origin rate scheduler
                    +──> SSRF-aware SafeFetcher boundary
                              |
                              +──> PageInspector and AcquisitionPipeline
                                      └──> SHA-256 CorpusStore
```

Firefox receives only the URL chosen by the crawler. It does not supply DOM, text, network
traffic, or decisions. `URLNewsAnalyzer.fetch_result` remains the safe acquisition boundary;
`PageInspector` performs static inspection; `AcquisitionPipeline` owns extraction, Swahili
validation, canonicalization, deduplication, provenance, and storage; and
`CrawlOrchestrator` owns navigation and policy.

The demo-only tracing adapter records real safe-fetch, inspection, and ingestion return
values for presentation. It does not decide whether a document is accepted.

## Running

Install the repository's existing web dependencies, then run:

```bash
python -m src.demo.live_crawl
```

Conservative options are intentionally restricted:

```bash
python -m src.demo.live_crawl \
  --max-pages-per-site 3 \
  --max-depth 1 \
  --demo-delay 2
```

`--max-pages-per-site` accepts 1–3, `--max-depth` accepts 0–1, and `--demo-delay`
accepts 0–10 seconds. The demo delay is presentation timing; it is separate from the
origin-scoped scheduler's two-second minimum. Defaults produce at most three attempts per
origin and nine overall. Sites are processed sequentially.

Generated state is under `data/live-crawl-demo/` by default and is ignored by Git. The
SQLite file is the persistent crawl frontier; the corpus directory contains immutable JSON
documents plus the JSONL manifest.

## Terminal output

For each selected frontier URL, the terminal reports the URL-safety result, current robots
decision, configured and effective rate policy, frontier state, browser action, fetch
metadata, static inspection evidence, pipeline outcome, language evidence score, corpus
identity/provenance fields, discovery totals, and next action. The language score is labeled
as a heuristic evidence score, never a probability. Unavailable metrics are explicitly
reported rather than inferred.

Failures remain visible. A robots denial skips acquisition; a network or extraction failure
uses the existing frontier transition; a language rejection creates no artifact; and a
static/dynamic limitation does not trigger browser scraping.

## Sites and live run

Live run date: **2026-08-16**. Web accessibility and robots policies can change, so all three
are re-evaluated on every run and are not claimed to be permanently compatible.

| Site | Seed/origin | Selection reason | Live robots result | Attempted | Completed | Skipped | Failed | New artifacts | Termination |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| VOA Swahili | `https://www.voaswahili.com/` | Public Swahili news with ordinary category/article links | allowed | 3 | 1 | 27 | 2 | 1 | page budget exhausted |
| DW Kiswahili | `https://www.dw.com/sw/` | Public Kiswahili news and feature publishing | allowed | 3 | 2 | 18 | 1 | 1 | page budget exhausted |
| UN News Kiswahili | `https://news.un.org/sw/` | Public institutional reporting in Swahili | allowed | 3 | 1 | 34 | 2 | 1 | page budget exhausted |

The run discovered 305 canonical frontier URLs but attempted only 9. It completed 4,
skipped 79 (including external-origin/depth exclusions), failed 5 acquisition attempts,
stored 3 new artifacts, and detected 1 canonical-URL duplicate. No robots denial occurred.
Two failures were explicit language rejections after UN language-selector links led to Arabic
and Chinese pages; two VOA category pages and one DW video page lacked sufficient static
article content.

Browser visualization was unavailable in this WSL2 session. `DISPLAY=:0`,
`WAYLAND_DISPLAY=wayland-0`, and WSL interoperability were present, but no `firefox`,
`firefox.exe`, `wslview`, or `xdg-open` executable was on `PATH`. The terminal crawl
continued normally without installing or invoking browser automation.

## Relationship to existing components

The CLI creates one existing `CrawlJob` and `CrawlBudget` per origin. The existing SQLite
repository provides frontier persistence/checkpoints, the robots service evaluates publisher
policy fail-closed, the scheduler applies origin pacing, and `Web Corpus Acquisition v1`
creates content-addressed artifacts with Brazilian scientific provenance unchanged. The demo
adds presentation and composition only; it does not alter linguistic contracts.

## Known limitations and recommendation

- Browser process availability can be detected, but a browser can still fail after launch;
  such failure is displayed and does not affect acquisition.
- Breadth-first frontier order follows document link order. Language selectors and category
  pages can consume the intentionally tiny budget before article pages.
- Pipeline rejection detail is compact; some extraction/language internals are not currently
  exposed for rejected pages.
- Live sites, DNS, redirects, content, and robots policies are mutable.

The evidence supports **Corpus Acquisition Observability / Quality Hardening** as the next
milestone, before Public Swahili Corpus Pilot v1. In particular, policy-preserving link
eligibility should recognize language-path signals and prioritize likely article URLs, while
rejection telemetry should expose structured extraction and language details without moving
those decisions into the crawler or demo.
