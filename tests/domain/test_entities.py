"""
Unit Tests - Domain Layer: Entities

Tests for the lexeme-first domain entities introduced during the domain
refactor while keeping legacy compatibility.
"""
import pytest

from src.domain.entities import (
    Context,
    Derivation,
    Lexeme,
    Meaning,
    SwahiliTerm,
    WordForm,
)
from src.domain.value_objects import BantuClass, Etymology, MorphologicalRoot, WordType


class TestLexemeModel:
    """Tests for the new lexeme-centered domain model."""

    def test_lexeme_accepts_multiple_word_forms(self):
        """A lexeme can own multiple concrete realizations."""
        lexeme = Lexeme(lemma="soma", word_type=WordType.VERB)

        lexeme.add_word_form(
            WordForm(
                lexeme_lemma="soma",
                form="soma",
                word_type=WordType.VERB,
                is_canonical=True,
            )
        )
        lexeme.add_word_form(
            WordForm(
                lexeme_lemma="soma",
                form="ninasoma",
                root=MorphologicalRoot(root="som", prefix="nina", suffix="a"),
                word_type=WordType.VERB,
            )
        )

        assert len(lexeme.word_forms) == 2
        assert lexeme.canonical_form is not None
        assert lexeme.canonical_form.form == "soma"

    def test_meaning_belongs_to_lexeme(self):
        """Meanings are attached to the abstract lexeme."""
        lexeme = Lexeme(lemma="mtu", word_type=WordType.NOUN)
        meaning = Meaning(
            lexeme_lemma="mtu",
            gloss="person",
            english_translation="person",
            definition="A human being.",
        )

        lexeme.add_meaning(meaning)

        assert lexeme.has_meanings is True
        assert lexeme.primary_meaning == meaning

    def test_context_references_lexical_data(self):
        """Context links attested usage back to the lexeme and word form."""
        lexeme = Lexeme(lemma="soma", word_type=WordType.VERB)
        lexeme.add_word_form(
            WordForm(
                lexeme_lemma="soma",
                form="ninasoma",
                word_type=WordType.VERB,
            )
        )

        context = Context(
            text="Ninasoma kitabu kila siku.",
            english_translation="I read a book every day.",
            lexeme_lemma="soma",
            word_form="ninasoma",
            source="example-corpus",
        )

        lexeme.add_context(context)

        assert len(lexeme.contexts) == 1
        assert lexeme.contexts[0].references_specific_form is True

    def test_word_form_can_store_structured_morphology(self):
        """Word forms should expose structured Swahili verbal morphology."""
        word_form = WordForm(
            lexeme_lemma="penda",
            form="ninakupenda",
            word_type=WordType.VERB,
            verb_components={
                "subject_marker": "ni",
                "tense_marker": "na",
                "object_marker": "ku",
                "root": "pend",
                "final_vowel": "a",
                "suffixes_extensions": ["a"],
                "full_prefix": "ninaku",
            },
        )

        assert word_form.subject_marker == "ni"
        assert word_form.tense_marker == "na"
        assert word_form.object_marker == "ku"
        assert word_form.root is not None
        assert word_form.root.root == "pend"
        assert word_form.suffixes_extensions == ["a"]
        assert word_form.final_vowel == "a"
        assert word_form.polarity == "affirmative"
        assert word_form.has_structured_morphology is True

    def test_context_rejects_unknown_word_form_when_forms_exist(self):
        """Context should not point to a form the lexeme does not own."""
        lexeme = Lexeme(lemma="soma", word_type=WordType.VERB)
        lexeme.add_word_form(
            WordForm(
                lexeme_lemma="soma",
                form="soma",
                word_type=WordType.VERB,
                is_canonical=True,
            )
        )

        with pytest.raises(ValueError, match="unknown word form"):
            lexeme.add_context(
                Context(
                    text="Wanasoma sasa.",
                    lexeme_lemma="soma",
                    word_form="wanasoma",
                )
            )

    def test_derivation_models_lexeme_relation(self):
        """Derivations are directed relations between lexemes."""
        lexeme = Lexeme(lemma="andika", word_type=WordType.VERB)
        derivation = Derivation(
            source_lexeme="andika",
            target_lexeme="andikisha",
            process="causative",
        )

        lexeme.add_derivation(derivation)

        assert len(lexeme.derivations) == 1
        assert lexeme.derivations[0].process == "causative"


class TestLegacyCompatibility:
    """Tests for the temporary SwahiliTerm compatibility layer."""

    def test_swahili_term_can_be_projected_to_lexeme(self):
        """Legacy term objects can be adapted to the new model."""
        term = SwahiliTerm(
            term="mtu",
            root=MorphologicalRoot(root="tu", prefix="m"),
            noun_class=BantuClass.M_WA,
            etymology=Etymology.BANTU,
            word_type=WordType.NOUN,
        )

        lexeme = term.to_lexeme()

        assert lexeme.lemma == "mtu"
        assert lexeme.noun_class == BantuClass.M_WA
        assert lexeme.etymology == Etymology.BANTU
        assert len(lexeme.word_forms) == 1
        assert lexeme.word_forms[0].is_canonical is True
