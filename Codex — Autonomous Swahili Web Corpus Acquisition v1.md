# AUTONOMOUS ENGINEERING SESSION — WEB CORPUS ACQUISITION V1

You are continuing development of the existing:

# Swahili Linguistic Intelligence

repository.

This is a LONG AUTONOMOUS ENGINEERING SESSION.

I may be unavailable for several hours.

Do not stop after auditing or planning.

Do not wait for approval between normal engineering tasks.

Your operating loop is:

INSPECT CURRENT STATE
→ VERIFY BASELINE
→ PLAN
→ IMPLEMENT
→ TEST
→ REVIEW
→ FIX
→ DOCUMENT
→ COMMIT LOCALLY
→ SELECT NEXT TASK
→ CONTINUE

If one task is blocked, document it and continue with another safe independent task.

---

# 1. CURRENT PROJECT STATE

The previous engineering sessions have already completed major linguistic and software stabilization work.

Expected current baseline is approximately:

- Python 3.13.5
- 143 tests collected
- 142 passed
- 1 optional network test skipped
- 0 failures
- approximately 65% branch-aware coverage
- mypy clean
- formatting clean
- changed Python files Ruff-clean
- repository-wide Ruff debt remains pre-existing
- Git repository already initialized on `main`

DO NOT assume these numbers are still correct.

Verify them yourself before modifying production code.

Existing recent commits include approximately:

- `7affe15 feat: add Russell linguistic reference harness`
- `9fea9d5 docs: report linguistic harness and project layers`

Inspect the actual Git history.

---

# 2. CLEAN WORKTREE FIRST

Before beginning feature work:

Run:

git status
git log --oneline --decorate -10

There may still be an untracked file similar to:

`Codex — Linguistic Harness with Russell Swahili Manual.md`

This is a development prompt/harness.

DO NOT COMMIT IT.

Either:

- ignore it appropriately;
- or leave it untracked and document that fact.

Do not delete user-supplied material unless clearly safe.

Confirm that the Russell PDF remains ignored and is not tracked.

Never commit the copyrighted source PDF.

---

# 3. PRESERVE THE LINGUISTIC CONTRACT

Before changing any NLP-related code, read:

- LINGUISTIC_SPEC.md
- docs/linguistics/COMPUTATIONAL_MORPHOLOGY.md
- docs/linguistics/RUSSELL_RULE_INDEX.md
- docs/linguistics/LINGUISTIC_HARNESS_REPORT.md
- docs/PROJECT_LAYER_STATUS.md
- docs/WORKLOG.md

The linguistic contract is now intentionally explicit.

Do NOT silently redefine:

- surface form;
- lexeme;
- lemma;
- stem;
- root;
- radical;
- prefix;
- suffix;
- morpheme;
- inflection;
- derivation;
- final vowel;
- noun class;
- agreement marker;
- subject marker;
- object marker;
- tense/aspect;
- polarity;
- locative marker.

In particular:

- noun-class membership and agreement remain separate concepts;
- animate agreement must not rewrite morphological class membership;
- retained infinitival `ku-` must not be mislabeled as an object marker;
- the project continues to represent regular `som-a` as radical/root-like `som` plus final vowel `a`;
- current verbal analysis remains heuristic.

Do not reopen these decisions without compelling evidence.

---

# 4. DO NOT TURN THIS INTO ANOTHER LINGUISTICS SESSION

Known linguistic limitations include:

- zero-prefix JI/MA ambiguity;
- M/WA versus M/MI ambiguity;
- loanword class inference;
- automatic animacy;
- ordered derivational extensions;
- relative constructions;
- locative semantics;
- imperative morphology;
- surface concord morphophonemics.

These are NOT the main objective of this session.

Do not spend hours trying to solve them.

Only touch linguistic code if necessary to integrate acquired corpus content safely.

The next serious noun-class work should eventually use an independently reviewed gold evaluation set.

---

# 5. PRIMARY OBJECTIVE

Build the first real:

# Swahili Web Corpus Acquisition Pipeline

The target pipeline is:

