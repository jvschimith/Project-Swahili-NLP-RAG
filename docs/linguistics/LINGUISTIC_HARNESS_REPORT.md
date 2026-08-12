# Linguistic Harness Report

## Source used

Joan Russell, *Swahili*, Teach Yourself Books, 1996, local 333-page PDF. It is a
private development reference and is neither committed nor required at runtime.

## Scope reviewed

The contents, introductory pronunciation discussion, progressive noun-class
sections, agreement summaries, negation, monosyllabic verbs, verbal extensions,
relatives, and locatives were inspected selectively. Dialogues, exercises, and
vocabulary lists were not mined.

## Rules formalized

Twenty-one source-index entries cover noun membership, concord, core verbal
slots, negation, monosyllabic verbs, locatives, relatives, and derivation.

## Noun-class and agreement improvements

The implementation now separates prefix-based class inference from typed
agreement paradigms. M/WA, M/MI, JI/MA, KI/VI, N and U have underlying subject,
adjective, possessive, demonstrative, numeral and relative markers. An explicit
animate override prevents semantic agreement from being confused with lexical
class membership. Automatic animacy and surface concord realization are not
claimed.

## Verbal morphology improvements

The parser recognizes six person-specific negative concords, negative past
`-ku-`, negative future `-ta-`, and zero-marked negative present with final-vowel
alternation for regular Bantu-origin verbs. Retained `ku-` in `walikunywa` is no
longer mislabeled as an object marker. Radical and final vowel stay separate.

## Derivational and locative morphology status

Both remain partial. The domain has `Derivation` and a lightweight extension
list, but no reliable ordered extension parser. `ko/po/mo` occur in legacy suffix
data but are not yet assigned defensible locative semantics.

## Test harness and evaluation results

Fourteen synthetic/parameterized cases were added across agreement and verbal
morphology. Focused validation: 42 passed. See the session report for the final
full-suite and coverage measurement.

## Conflicts between project specification and source

No substantive conflict was found. A root/stem terminology difference is
recorded in the rule index; the current project contract remains authoritative.

## Known ambiguities and unsupported structures

Prefix-only noun inference cannot resolve zero-prefix JI/MA nouns, many loans,
homographs, or all M/WA versus M/MI cases. Negative foreign-origin verbs,
relative constructions, ordered derivational extensions, automatic animate
detection, concord morphophonemics, imperative morphology, and locative
semantics remain unsupported or partial.

## Copyright/provenance handling

PDF patterns are ignored. The tracked index contains section provenance,
concise factual descriptions, and independent examples only. No full-book text,
page scans, tables, dialogues, exercises, or vocabulary corpus is tracked.
