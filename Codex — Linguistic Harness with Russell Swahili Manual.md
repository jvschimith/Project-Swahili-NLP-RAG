# AUTONOMOUS LINGUISTIC ENGINEERING SESSION

You are continuing development of the existing project:

# Swahili Linguistic Intelligence

This repository has already undergone an engineering audit and refactor.

Current verified baseline from the previous session includes approximately:

- 129 tests collected;
- 128 passing;
- 1 optional network test skipped;
- 0 failing;
- approximately 65% branch-aware coverage;
- hardened URL acquisition;
- static page inspection foundation;
- Git repository with incremental local commits;
- no actual RAG pipeline despite historical naming.

You must verify the current repository state yourself before relying on these numbers.

This is another LONG AUTONOMOUS SESSION.

I will be unavailable for several hours.

Do not stop after analysis.

Your loop is:

INSPECT
→ MODEL
→ FORMALIZE
→ IMPLEMENT
→ TEST
→ REVIEW
→ DOCUMENT
→ COMMIT LOCALLY
→ SELECT NEXT TASK
→ CONTINUE

Do not ask for approval for ordinary safe engineering decisions.

---

# 1. NEW PRIMARY REFERENCE

A local PDF reference is being added to the project:

**Swahili — Teach Yourself, Joan Russell, 1996**

The file may exist under a path such as:

`references/Swahili_Teach_Yourself_Russell_1996.pdf`

or another local path provided in the workspace.

Locate the PDF before starting.

If needed, create an appropriate local reference directory such as:

`references/private/`

or:

`data/references/`

Use whichever location best matches the existing repository architecture.

IMPORTANT:

The PDF is a COPYRIGHTED linguistic reference.

It must NOT be committed to the public Git repository.

Add the PDF path/pattern to `.gitignore`.

Do NOT reproduce substantial passages from the book in repository documentation.

Do NOT copy entire tables, dialogues, exercises, vocabulary sections or chapters.

Use the book to derive:

- linguistic facts;
- formalized rules;
- small factual examples when necessary;
- synthetic examples;
- test cases;
- implementation requirements;
- terminology comparisons;
- provenance metadata.

The repository should contain DERIVED KNOWLEDGE, not a reproduction of the book.

---

# 2. PURPOSE OF THE MANUAL

The manual is not being added as ordinary training data.

It will serve as a:

# Linguistic Reference Harness

Its purpose is to help verify and expand the computational linguistic model.

The desired traceability is:

LINGUISTIC SOURCE
→ RULE IDENTIFICATION
→ FORMAL RULE
→ IMPLEMENTATION
→ TEST CASE
→ EVALUATION

The source must inform the implementation, but must not automatically override the existing linguistic contract.

---

# 3. SOURCE PRECEDENCE

When linguistic sources disagree, use this hierarchy:

1. explicit current project linguistic specification;
2. reproducible project invariants;
3. Russell manual;
4. existing implementation;
5. legacy tests;
6. historical README/documentation.

However:

If the Russell manual exposes a likely error in the current `LINGUISTIC_SPEC.md`, do NOT silently ignore it.

Document the conflict explicitly.

Create a category:

`LINGUISTIC_CONFLICT`

and record:

- project rule;
- manual rule;
- examples;
- likely interpretation;
- implementation impact;
- recommendation.

Do not make major semantic changes when evidence is genuinely ambiguous.

---

# 4. READ EXISTING PROJECT STATE FIRST

Before modifying linguistic code, inspect:

- AGENTS.md
- LINGUISTIC_SPEC.md
- README.md
- pyproject.toml
- docs/TECHNICAL_AUDIT.md
- docs/REFACTOR_PLAN.md
- docs/ARCHITECTURE.md
- docs/WORKLOG.md
- docs/SESSION_REPORT.md
- docs/WEB_ACQUISITION_ROADMAP.md

Inspect all linguistic/domain modules under:

`src/domain/`

and relevant application modules.

Inspect existing linguistic tests.

Inspect current Git status and history.

Run the current test suite before substantial changes.

Record a new baseline checkpoint in `docs/WORKLOG.md`.

---