PUBLIC WEB SOURCE
→ SAFE FETCH
→ PAGE INSPECTION
→ EXTRACTION STRATEGY
→ CONTENT EXTRACTION
→ NORMALIZATION
→ SWAHILI LANGUAGE VALIDATION
→ URL CANONICALIZATION
→ CONTENT HASHING
→ DEDUPLICATION
→ PROVENANCE
→ WEB DOCUMENT
→ LOCAL CORPUS STORAGE
→ OPTIONAL NLP ANALYSIS

This should turn the existing URL-analysis prototype into defensible research/data-engineering infrastructure.

Do not build a generic crawler framework.

Build the smallest real pipeline that demonstrates this flow end-to-end.

---

# 6. INSPECT THE EXISTING ACQUISITION FOUNDATION FIRST

The previous session reportedly added:

`src/acquisition`

and a Page Inspector accessible approximately as:

`python -m src.acquisition.inspector <URL>`

Inspect the actual implementation.

Do not duplicate existing functionality.

Map:

- fetcher;
- inspector;
- models;
- extraction;
- URL validation;
- metadata;
- tests.

Determine what is implemented and what is missing.

Create/update:

`docs/WEB_ACQUISITION_WORKLOG.md`

Record:

## Existing

## Missing

## Architectural decisions

## Tests

## Live-network limitations

## Next task

Keep updating this during the session.

---

# 7. PAGE INSPECTION IS THE CENTER OF THE ARCHITECTURE

The acquisition pipeline must inspect a page BEFORE deciding how to extract it.

The Page Inspector should be able to gather defensible signals such as:

- requested URL;
- final URL;
- canonical URL;
- HTTP status;
- content type;
- HTML language;
- title;
- meta description;
- author metadata when available;
- publication time when available;
- OpenGraph properties;
- JSON-LD;
- schema.org types;
- `<article>`;
- `<main>`;
- headings;
- paragraph counts;
- link counts;
- script counts;
- RSS/Atom links;
- sitemap hints;
- pagination hints;
- dynamic-page indicators.

Do not pretend heuristic signals are certainty.

Represent confidence/reasoning when useful.

---

# 8. EXTRACTION STRATEGY

Add a clear strategy-selection layer.

Conceptually, inspection should produce something like:

PageInspectionResult
→ ExtractionStrategy

Possible strategies:

- JSON_LD_ARTICLE
- SEMANTIC_ARTICLE
- MAIN_CONTENT
- GENERIC_PARAGRAPH
- RSS_ENTRY
- UNSUPPORTED
- DYNAMIC_BROWSER_REQUIRED

Exact names are implementation decisions.

The important principle is:

DO NOT immediately concatenate every `<p>`.

Prefer structural evidence.

---

# 9. EXTRACTION PRIORITY

Use approximately this order:

1. explicit structured article metadata;
2. schema.org / JSON-LD Article or NewsArticle;
3. semantic `<article>`;
4. meaningful `<main>`;
5. carefully filtered paragraph extraction;
6. dynamic-browser-required result.

Do not use browser automation simply because it is available.

STATIC FIRST.

---

# 10. STRUCTURED DATA EXTRACTION

Implement robust JSON-LD inspection where possible.

Handle:

- single JSON-LD objects;
- arrays;
- `@graph`;
- Article;
- NewsArticle;
- BlogPosting;
- WebPage where relevant.

Potential fields:

- headline;
- name;
- description;
- author;
- datePublished;
- dateModified;
- articleBody;
- inLanguage;
- mainEntityOfPage;
- publisher.

Do not trust JSON-LD blindly.

Cross-check against page structure when appropriate.

Do not invent absent metadata.

---

# 11. CANONICAL URL MODEL

Implement deterministic URL canonicalization suitable for deduplication.

Handle conservatively:

- fragments;
- obvious tracking parameters;
- canonical links;
- redirect destination;
- hostname normalization;
- default ports;
- scheme.

Do NOT aggressively rewrite arbitrary query parameters that could identify different content.

Keep:

original_url
final_url
canonical_url

as separate concepts where appropriate.

