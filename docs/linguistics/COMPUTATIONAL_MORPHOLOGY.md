# Computational Morphology Contract

This vocabulary is normative for code and project documentation.

| Term | Project meaning |
|---|---|
| Surface form | The observed orthographic token, such as `ninasoma`. |
| Lexeme | Abstract lexical/semantic anchor shared by its forms. |
| Lemma | Canonical lookup label for a lexeme; verbs currently use an infinitive-style form. |
| Stem | Root/radical plus derivational material and, under some analyses, a final vowel. State the convention when used. |
| Root | The project's stored lexical core. For regular verbs this is currently radical-like and excludes the final vowel. |
| Radical | Irreducible lexical consonantal/core material; `som` in the current `som-a` representation. |
| Prefix / suffix | Bound material before / after a base; these positional terms do not by themselves identify function. |
| Morpheme | Minimal grammatical or lexical unit represented by a marker or base. |
| Inflection | Form change expressing grammar without creating a new lexeme. |
| Derivation | Form change creating a lexically or semantically related lexeme. |
| Final vowel | The final verbal slot, stored separately (`a`, `i`, `e`, or a loan-verb vowel). It is not automatically a derivational suffix. |
| Noun class | Lexical/morphological membership category. It does not alone determine semantic animacy. |
| Agreement marker | Concord selected by controller class/number for a grammatical target. |
| Subject marker | Verbal concord indexing the subject; negative forms may use fused negative subject concords. |
| Object marker | Verbal concord indexing an object; retained infinitival `ku-` is not an object marker. |
| Tense/aspect marker | Marker such as present `na`, past `li`, future `ta`, or perfect `me`. Absence can itself be meaningful. |
| Polarity | Affirmative or negative grammatical value, separate from tense/aspect. |
| Locative marker | Class/concord or verbal relative element expressing location; `ko`, `po`, and `mo` must not be collapsed semantically. |

## Pedagogical-to-computational mapping

Russell deliberately uses limited pedagogical terminology. Her "noun-prefix"
can map to a noun's class prefix or to an adjective/numeral concord depending on
context. Her "verb-prefix" can correspond to a person subject concord or a
noun-class subject concord. Her dictionary "verb stem" generally includes more
material than this project's stored `root`. Therefore source terms are mapped by
function, not copied mechanically into field names.

## Current verbal analysis

The supported heuristic sequence is:

`[subject/polarity] [tense/aspect] [object] [retained ku] ROOT [final vowel]`

`VerbComponents` exposes only evidence the parser can currently identify.
Derivational extensions, relatives, and locatives remain partial. Confidence is
not emitted because no calibrated score exists; callers must treat the output as
heuristic.

## Noun membership versus agreement

`BantuClassifierService` estimates membership from lexical exceptions and
surface prefixes. `AgreementService` separately represents concord paradigms.
The explicit animate override enables human agreement without falsely changing
a noun's morphological class. Surface morphophonemic realization remains future
work; the table stores underlying markers rather than pretending concatenation
always yields the correct word.