# 5. INSPECT THE MANUAL STRUCTURE

Do not read the PDF as an undifferentiated block.

Create an index of relevant linguistic topics.

The manual contains progressively introduced grammatical material, including topics such as:

- pronunciation and syllable structure;
- noun classes;
- singular/plural noun prefixes;
- agreement;
- subject markers;
- verbal tense markers;
- negation;
- possessives;
- adjectival agreement;
- numerals;
- locatives;
- infinitives;
- imperatives;
- monosyllabic verbs;
- foreign-origin verbs;
- relative constructions;
- derivational morphology;
- vocabulary and examples.

The book also contains:

- dialogues;
- explanations;
- exercises;
- grammatical summaries;
- Swahili-English vocabulary;
- English-Swahili vocabulary.

Use explanatory and grammatical sections primarily.

Do NOT mine or reproduce the entire vocabulary or dialogue corpus.

---

# 6. CREATE A FORMAL LINGUISTIC SOURCE INDEX

Create:

`docs/linguistics/RUSSELL_RULE_INDEX.md`

This file must NOT contain long quotations.

For each relevant rule, record something conceptually like:

## SW-RUSSELL-001

Topic:
M/WA noun class

Source:
Russell 1996, Unit 1, noun classes

Concept:
Human-denoting nouns commonly use singular m-/mw- and plural wa-.

Examples:
Synthetic or minimal examples only.

Project mapping:
- BantuClass
- noun class analyzer
- agreement engine

Status:
- IMPLEMENTED
- PARTIAL
- MISSING
- CONFLICT
- NOT APPLICABLE

Tests:
- test_...
- test_...

Notes:
...

Do this systematically.

Aim for linguistic coverage, not raw number of rules.

---

# 7. CREATE A COMPUTATIONAL LINGUISTIC MODEL DOCUMENT

Create:

`docs/linguistics/COMPUTATIONAL_MORPHOLOGY.md`

Formalize the terminology used by the project.

Explicitly distinguish:

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
- tense/aspect marker;
- polarity;
- locative marker.

Do not allow these terms to be used interchangeably in code documentation.

Where the Russell manual uses pedagogical terminology that differs from the project terminology, document the mapping.

Example:

Russell pedagogical term
→ computational project term

Do not claim the manual uses modern computational-linguistic terminology when it does not.

---

# 8. NOUN CLASS SYSTEM

Perform a deep review of the existing noun-class representation.

At minimum evaluate:

- M/WA;
- N;
- KI/VI;
- JI/MA;
- M/MI;
- U;
- locative classes if represented;
- animate agreement behavior;
- loan-word behavior.

Do not model noun classes only as prefix lists.

Evaluate whether the project needs separate representations for:

NOUN CLASS MEMBERSHIP

and:

AGREEMENT PARADIGM

because some nouns may belong morphologically to one class but exhibit animate/human agreement behavior.

Formalize, where supported:

- singular noun prefix;
- plural noun prefix;
- subject agreement;
- adjective agreement;
- possessive agreement;
- demonstrative agreement;
- numeral agreement;
- relative agreement.

Avoid a giant hard-coded matrix if smaller typed structures are clearer.

---

# 9. NOUN MORPHOLOGY TEST HARNESS

Build curated tests from linguistic rules.

Do NOT copy the book's exercises verbatim.

Generate synthetic tests inspired by the rules.

Include cases similar in linguistic structure to:

singular → plural

noun → class

noun + adjective agreement

noun + possessive agreement

noun + numeral agreement

animate noun agreement

loan-word class behavior

ambiguous prefix cases

Every test must be traceable to a rule ID where practical.

For example:

`SW-RUSSELL-NOUN-001`

→ test case

→ implementation

This relationship should be documented.

---

# 10. VERBAL MORPHOLOGY

This is a high-priority area.

The current project already distinguishes the radical from the final vowel.

Preserve the current contract unless evidence strongly justifies change.

For example:

`soma`

may conceptually be represented as:

radical = `som`
final vowel = `a`

Do not collapse those fields accidentally.

Develop a more explicit verbal structure.

Evaluate a model conceptually equivalent to:

VerbAnalysis:
    surface_form
    polarity
    subject_marker
    tense_aspect_marker
    relative_marker
    object_marker
    root
    derivational_extensions
    final_vowel
    infinitive_marker
    confidence

Do not add fields that the current implementation cannot meaningfully populate.

---

# 11. SUBJECT MARKERS

Formalize human/person subject markers and relevant noun-class subject agreement.

Test cases should include structures equivalent to:

ni-
u-
a-
tu-
m-
wa-

and appropriate class agreement markers.

Ensure verbal evidence is evaluated before shallow noun-prefix matching.

The previous bug where a conjugated verb could be classified as an N-class noun must remain covered by regression tests.

---

# 12. TENSE / ASPECT / MOOD

Review the tense/aspect system currently supported.

Use the manual as a linguistic reference for structures it explicitly documents.

At minimum inspect current handling of:

- present;
- past;
- future;
- negative present;
- negative past;
- negative future;
- infinitive;
- imperative.

Do not implement every grammatical construction merely because the book mentions it.

Classify each construction:

SUPPORTED
PARTIAL
MISSING
FUTURE

Prioritize correctness of existing capabilities before expanding.

---

# 13. NEGATION

Formalize the distinction between:

subject marker
+
negative marking
+
tense/aspect behavior
+
final vowel behavior

Avoid implementing negation as a generic string prefix.

Account for:

- person-specific negative subject forms;
- tense-specific negative behavior;
- final-vowel alternation when linguistically applicable;
- verbs of foreign origin;
- irregular/monosyllabic verbs where supported.

Add focused tests.

---

# 14. MONOSYLLABIC AND IRREGULAR VERBS

Audit support for verbs such as those that preserve `ku-` in particular tense environments.

Do not assume normal verb parsing applies universally.

Create an explicit documented class/category if computationally useful.

Add regression fixtures.

---

# 15. DERIVATIONAL MORPHOLOGY

Inspect whether the existing domain model supports derivation meaningfully.

The project already conceptually supports:

Lexeme
→ WordForm
→ Derivation

Use the manual to identify relevant derivational phenomena where clearly explained.

Do not implement speculative derivations.

Where derivational extensions are supported, represent them explicitly rather than merely storing strings.

Conceptual example:

VerbDerivation:
    base_root
    extension_type
    derived_stem
    semantic_effect
    confidence

Possible extension categories should only be added when verified by sources and supported by tests.

---

# 16. LOCATIVES

Formalize current handling of locative forms.

The manual distinguishes forms conceptually corresponding to:

-ko
-po
-mo

with different locational functions.

Audit whether the current project models these distinctions.

If not, decide whether they belong in:

P1 implementation

or:

P2 roadmap.

Add tests if implemented.

Do not overstate semantic precision where usage is context-dependent.

---

# 17. AGREEMENT ENGINE

Evaluate whether agreement rules are currently scattered across:

- noun analyzer;
- adjective logic;
- verb morphology;
- hard-coded dictionaries.

If so, consider introducing a small cohesive agreement layer.

Potential responsibilities:

noun_class
→ subject agreement
→ adjective agreement
→ possessive agreement
→ numeral agreement
→ relative agreement

Do not create an excessively generic framework.

The goal is to eliminate inconsistent duplicated rules.

---

# 18. MORPHOLOGICAL CONFIDENCE

Many surface forms are ambiguous.

Do not force deterministic analysis when evidence is weak.

Where appropriate, support:

analysis
confidence
evidence

Conceptual example:

{
  "surface": "...",
  "analysis": {...},
  "confidence": 0.82,
  "evidence": [
    "subject marker match",
    "tense marker match",
    "known root"
  ]
}

Do not invent fake probabilistic precision.

If confidence is heuristic, document it as heuristic.

---

# 19. LINGUISTIC RULE REGISTRY

If beneficial, create a machine-readable rule registry.

For example:

`data/linguistic_rules/`

or an equivalent package structure.

Possible format:

YAML
JSON
typed Python structures

Each rule may include:

rule_id
category
description
source_reference
status
examples
known_exceptions

Do not reproduce copyrighted text.

The registry should contain formalized linguistic facts and synthetic examples.