---

# 12. WEB DOCUMENT MODEL

Create or refine a canonical acquired-document representation.

A good conceptual target is:

WebDocument

with fields approximately equivalent to:

- document_id
- original_url
- final_url
- canonical_url
- source_domain
- title
- author
- published_at
- retrieved_at
- language
- language_confidence
- raw_text
- normalized_text
- content_hash
- extraction_method
- extraction_metadata
- provenance

Adapt names to existing architecture.

Do NOT create fields that cannot be populated meaningfully.

Missing metadata should remain missing.

Do not fabricate values.

---

# 13. RAW VERSUS NORMALIZED CONTENT

Preserve the distinction:

RAW
vs
NORMALIZED

Raw text should represent extracted textual content before linguistic normalization.

Normalized text may apply safe cleanup such as:

- Unicode normalization;
- whitespace normalization;
- repeated blank-line reduction;
- boilerplate cleanup;
- duplicated paragraph removal;
- zero-width character handling.

Do NOT:

- lowercase everything by default;
- strip meaningful punctuation;
- destroy paragraph boundaries;
- rewrite Swahili morphology;
- stem text;
- lemmatize during acquisition.

Acquisition and linguistic analysis are separate stages.

---

# 14. SWAHILI LANGUAGE VALIDATION

Implement a dedicated language-validation layer.

Do NOT decide language solely from:

`<html lang="sw">`

Use multiple signals where practical.

Potential evidence can include:

- HTML language declaration;
- metadata language;
- existing language-detection dependency if lightweight and defensible;
- characteristic Swahili function-word evidence;
- corpus-derived lexical evidence already available in the project.

Avoid circular reasoning.

Do not classify text as Swahili merely because a few common tokens occur.

Represent a result conceptually like:

LanguageValidationResult:
    language
    confidence
    evidence
    is_acceptable

If no calibrated confidence model exists, do not call a heuristic score a statistically calibrated probability.

Document the distinction.

---

# 15. MULTILINGUAL CONTENT

Web pages can contain:

- Swahili article body;
- English navigation;
- advertisements;
- translated snippets;
- bilingual content.

Language validation should focus primarily on extracted article content, not the entire raw DOM.

Support outcomes such as:

- likely Swahili;
- multilingual;
- likely non-Swahili;
- uncertain.

Do not reject a legitimate Swahili article because surrounding website chrome is English.

---

# 16. DEDUPLICATION

Implement exact-content deduplication first.

Use a stable hash over normalized content.

For example conceptually:

SHA-256(normalized_text)

Also consider canonical URL duplication.

A document can therefore be duplicate because:

- canonical URL already exists;
- normalized content hash already exists.

Keep URL identity and content identity distinct.

Do NOT implement embeddings-based near-duplicate detection yet unless core requirements are already complete.

Document near-duplicate detection as future work.

---

# 17. PROVENANCE

Provenance is mandatory.

Every acquired document must remain traceable to its source.

Store enough metadata to answer:

- Where did this text come from?
- Which URL produced it?
- When was it retrieved?
- Which extraction strategy was used?
- What canonical URL was discovered?
- What content hash was generated?
- Which acquisition implementation/version processed it?

A research corpus without provenance is not acceptable.

---

# 18. STORAGE LIFECYCLE

Design a simple local storage lifecycle.

Conceptually:

data/
    raw/
    processed/
    corpus/

or an equivalent existing convention.

Do not restructure existing data directories unnecessarily.

Distinguish:

RAW FETCH/EXTRACTION
NORMALIZED DOCUMENT
CORPUS DOCUMENT
GENERATED ARTIFACT

Do not commit downloaded corpora to Git by default.

Add appropriate paths to `.gitignore`.

Provide small synthetic fixtures for tests.

---

# 19. CORPUS MANIFEST

Implement a lightweight manifest or index for acquired documents.

It should make it possible to inspect corpus contents without loading every full document.

Useful fields may include:

document_id
canonical_url
domain
title
published_at
retrieved_at
language
content_hash
extraction_method
storage_path

Choose a simple reproducible format such as:

