# Linguistic Specification

This file freezes the linguistic core of the project as of the current
domain-layer refactor. It is the stable contract for future work in data
engineering, API integration, storage, pipelines, analytics, and
infrastructure.

## Core Entities

- `Lexeme`: abstract semantic unit and lexical anchor.
- `WordForm`: concrete surface realization of a lexeme.
- `Meaning`: lexeme-owned semantic content.
- `Context`: attested usage linked to a lexeme and optionally a specific word form.
- `Derivation`: directed relation between lexemes.
- `VerbComponents`: structured verbal morphology used during analysis.
- `SwahiliTerm`: legacy compatibility model only. It is not the linguistic core.

## Lexeme-First Contract

- The linguistic core is lexeme-first, not term-first.
- A `Lexeme` may own multiple `WordForm` objects.
- `Meaning` belongs to `Lexeme`, not to `WordForm`.
- `Context` stores attested usage and references lexical data explicitly.
- `Derivation` models relations between lexemes, not between raw strings alone.

## Morphology Fields

Structured morphology is standardized around `WordForm` and `VerbComponents`.

Supported fields:

- `subject_marker`
- `tense_marker`
- `object_marker`
- `root`
- `suffixes_extensions`
- `final_vowel`
- `polarity`
- `full_prefix`

Compatibility note:

- `WordForm` still retains `grammatical_features` for backward compatibility.
- `MorphologicalRoot` remains available and is still used by existing services.

## Lemma Inference Rules

- Verbs prefer an infinitive-style canonical lemma.
- Current canonical verb behavior is `ku + root + final_vowel` when available.
- If the final vowel is unavailable but the root is available, the fallback is `ku + root`.
- Nouns currently default to the normalized surface form as the canonical lexical form.
- If morphology is weak or uncertain, the safe fallback is the normalized input word.

Examples:

- `mtu` -> lemma `mtu`
- `soma` -> lemma `kusoma`
- `ninasoma` -> lemma `kusoma`
- `ninakupenda` -> lemma `kupenda`

## Grammatical Categories

The frozen core categories that future engineering work may depend on are:

- `NOUN`
- `VERB`
- `ADJECTIVE`
- `ADVERB`
- `UNKNOWN`

Other categories may continue to exist for compatibility, but the core
linguistic contract is defined around the list above.

## Noun Class Handling

Noun-class handling is centralized and treated as a linguistic rule set.

Supported classes:

- `1/2`
- `3/4`
- `5/6`
- `7/8`
- `9/10`
- `11/14`
- `16/17/18`
- `N/A`

Current implementation behavior:

- noun-class inference applies to nouns and unknown words only
- special lexical cases are checked first
- prefix-based rules are applied next
- if no rule matches, the result is `N/A`

Noun-class membership and agreement are separate computational concerns.
`AgreementService` stores typed underlying concord paradigms and supports an
explicit animate agreement override without changing morphological membership.
Surface morphophonemic realization is not yet implemented.

## Rule Centralization

The stable source of truth for linguistic rules is:

- `src/domain/linguistic_rules.py`

This module centralizes:

- noun-class rule data
- noun-class descriptions and examples
- verbal markers
- polarity inference
- canonical lemma rules
- normalization helpers for linguistic fields

## Known Limitations

- The morphology engine is heuristic, not a full finite-state morphological analyzer.
- Noun lemma normalization does not yet derive singular lexical lemmas from plural forms.
- Derivational suffix analysis is still lightweight and represented as `suffixes_extensions`.
- Polarity is only inferred when verbal morphology exposes it clearly.
- Regular negative present/past/future person forms are recognized heuristically.
- Monosyllabic retained `ku-` has an initial regression rule, not full paradigm coverage.
- The project does not yet model a full paradigm generator in the frozen contract.

## Intentionally Out of Scope

The frozen linguistic layer does not include:

- API route design
- database schema or migrations
- storage layout
- scraping or ingestion infrastructure
- analytics or observability
- LLM-based linguistic inference
- a broad general-purpose NLP framework

## Engineering Expectation

Future work should treat this file as the authoritative linguistic
contract. Changes to the linguistic core should be rare, deliberate, and
backward-compatible whenever reasonably possible.