Only implement this if it improves maintainability.

---

# 20. GOLD / CURATED EVALUATION SET

Create a small curated evaluation suite.

Suggested categories:

- noun-class identification;
- singular/plural relation;
- subject marker detection;
- tense recognition;
- negative forms;
- roots/radicals;
- final vowels;
- locatives;
- agreement;
- derivational morphology.

Do NOT copy textbook exercises.

Create independent examples demonstrating the same rules.

Store them in a format suitable for testing, e.g.:

`tests/fixtures/linguistics/`

or:

`data/evaluation/linguistics/`

Keep it intentionally small and high quality.

---

# 21. PROPERTY-BASED OR PARAMETRIC TESTING

Where useful, turn paradigms into parameterized tests.

Example conceptually:

subject_marker
×
tense_marker
×
root

rather than manually duplicating identical test logic.

However, preserve explicit regression tests for historically broken words.

Examples of regressions to preserve include:

- verbal forms beginning with `n`;
- noun `m` prefix handling;
- empty morphology rejection;
- radical/final-vowel distinction.

---

# 22. COPYRIGHT DISCIPLINE

The PDF must remain local/private.

Ensure `.gitignore` excludes it.

Create a file such as:

`references/README.md`

explaining:

- which external references the project can optionally use;
- how local references should be stored;
- that copyrighted references are not distributed;
- that repository linguistic rules are derived factual descriptions and synthetic examples.

Do not include long quotations.

Do not commit scanned pages or extracted full text.

Do not create a local full-book text dump in tracked files.

---

# 23. SOURCE PROVENANCE

Rules should carry provenance without reproducing source content.

Example:

source:
    type: book
    author: Joan Russell
    year: 1996
    section: Unit 2 — N-class morphology

Do not include extensive quoted material.

This enables:

source
→ rule
→ implementation
→ test

traceability.

---

# 24. DO NOT BREAK THE REST OF THE PROJECT

This session focuses on the linguistic layer.

However, every linguistic change must preserve:

- FastAPI;
- persistence;
- acquisition;
- exports;
- Streamlit where applicable;
- existing tests.

Run the full test suite periodically.

Do not work only against isolated linguistic unit tests.

---

# 25. QUALITY CLEANUP

While working on files you touch:

- migrate naive UTC timestamps where relevant;
- fix clear Ruff issues;
- improve typing;
- modernize Pydantic patterns;
- improve docstrings.

Do NOT start a repository-wide style rewrite.

Do not spend hours eliminating unrelated mypy errors.

---

# 26. GIT

Continue using the existing local Git repository.

Before starting major modifications:

run:

`git status`

Ensure no unexplained uncommitted state exists.

Create coherent commits throughout the session.

Suggested examples:

docs: add linguistic reference harness

test: add curated swahili morphology benchmark

refactor: formalize noun class agreement rules

feat: improve verbal morphology analysis

test: expand linguistic regression coverage

docs: document computational morphology model

These are examples only.

Use actual work to determine commit boundaries.

Do NOT push to GitHub yet.

Do NOT force push.

---

# 27. SECOND-PASS LINGUISTIC REVIEW

After implementation, perform a fresh adversarial review.

Pretend you are a computational linguist reviewing the analyzer.

Look specifically for:

- English-centric assumptions;
- prefix stripping masquerading as morphology;
- confusion between root/stem/lemma;
- incorrect noun class inference;
- animate agreement exceptions;
- irregular verbs;
- incorrect final-vowel treatment;
- overconfident analysis;
- undocumented heuristics;
- tests that merely mirror implementation;
- rules with no source provenance;
- source rules with no implementation/tests.

Fix high-value findings.

---

# 28. THIRD-PASS SOFTWARE REVIEW

Then review the integration as a software engineer.

Look for:

- duplicated linguistic tables;
- circular imports;
- domain/application leakage;
- poor API schemas;
- test brittleness;
- bad names;
- unnecessary abstractions;
- large hard-coded conditional chains;
- accidental dependence on the PDF at runtime.

CRITICAL:

The production API must NOT require the Russell PDF at runtime.

The manual is a development/reference harness.