JSONL
or another existing project convention.

Do not add a database solely for this if a manifest is sufficient.

---

# 20. IDEMPOTENT INGESTION

Running ingestion twice against the same content should not silently create duplicate corpus documents.

Test:

same URL twice
same canonical URL through different tracking URLs
same content through different URLs
changed content at same URL

Define behavior explicitly.

Do not overwrite historical material silently.

If versioning changed content is outside v1 scope, document the limitation.

---

# 21. DISCOVERY — LIMITED V1

Implement only bounded discovery.

Useful v1 capabilities:

- RSS/Atom feed discovery;
- sitemap discovery;
- article links discovered from a seed page.

Do NOT create an unrestricted recursive spider.

All discovery must support limits such as:

- allowed domains;
- maximum pages;
- maximum depth where applicable;
- timeouts;
- delay/rate settings.

A seed URL must never imply unlimited crawling.

---

# 22. RSS / ATOM

If inspection discovers RSS or Atom:

Parse feeds safely.

Extract candidate article URLs and available metadata.

Do not treat RSS content as authoritative over the final article if the article can be fetched and inspected.

Preserve feed provenance when useful.

Add offline feed fixtures.

---

# 23. SITEMAP SUPPORT

Support:

- sitemap.xml;
- sitemap index;
- URL entries.

Bound how many URLs are returned.

Do not recursively download huge sitemap graphs without explicit limits.

Test with local fixtures.

---

# 24. SAFE FETCHING MUST REMAIN INTACT

The previous session hardened URL fetching against:

- URL credentials;
- unsupported schemes;
- local hostnames;
- non-global resolved IPs;
- unsafe redirects;
- invalid content types;
- oversized responses.

Do not regress these controls.

Preserve:

- bounded redirects;
- redirect revalidation;
- content-type checks;
- response-size limit;
- timeout;
- identifiable user agent;
- HTTP(S)-only policy.

Maintain explicit documentation that application-level filtering does not fully solve DNS rebinding.

Do not claim complete SSRF elimination.

---

# 25. RESPONSIBLE ACQUISITION

The project is intended for acquisition of PUBLIC Swahili-language material for research.

Do not implement:

- authentication bypass;
- CAPTCHA bypass;
- login automation;
- stolen cookies;
- paywall circumvention;
- private API access;
- access-control evasion;
- fingerprint evasion;
- stealth bot behavior.

Respect site policies and reasonable request rates.

Where appropriate inspect:

robots.txt

and document policy behavior.

Do not build a system intended to evade blocking.

---

# 26. SOURCE ADAPTERS

Do not immediately create adapters for dozens of sites.

First build a strong generic pipeline.

Only introduce a SourceAdapter abstraction if real differences between sources justify it.

A source-specific adapter should be a small extension around the common acquisition pipeline, not an entirely separate scraper.

Do not create empty architecture.

---

# 27. LIVE WEBSITE TESTING

Unit and normal integration tests MUST NOT depend on live websites.

Create fixtures for:

- semantic news article;
- JSON-LD article;
- OpenGraph article;
- article with navigation noise;
- multilingual page;
- non-Swahili page;
- duplicate page;
- canonical URL;
- RSS feed;
- sitemap;
- malformed JSON-LD;
- dynamic-content placeholder.

Live tests must remain OPTIONAL and clearly marked.

Network failure must not make the normal test suite fail.

---

# 28. PAGE INSPECTOR CLI V2

Improve the developer CLI if useful.

A command conceptually like:

python -m src.acquisition.inspector <URL>

should report structured information useful for developing acquisition support.

Potential output:

URL
Final URL
Canonical URL
HTTP status
Content type
HTML language
Detected article title
JSON-LD types
OpenGraph fields
Possible article container
Paragraph count
Feed discovery
Sitemap hints
Dynamic indicators
Recommended extraction strategy
Language validation
Warnings

Support JSON output if straightforward, e.g.:

`--json`

Do not overbuild CLI presentation.

---

# 29. CORPUS INGESTION CLI

If architecture is stable, add a simple CLI approximately equivalent to:

python -m src.acquisition.ingest <URL>

or another coherent project command.

Possible options:

--output
--max-pages
--allowed-domain
--dry-run

Dry-run should inspect and report without persisting corpus data.

Actual CLI design is up to you.

Do not build a huge command framework.

---

# 30. NLP INTEGRATION

After a WebDocument has successfully entered the corpus, make it possible to pass normalized content into existing NLP analysis.

Maintain this boundary:

ACQUISITION
≠
LINGUISTIC ANALYSIS

The acquisition pipeline should not know the details of:

- noun-class agreement;
- verbal morphology;
- root analysis.

Instead:

WebDocument
→ NLP/Application Service

Do not tightly couple `src/acquisition` to internal morphology implementation.

---

# 31. CORPUS-LEVEL DEMONSTRATION

Create a small offline demonstration using fixtures.

Show:

3–5 article-like fixture documents
→ inspection
→ extraction
→ language validation
→ deduplication
→ provenance
→ corpus manifest

Then optionally:

corpus document
→ existing NLP analysis

This should be fully reproducible without internet access.

---

# 32. ADVANCED PAGE INSPECTION — PHASE 2 ONLY

After all static acquisition P0/P1 tasks are healthy, investigate browser-assisted inspection.

Do NOT make it mandatory for the basic installation.

Potential optional stack:

Playwright

or an equivalent justified tool.

The purpose is NOT merely:

render page → grab text

The purpose is inspection.

Browser-assisted inspection should eventually examine:

- rendered DOM;
- hydration behavior;
- script-generated content;
- network requests;
- fetch/XHR requests;
- public JSON endpoints used by the page;
- lazy-loaded article content.

This is an EXPERIMENTAL P2 capability.

---

# 33. NETWORK INSPECTION

If browser work is reached:

Capture metadata about fetch/XHR requests initiated by a PUBLIC page.

Look for structured article/content APIs.

For example conceptually:

Rendered Web Page
→ Network Inspection
→ Public XHR request
→ Structured JSON article data

Do NOT:

- capture credentials;
- reuse authenticated tokens;
- expose cookies;
- bypass access control;
- call private/internal APIs.

Only analyze requests accessible as part of normal public page loading.

---

# 34. STATIC VERSUS DYNAMIC DECISION

The inspector should eventually be able to communicate something like:

STATIC_SUFFICIENT

or:

STRUCTURED_ENDPOINT_AVAILABLE

or:

BROWSER_RENDER_REQUIRED

or:

UNSUPPORTED

Do not use Playwright for pages that static HTTP extraction handles correctly.

This distinction is an important engineering goal.

---

# 35. OBSERVABILITY

Add useful acquisition metrics.

Examples:

pages_inspected
pages_fetched
pages_failed
documents_extracted
swahili_documents
non_swahili_rejected
uncertain_language
duplicates_by_url
duplicates_by_hash
rss_urls_discovered
sitemap_urls_discovered
dynamic_pages_detected

Do not introduce Prometheus or distributed observability infrastructure for this local v1.

Simple structured counters/logs are sufficient.

---

# 36. ERROR TAXONOMY

Do not reduce every acquisition failure to:

Exception

Create or reuse meaningful failure categories when beneficial:

UnsafeURL
FetchTimeout
HTTPFailure
UnsupportedContentType
ResponseTooLarge
ExtractionFailure
LanguageRejected
DuplicateDocument
UnsupportedDynamicPage

Do not create excessive exception hierarchy.

The goal is diagnosability.

---

# 37. LOGGING

Ensure logs help answer why a document was rejected.

Avoid logging:

- secrets;
- credentials;
- cookies;
- massive HTML bodies.

Useful log context:

document URL
canonical URL
strategy
status
language decision
duplicate reason
failure category

---

# 38. TEST TARGET

Do not chase an arbitrary coverage number.

Maintain or improve the current overall 65% where naturally possible.

More importantly, new acquisition modules should receive strong focused coverage.

Prefer high coverage of:

- inspector;
- canonicalization;
- language validation;
- normalization;
- deduplication;
- provenance;
- storage;
- discovery.

