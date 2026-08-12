"""Typed noun-class agreement paradigms, separate from class inference."""

from dataclasses import dataclass

from ..value_objects import BantuClass


@dataclass(frozen=True)
class AgreementParadigm:
    """Agreement markers for one grammatical noun-class number."""

    subject: str
    adjective: str
    possessive: str
    demonstrative_proximal: str
    numeral: str
    relative: str


@dataclass(frozen=True)
class NounClassAgreement:
    """Singular/plural agreement pair for a project noun-class grouping."""

    singular: AgreementParadigm
    plural: AgreementParadigm


# Markers are underlying agreement forms. Surface morphophonemic alternations
# (for example m- + -ema -> mwema) belong to a later realization layer.
NOUN_CLASS_AGREEMENT: dict[BantuClass, NounClassAgreement] = {
    BantuClass.M_WA: NounClassAgreement(
        singular=AgreementParadigm("a", "m", "w", "huyu", "m", "ye"),
        plural=AgreementParadigm("wa", "wa", "w", "hawa", "wa", "o"),
    ),
    BantuClass.M_MI: NounClassAgreement(
        singular=AgreementParadigm("u", "m", "w", "huu", "m", "o"),
        plural=AgreementParadigm("i", "mi", "y", "hii", "mi", "yo"),
    ),
    BantuClass.JI_MA: NounClassAgreement(
        singular=AgreementParadigm("li", "ji", "l", "hili", "ji", "lo"),
        plural=AgreementParadigm("ya", "ma", "y", "haya", "ma", "yo"),
    ),
    BantuClass.KI_VI: NounClassAgreement(
        singular=AgreementParadigm("ki", "ki", "ch", "hiki", "ki", "cho"),
        plural=AgreementParadigm("vi", "vi", "vy", "hivi", "vi", "vyo"),
    ),
    BantuClass.N_N: NounClassAgreement(
        singular=AgreementParadigm("i", "N", "y", "hii", "N", "yo"),
        plural=AgreementParadigm("zi", "N", "z", "hizi", "N", "zo"),
    ),
    BantuClass.U: NounClassAgreement(
        singular=AgreementParadigm("u", "m", "w", "huu", "m", "o"),
        plural=AgreementParadigm("zi", "N", "z", "hizi", "N", "zo"),
    ),
}


class AgreementService:
    """Look up agreement without pretending prefix inference proves membership."""

    @staticmethod
    def for_class(noun_class: BantuClass) -> NounClassAgreement | None:
        return NOUN_CLASS_AGREEMENT.get(noun_class)

    @staticmethod
    def for_animate(*, plural: bool) -> AgreementParadigm:
        """Return semantic human/animate agreement independently of membership."""
        paradigm = NOUN_CLASS_AGREEMENT[BantuClass.M_WA]
        return paradigm.plural if plural else paradigm.singular
