# Russell Linguistic Rule Index

Source: Joan Russell, *Swahili* (Teach Yourself Books, 1996). References are
section-level pointers, not quotations. Examples below are synthetic or minimal.
The current project specification retains precedence over this reference.

| Rule ID | Topic and formalized fact | Source section | Project mapping | Status / tests |
|---|---|---|---|---|
| SW-RUSSELL-NOUN-001 | M/WA nouns generally contrast singular `m-/mw-` with plural `wa-`. | Unit 1, noun prefixes | classifier, noun extraction | IMPLEMENTED; existing `mtu/watu` tests |
| SW-RUSSELL-NOUN-002 | N-class singular and plural surface forms are generally identical; nasal realization varies by stem onset and many loans have no overt prefix. | Unit 2, N class | classifier | PARTIAL; lexical/prefix heuristic only |
| SW-RUSSELL-NOUN-003 | KI/VI commonly contrasts `ki-/ch-` with `vi-/vy-`. | Unit 3; Appendix | classifier | IMPLEMENTED; `test_agreement.py` |
| SW-RUSSELL-NOUN-004 | JI/MA commonly contrasts `ji-/j-/zero` with `ma-`. | Unit 4; Appendix | classifier | PARTIAL; zero-prefix membership is ambiguous |
| SW-RUSSELL-NOUN-005 | M/MI commonly contrasts `m-/mw-` with `mi-`. | Unit 5; Appendix | classifier | PARTIAL; prefix ambiguity remains |
| SW-RUSSELL-NOUN-006 | U nouns have heterogeneous plural behavior, including N-class plurals. | Unit 6; Appendix | `BantuClass.U` | PARTIAL |
| SW-RUSSELL-NOUN-007 | Loan-word behavior cannot be inferred from an overt noun prefix alone. | Units 2, 6 | classifier | MISSING lexical evidence |
| SW-RUSSELL-AGR-001 | Class membership and agreement are distinct; each class/number controls several concord series. | Units 1–7; Appendix agreement summaries | `AgreementService` | IMPLEMENTED; `test_agreement.py` |
| SW-RUSSELL-AGR-002 | Human/animate referents may use M/WA agreement even when noun morphology belongs elsewhere. | Unit 6, animate nouns | animate override | IMPLEMENTED as explicit lookup; no automatic semantic detection |
| SW-RUSSELL-AGR-003 | Agreement series include subject, adjective, possessive, demonstrative, numeral, and relative concord. | Appendix | typed paradigm | IMPLEMENTED underlying markers; surface realization PARTIAL |
| SW-RUSSELL-VERB-001 | A finite verb can contain subject concord, tense/aspect, object concord, radical/stem material, and final vowel. | Unit 1 onward; Appendix | `VerbComponents` | IMPLEMENTED heuristic |
| SW-RUSSELL-VERB-002 | Person subject concords include `ni-, u-, a-, tu-, m-, wa-`. | Unit 1 | parser | IMPLEMENTED; existing tests |
| SW-RUSSELL-VERB-003 | Present, past and future affirmative markers include `-na-, -li-, -ta-`. | Units 1–3 | parser | IMPLEMENTED; parameterized tests |
| SW-RUSSELL-NEG-001 | Negative subject concords are person-specific and replace affirmative subject concords. | Units 2, 4, 5 | parser | IMPLEMENTED; `test_verbal_harness.py` |
| SW-RUSSELL-NEG-002 | Regular negative present has no affirmative tense marker and commonly changes final `-a` to `-i`. | Unit 4; Appendix | parser, lemma inference | IMPLEMENTED for regular Bantu-origin verbs |
| SW-RUSSELL-NEG-003 | Negative past uses a negative concord plus `-ku-`; negative future uses negative concord plus `-ta-`. | Units 4–5 | parser | IMPLEMENTED; parameterized tests |
| SW-RUSSELL-VERB-004 | Monosyllabic verbs retain infinitival `ku-` in specified affirmative environments. | Units 3, 7; Appendix | parser exception category | PARTIAL; regression for `walikunywa` |
| SW-RUSSELL-VERB-005 | Foreign-origin verbs may retain non-`a` final vowels and differ in negative/passive realization. | Units 4, 11 | final-vowel model | PARTIAL; final vowels retained, class not identified |
| SW-RUSSELL-LOC-001 | `-ko, -po, -mo` distinguish broad/general, specific, and interior location, with contextual limits. | Units 7, 15 | roadmap | FUTURE; current suffix list is not semantic analysis |
| SW-RUSSELL-DERIV-001 | Applicative, passive, stative, reciprocal and causative extensions attach between radical and final vowel. | Units 4, 10–16; Appendix | `suffixes_extensions`, `Derivation` | PARTIAL model, MISSING reliable parser |
| SW-RUSSELL-REL-001 | Relative concord depends on noun class and occupies defined positions in several constructions. | Units 7–18; Appendix | agreement paradigm | PARTIAL concord inventory only |

## LINGUISTIC_CONFLICT

No direct contradiction requiring a semantic contract change was found. The
project specification calls the consonantal element in `som-a` a `root`, while
the manual often teaches a dictionary "stem" including the final vowel. This is
a terminology difference: the project intentionally stores radical-like `som`
and final vowel `a` separately. Recommendation: preserve the frozen fields and
describe the mapping explicitly rather than relabeling stored data.