Do not write meaningless tests merely to increase global coverage.

---

# 39. QUALITY DEBT

Repository-wide Ruff currently has substantial known legacy debt.

Do NOT spend the session fixing unrelated old lint issues.

Rule:

all NEW or MODIFIED Python files should pass Ruff.

Mypy should remain clean if currently clean.

Formatting should remain clean.

Do not turn this feature session into a repository-wide style rewrite.

---

# 40. DATETIME MODERNIZATION

The previous run reported many naive UTC deprecation warnings.

As files are touched, migrate semantically appropriate code from naive UTC patterns to timezone-aware UTC.

Prefer conceptually:

datetime.now(timezone.utc)

Do not perform a blind repository-wide search/replace without tests.

If a small safe dedicated cleanup eliminates a large number of warnings, it is acceptable as a bounded commit.

---

# 41. DOCUMENTATION

Create/update:

docs/WEB_ACQUISITION.md
docs/PAGE_INSPECTION.md
docs/CORPUS_PROVENANCE.md
docs/WEB_ACQUISITION_WORKLOG.md

Update README only where needed.

Document:

architecture
pipeline
safety model
inspection strategy
language validation
deduplication
provenance
corpus storage
CLI
testing
limitations
responsible acquisition
future browser inspection

Do not describe planned browser/network inspection as implemented unless it actually exists.

Clearly distinguish:

IMPLEMENTED
EXPERIMENTAL
PLANNED

---

# 42. ARCHITECTURE DIAGRAM

Document a Mermaid pipeline equivalent to:

Public Web
    ↓
SafeFetcher
    ↓
PageInspector
    ↓
StrategySelector
    ↓
Extractor
    ↓
Normalizer
    ↓
LanguageValidator
    ↓
Canonicalizer / Deduplicator
    ↓
Provenance
    ↓
WebDocument
    ↓
Corpus Storage
    ↓
NLP Services

If browser inspection exists:

PageInspector
    ↓
Dynamic Required?
    ├── No → Static extraction
    └── Yes → Optional Browser Inspector

Do not make the diagram claim functionality that does not exist.

---

# 43. GIT COMMITS

Continue using local Git commits.

Before each commit:

run relevant tests
run git diff --check
inspect git status
inspect staged diff

Never commit:

- Russell PDF;
- user harness prompts;
- downloaded corpora;
- local databases;
- `.env`;
- coverage files;
- caches;
- credentials;
- private content.

Potential commit structure:

feat: add canonical web document model

feat: implement structured article extraction

feat: add swahili language validation

feat: add provenance and corpus deduplication

feat: add bounded feed and sitemap discovery

test: expand acquisition pipeline coverage

feat: add optional browser inspection foundation

docs: document web corpus acquisition pipeline

Use actual work to determine commit boundaries.

Do not create empty/artificial commits.

Do NOT push remotely.

---

# 44. SECURITY REVIEW BEFORE SESSION END

Perform another acquisition-specific security review.

Check:

- SSRF regressions;
- redirects;
- URL canonicalization;
- response-size handling;
- malformed HTML;
- malformed JSON;
- path traversal in corpus storage;
- malicious filenames;
- manifest injection;
- unsafe deserialization;
- HTML/script execution;
- browser context isolation if Playwright is introduced.

Acquired web content must be treated as UNTRUSTED DATA.

Never execute JavaScript extracted from a page outside an isolated browser context.

Never evaluate arbitrary page-provided code.

---

# 45. ADVERSARIAL TESTS

Add adversarial fixtures for cases such as:

- canonical URL points elsewhere;
- malformed JSON-LD;
- huge paragraph repeated many times;
- duplicate tracking URLs;
- mixed English/Swahili navigation;
- tiny Swahili snippet inside English page;
- misleading `lang="sw"` page containing English text;
- duplicated article body;
- article text hidden among boilerplate;
- redirect to disallowed address;
- content type claiming HTML incorrectly;
- same content under two URLs.

The objective is robustness, not merely happy-path extraction.

---

