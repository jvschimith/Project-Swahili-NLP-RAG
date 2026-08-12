"""Synthetic verbal cases traceable to the Russell reference index."""

import pytest

from src.domain.services.linguistic_analysis import LinguisticAnalysisService
from src.domain.services.root_extractor import RootExtractorService


@pytest.mark.parametrize(
    ("surface", "subject", "tense", "root", "final", "lemma"),
    [
        ("sisomi", "si", None, "som", "i", "kusoma"),
        ("hatusomi", "hatu", None, "som", "i", "kusoma"),
        ("sikupenda", "si", "ku", "pend", "a", "kupenda"),
        ("hawakupenda", "hawa", "ku", "pend", "a", "kupenda"),
        ("sitapenda", "si", "ta", "pend", "a", "kupenda"),
        ("hamtapenda", "ham", "ta", "pend", "a", "kupenda"),
    ],
)
def test_negative_person_tense_and_final_vowel(surface, subject, tense, root, final, lemma):
    result = LinguisticAnalysisService().analyze_word(surface)
    components = result.word_form.verb_components
    assert components is not None
    assert components.subject_marker == subject
    assert components.tense_marker == tense
    assert components.root == root
    assert components.final_vowel == final
    assert components.polarity == "negative"
    assert result.lexeme.lemma == lemma


def test_retained_ku_on_monosyllabic_verb_is_not_an_object_marker():
    components = RootExtractorService.extract_verb_components("walikunywa")
    assert components.subject_marker == "wa"
    assert components.tense_marker == "li"
    assert components.object_marker is None
    assert components.full_prefix == "waliku"
    assert components.root == "nyw"
    assert components.final_vowel == "a"


def test_habitual_hu_is_not_mislabeled_as_negative_second_person():
    components = RootExtractorService.extract_verb_components("hupenda")
    assert components.subject_marker is None
    assert components.polarity == "affirmative"