The final program must function without the PDF installed.

---

# 29. VALIDATION

Before finishing, run all applicable:

- pytest;
- branch-aware coverage;
- Ruff;
- formatter check;
- mypy or targeted typing checks;
- import smoke tests;
- API smoke tests;
- persistence tests;
- acquisition tests;
- linguistic benchmark tests.

Report actual results.

Never invent a score.

---

# 30. LINGUISTIC COMPLETION REPORT

Create:

`docs/linguistics/LINGUISTIC_HARNESS_REPORT.md`

It must contain:

## Source used

## Scope reviewed

## Rules formalized

## Noun-class improvements

## Agreement improvements

## Verbal morphology improvements

## Derivational morphology status

## Locative morphology status

## Test harness

## Evaluation results

## Conflicts between project specification and source

## Known ambiguities

## Unsupported structures

## Future linguistic work

## Copyright/provenance handling

---

# 31. FINAL PROJECT-LAYER ASSESSMENT

THIS IS REQUIRED.

At the end of the entire session, create:

`docs/PROJECT_LAYER_STATUS.md`

This document must assess the CURRENT REAL STATE of every major layer of the project.

Do not describe plans as implemented features.

Use this structure.

# Project Layer Status

## 1. Linguistic Layer

Assess:

- noun classes;
- agreement;
- morphology;
- verbal analysis;
- roots/stems;
- derivation;
- locatives;
- lexical model;
- rule provenance;
- linguistic test coverage;
- remaining linguistic weaknesses.

Give status:

MATURE
FUNCTIONAL
PARTIAL
EXPERIMENTAL
MISSING

Explain why.

---

## 2. Domain Layer

Assess:

- entities;
- value objects;
- Lexeme;
- WordForm;
- Meaning;
- Context;
- Derivation;
- SwahiliTerm legacy compatibility;
- invariants;
- coupling.

State architectural debt.

---

## 3. Application Layer

Assess:

- services;
- use cases;
- orchestration;
- batch processing;
- ingestion;
- export functionality;
- error handling.

---

## 4. Persistence / Database Layer

Assess:

- SQLAlchemy;
- repository contracts;
- SQLite;
- migrations;
- session lifecycle;
- lexeme-first vs term-first mismatch;
- test coverage;
- SQLAlchemy 2 modernization status.

---

## 5. Backend / API Layer

Assess:

- FastAPI;
- endpoint quality;
- schemas;
- error handling;
- dependency injection;
- API organization;
- route tests;
- current oversized `api.py` situation if still present.

List actual supported API capabilities.

---

## 6. Web Acquisition Layer

Assess:

- safe HTTP fetching;
- SSRF protections;
- redirects;
- HTML restrictions;
- size limits;
- page inspector;
- semantic HTML;
- JSON-LD;
- OpenGraph;
- RSS/sitemap hints;
- extraction quality;
- remaining limitations.

Clearly distinguish:

implemented acquisition

from:

future crawler.

---

## 7. Corpus / Data Engineering Layer

Assess:

- raw data;
- processed data;
- manifests;
- ingestion scripts;
- provenance;
- deduplication;
- language validation;
- storage;
- reproducibility.

Explain what is still missing for a real Swahili web corpus pipeline.

---

## 8. NLP / Analysis Layer

Assess:

- text processing;
- morphology;
- sentiment baseline;
- keyword extraction;
- linguistic features;
- batch analysis;
- research exports.

Do not call lexicon sentiment AI unless appropriate.

---

## 9. Testing / Evaluation Layer

Report:

- total tests;
- passed;
- failed;
- skipped;
- branch-aware coverage;
- linguistic benchmark size;
- API tests;
- DB tests;
- acquisition tests;
- remaining weak areas.

Use only measured values.

---

## 10. Security Layer

Assess:

- secrets;
- URL fetching;
- SSRF;
- file handling;
- dependency exposure;
- local data;
- public-repository readiness.

---

## 11. Developer Experience / Tooling

Assess:

- pyproject.toml;
- dependency groups;
- Makefile;
- lint;
- formatter;
- typing;
- warnings;
- setup;
- reproducibility.