# 46. DEFINITION OF DONE — P0

P0 is complete when:

- baseline still passes;
- safe fetch remains enforced;
- Page Inspector is integrated into acquisition;
- canonical WebDocument exists;
- deterministic extraction exists;
- text normalization exists;
- language validation exists;
- exact content hashing exists;
- deduplication exists;
- provenance exists;
- local storage exists;
- tests use offline fixtures;
- no new secrets/private content are tracked.

Do not stop merely because P0 is complete.

Continue into P1.

---

# 47. DEFINITION OF DONE — P1

P1 is complete when an offline fixture can demonstrably execute:

SEED
→ INSPECT
→ EXTRACT
→ NORMALIZE
→ VALIDATE SWAHILI
→ HASH
→ DEDUPLICATE
→ STORE
→ MANIFEST

and:

- repeated ingestion is idempotent;
- source provenance remains available;
- CLI or application service can execute the pipeline;
- documentation reproduces it;
- relevant tests pass.

Also implement bounded:

- RSS discovery;
- sitemap discovery;

if this can be done without destabilizing P0.

---

# 48. DEFINITION OF DONE — P2

Only after P0 and P1:

Explore OPTIONAL browser-assisted inspection.

P2 success can be as small as:

- optional dependency;
- isolated BrowserInspector;
- one local/deterministic dynamic-page fixture or controlled example;
- rendered DOM inspection;
- identification of fetch/XHR metadata;
- classification that browser assistance was required.

Do NOT make browser acquisition mandatory.

Do NOT build a large crawling platform.

---

# 49. AUTONOMOUS CONTINUATION RULE

Every time you finish a task:

1. update WEB_ACQUISITION_WORKLOG.md;
2. run focused tests;
3. fix regressions;
4. run quality checks for touched files;
5. inspect Git diff;
6. make a local commit when coherent;
7. choose the next highest-value P0/P1 task;
8. continue.

Do not return to me for routine approval.

Do not stop after producing documentation.

Do not merely propose implementation.

Implement it.

---

# 50. WHEN TO STOP

Stop only if:

A. P0 and P1 are fully implemented, tested, reviewed and documented, and useful P2 work has either been completed or explicitly deferred;

OR

B. all remaining work requires an external credential, privileged system operation, potentially destructive decision, or product decision that cannot safely be inferred;

OR

C. the runtime prevents further safe implementation.

If blocked:

document the blocker and continue on independent tasks.

---

# 51. FINAL VALIDATION

Before finishing, run the complete validation suite available in the repository.

At minimum attempt:

pytest with branch coverage

mypy

format check

Ruff on all newly changed files

import smoke tests

FastAPI import/startup smoke test

acquisition CLI smoke test

offline corpus pipeline smoke test

git diff --check

git status

git log --oneline --decorate -15

Do not hide warnings or failures.

Record exact measured values.

---

# 52. FINAL REPORT

Create:

docs/WEB_ACQUISITION_SESSION_REPORT.md

Include:

## Starting state

## Baseline validation

## Existing Page Inspector assessment

## Architecture implemented

## WebDocument model

## Extraction strategies

## Language validation

## Normalization

## URL canonicalization

## Deduplication

## Provenance

## Corpus storage

## RSS/sitemap discovery

## Security review

## Tests added

## Final test results

## Coverage

## Quality checks

## Git commits

## Browser-inspection progress

## Known limitations

## Blocked items

## Recommended next session

Also update:

docs/WORKLOG.md

with a concise checkpoint linking to the acquisition report.

---

# 53. FINAL TERMINAL SUMMARY

When the session is complete, print a concise summary containing:

- tests passed / skipped / failed;
- global branch coverage;
- acquisition-module coverage if available;
- documents successfully processed in offline demo;
- number of acquisition strategies implemented;
- language-validation status;
- deduplication status;
- provenance status;
- RSS/sitemap status;
- browser-inspection status;
- commits created;
- Git worktree status;
- highest-value remaining task.

Begin now.

Do not merely summarize this prompt.

Inspect the existing repository and continue development from the current Git state.