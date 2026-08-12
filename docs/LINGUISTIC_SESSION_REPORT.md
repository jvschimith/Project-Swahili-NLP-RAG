# Linguistic Session Report

## Starting state

The repository began clean except for the user-provided untracked harness and
Russell PDF. Baseline measurement was 129 collected, 128 passed, 1 skipped and
65% branch-aware coverage.

## Reference integration and rules

The 333-page Russell (1996) PDF was inspected selectively as a development
reference. PDF patterns are now ignored and runtime code has no reference-file
dependency. Twenty-one concise rules were indexed with section provenance. No
substantial source text, dialogue, exercise, table or vocabulary list was added.

## Implementation changes and bugs found

- Introduced typed agreement paradigms separate from noun-class inference.
- Added explicit human/animate agreement override without rewriting membership.
- Parsed fused negative subject concords, negative past `ku`, negative future
  `ta`, and regular negative-present final `i` while reconstructing lemma `-a`.
- Prevented retained `ku` in the monosyllabic form `walikunywa` from being
  mislabeled as an object marker.
- Preserved the frozen root/final-vowel and Lexeme/WordForm contracts.

No project-specification conflict required semantic change. The source's
pedagogical "stem" and the project's radical-like `root` differ terminologically;
that mapping is documented.

## Tests and coverage

Fourteen curated synthetic cases were added. Final full result: **143 collected,
142 passed, 0 failed, 1 skipped**, with **65% branch-aware coverage** (2,604
statements, 827 missed; 588 branches, 92 partial). Coverage held steady while the
new agreement module reached 100% and root extraction rose from 77% to 80%.

Black, isort and mypy pass. Ruff passes for the new agreement and harness files;
repository-wide Ruff still reports 156 pre-existing issues. Import/API smoke
checks pass. The suite emitted 154 known naive-UTC/Pydantic/SQLAlchemy warnings.

## Reviews

The linguistic review found continued risks from prefix stripping, loan words,
zero prefixes, unmodeled morphophonemics, incomplete monosyllabic paradigms and
uncalibrated certainty. The software review confirmed one centralized agreement
table, no circular dependency, no runtime PDF dependency and backward-compatible
models. The new parser remains heuristic and does not claim full negation,
derivation, relative or locative coverage.

## Commits

Local commits created during this session are listed in the final terminal
summary after commit creation. Nothing was pushed.

## Project assessment and next milestone

The linguistic/domain/API foundations are functional research-alpha components;
persistence, corpus engineering, NLP breadth, security and tooling remain
partial or experimental. The next major milestone should be ambiguity-aware noun
classification backed by a small independently reviewed gold evaluation set,
followed by additive lexeme-first persistence.
