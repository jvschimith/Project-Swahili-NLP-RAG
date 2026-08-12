"""Curated agreement checks derived from SW-RUSSELL-AGR rules."""

import pytest

from src.domain.services.agreement import AgreementService
from src.domain.value_objects import BantuClass


@pytest.mark.parametrize(
    ("noun_class", "singular_subject", "plural_subject", "singular_possessive"),
    [
        (BantuClass.M_WA, "a", "wa", "w"),
        (BantuClass.M_MI, "u", "i", "w"),
        (BantuClass.JI_MA, "li", "ya", "l"),
        (BantuClass.KI_VI, "ki", "vi", "ch"),
        (BantuClass.N_N, "i", "zi", "y"),
    ],
)
def test_noun_membership_maps_to_distinct_agreement_paradigm(
    noun_class, singular_subject, plural_subject, singular_possessive
):
    paradigm = AgreementService.for_class(noun_class)
    assert paradigm is not None
    assert paradigm.singular.subject == singular_subject
    assert paradigm.plural.subject == plural_subject
    assert paradigm.singular.possessive == singular_possessive


def test_animate_agreement_can_differ_from_morphological_membership():
    membership = AgreementService.for_class(BantuClass.N_N)
    animate = AgreementService.for_animate(plural=False)
    assert membership is not None
    assert membership.singular.subject == "i"
    assert animate.subject == "a"
