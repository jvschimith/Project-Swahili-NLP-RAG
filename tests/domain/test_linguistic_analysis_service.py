"""
Unit Tests - Domain Layer: Linguistic Analysis Service
"""

import pytest

from src.domain.services.linguistic_analysis import LinguisticAnalysisService
from src.domain.value_objects import BantuClass, WordType


class TestLinguisticAnalysisService:
    """Tests for lexeme-first single-word linguistic analysis."""

    @pytest.mark.parametrize(
        (
            "word",
            "expected_word_type",
            "expected_lemma",
            "expected_noun_class",
            "expected_root_text",
            "expected_prefix",
            "expected_suffix",
            "expected_subject_marker",
            "expected_tense_marker",
            "expected_object_marker",
            "expected_final_vowel",
            "expected_polarity",
            "expected_is_canonical",
        ),
        [
            (
                "mtu",
                WordType.NOUN,
                "mtu",
                BantuClass.M_WA,
                "tu",
                "m",
                None,
                None,
                None,
                None,
                None,
                None,
                True,
            ),
            (
                "watu",
                WordType.NOUN,
                "watu",
                BantuClass.M_WA,
                "tu",
                "wa",
                None,
                None,
                None,
                None,
                None,
                None,
                True,
            ),
            (
                "soma",
                WordType.VERB,
                "kusoma",
                BantuClass.UNKNOWN,
                "som",
                None,
                "a",
                None,
                None,
                None,
                "a",
                "affirmative",
                False,
            ),
            (
                "ninasoma",
                WordType.VERB,
                "kusoma",
                BantuClass.UNKNOWN,
                "som",
                "nina",
                "a",
                "ni",
                "na",
                None,
                "a",
                "affirmative",
                False,
            ),
            (
                "ninakupenda",
                WordType.VERB,
                "kupenda",
                BantuClass.UNKNOWN,
                "pend",
                "ninaku",
                "a",
                "ni",
                "na",
                "ku",
                "a",
                "affirmative",
                False,
            ),
        ],
    )
    def test_frozen_release_one_analysis_contract(
        self,
        word,
        expected_word_type,
        expected_lemma,
        expected_noun_class,
        expected_root_text,
        expected_prefix,
        expected_suffix,
        expected_subject_marker,
        expected_tense_marker,
        expected_object_marker,
        expected_final_vowel,
        expected_polarity,
        expected_is_canonical,
    ):
        """
        Release 1 frozen linguistic contract for the five required forms.

        This test intentionally locks the current alpha behavior for:
        - inferred word type
        - inferred lemma
        - structured morphology
        - noun class where applicable
        - Lexeme / WordForm consistency
        """
        service = LinguisticAnalysisService()
        result = service.analyze_word(word)

        assert result.word_form.form == word
        assert result.word_form.word_type == expected_word_type
        assert result.word_form.lexeme_lemma == expected_lemma
        assert result.word_form.is_canonical is expected_is_canonical

        assert result.word_form.root is not None
        assert result.word_form.root.root == expected_root_text
        assert result.word_form.root.prefix == expected_prefix
        assert result.word_form.root.suffix == expected_suffix

        assert result.lexeme.lemma == expected_lemma
        assert result.lexeme.word_type == expected_word_type
        assert result.lexeme.noun_class == expected_noun_class
        assert result.lexeme.root is not None
        assert result.lexeme.has_word_forms is True
        assert len(result.lexeme.word_forms) == 1

        attached_form = result.lexeme.word_forms[0]
        assert attached_form.form == result.word_form.form
        assert attached_form.lexeme_lemma == result.lexeme.lemma
        assert attached_form.word_type == result.word_form.word_type
        assert result.lexeme.canonical_form is None or (
            result.lexeme.canonical_form.lexeme_lemma == result.lexeme.lemma
        )

        if expected_word_type == WordType.NOUN:
            assert result.word_form.verb_components is None
            assert result.word_form.subject_marker is None
            assert result.word_form.tense_marker is None
            assert result.word_form.object_marker is None
            assert result.word_form.final_vowel is None
            assert result.word_form.polarity is None
            assert result.word_form.suffixes_extensions == []
            assert result.lexeme.root.root == expected_root_text
        else:
            assert result.word_form.verb_components is not None
            assert result.word_form.subject_marker == expected_subject_marker
            assert result.word_form.tense_marker == expected_tense_marker
            assert result.word_form.object_marker == expected_object_marker
            assert result.word_form.final_vowel == expected_final_vowel
            assert result.word_form.polarity == expected_polarity
            assert result.word_form.suffixes_extensions == ["a"]
            assert result.word_form.verb_components.root == expected_root_text
            assert result.word_form.verb_components.final_vowel == expected_final_vowel
            assert result.word_form.verb_components.polarity == expected_polarity
            assert result.lexeme.root.root == expected_root_text

    def test_conjugated_verbs_preserve_full_prefix_information(self):
        """Structured morphology should keep the full verbal prefix chain."""
        service = LinguisticAnalysisService()

        ninasoma = service.analyze_word("ninasoma")
        ninakupenda = service.analyze_word("ninakupenda")

        assert ninasoma.word_form.verb_components is not None
        assert ninasoma.word_form.verb_components.full_prefix == "nina"
        assert ninasoma.word_form.verb_components.to_dict()["tense"] == "na"

        assert ninakupenda.word_form.verb_components is not None
        assert ninakupenda.word_form.verb_components.full_prefix == "ninaku"
        assert ninakupenda.word_form.verb_components.to_dict()["object"] == "ku"

    def test_release_one_lexeme_word_form_alignment_is_strict(self):
        """Analyzed forms should always attach to the matching lexeme lemma."""
        service = LinguisticAnalysisService()

        for word in ["mtu", "watu", "soma", "ninasoma", "ninakupenda"]:
            result = service.analyze_word(word)

            assert len(result.lexeme.word_forms) == 1
            word_form = result.lexeme.word_forms[0]

            assert word_form.lexeme_lemma == result.lexeme.lemma
            assert word_form.form == result.word_form.form
            assert word_form.word_type == result.lexeme.word_type
            assert word_form.has_structured_morphology == (
                result.lexeme.word_type == WordType.VERB
            )