Report remaining Ruff and mypy issues honestly.

---

## 12. Documentation Layer

Assess:

- README;
- architecture;
- linguistic specification;
- acquisition roadmap;
- worklog;
- reference documentation;
- API documentation.

---

## 13. Dashboard / Interface Layer

Assess Streamlit or other interfaces.

State whether it is:

FUNCTIONAL
PARTIAL
LEGACY
EXPERIMENTAL

and why.

---

## 14. Research Readiness

Evaluate whether the project is ready for:

- portfolio demonstration;
- undergraduate research;
- TCC experimentation;
- linguistic corpus experiments;
- reproducible computational-linguistics evaluation.

Do not exaggerate.

---

## 15. Production Readiness

Evaluate separately.

Do NOT equate:

portfolio-ready

with:

production-ready.

List what would still be required for real production deployment.

---

# 32. LAYER SCORECARD

At the beginning or end of `PROJECT_LAYER_STATUS.md`, create a compact scorecard:

| Layer | Status | Confidence | Main Strength | Main Gap |
|---|---|---:|---|---|

Use status values:

MATURE
FUNCTIONAL
PARTIAL
EXPERIMENTAL
MISSING

Confidence should describe confidence in the assessment, not arbitrary software quality percentages.

---

# 33. ARCHITECTURE OVERVIEW

At the end of `PROJECT_LAYER_STATUS.md`, generate a Mermaid diagram showing the REAL current architecture.

Something conceptually similar to:

Web Sources
    ↓
Acquisition
    ↓
Corpus/Data
    ↓
Linguistic/NLP
    ↓
Application
    ↓
API
    ↓
Consumers

with:

Domain
Persistence
Testing

represented appropriately.

Do not draw components that do not exist.

---

# 34. PRIORITIZED NEXT STEPS

Finish `PROJECT_LAYER_STATUS.md` with:

## Recommended Next 10 Tasks

Rank exactly ten tasks.

Each must include:

Priority:
P0 / P1 / P2

Layer:
...

Why:
...

Expected impact:
...

Avoid generic tasks such as:

"improve code quality"

Be specific.

---

# 35. FINAL SESSION REPORT

Create:

`docs/LINGUISTIC_SESSION_REPORT.md`

Include:

- starting state;
- PDF/reference integration;
- rules discovered;
- implementation changes;
- tests added;
- bugs found;
- linguistic conflicts;
- coverage change;
- final tests;
- Git commits;
- project layer assessment summary;
- recommended next major milestone.

---

# 36. DEFINITION OF DONE

This session is complete only when:

- the Russell PDF is integrated as a local/private reference;
- it is protected from Git publication;
- its relevant grammatical structure has been indexed;
- key rules have been mapped to the project;
- linguistic terminology is formalized;
- high-value noun-class rules are tested;
- high-value verbal morphology rules are tested;
- regressions remain fixed;
- production code does not depend on the PDF;
- copyright-sensitive content is not copied;
- the complete test suite is run;
- actual coverage is reported;
- local commits are created;
- `LINGUISTIC_HARNESS_REPORT.md` exists;
- `PROJECT_LAYER_STATUS.md` exists;
- `LINGUISTIC_SESSION_REPORT.md` exists.

---

# 37. AUTONOMY

Do not stop after creating documents.

Implement high-value findings.

When one task finishes:

1. update WORKLOG;
2. run relevant tests;
3. review results;
4. fix regressions;
5. commit coherent work;
6. select next P0/P1 task;
7. continue.

If linguistic P0/P1 work finishes early:

improve the linguistic evaluation harness.

Do NOT immediately build Playwright or a large crawler in this session.

The linguistic foundation has priority.

---

# 38. FINAL TERMINAL OUTPUT

When the session is finished, print:

- total tests;
- passed;
- failed;
- skipped;
- branch-aware coverage;
- number of linguistic rules indexed;
- number of curated linguistic cases;
- Ruff status;
- mypy status;
- Git commits created;
- git status;
- major linguistic improvements;
- highest-priority remaining task;
- overall status of each major project layer.

Begin now.

Do not merely produce a plan.

Inspect the repository and the local Russell reference and start executing.