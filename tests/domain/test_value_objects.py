"""
Unit Tests - Domain Layer: Value Objects

Tests for immutable value objects.
"""

import pytest

from src.domain.linguistic_rules import AFFIRMATIVE_POLARITY, NEGATIVE_POLARITY
from src.domain.value_objects import (
    BantuClass,
    EntityType,
    Etymology,
    MorphologicalRoot,
    SentimentScore,
    VerbComponents,
    WordType,
)


class TestBantuClass:
    """Tests for BantuClass enum."""

    def test_bantu_class_values(self):
        """Test all Bantu class values exist."""
        assert BantuClass.M_WA.value == "1/2"
        assert BantuClass.M_MI.value == "3/4"
        assert BantuClass.KI_VI.value == "7/8"
        assert BantuClass.UNKNOWN.value == "N/A"

    def test_bantu_class_description(self):
        """Test Bantu class descriptions."""
        assert "People" in BantuClass.M_WA.description
        assert "Tools" in BantuClass.KI_VI.description
        assert "Unknown" in BantuClass.UNKNOWN.description

    def test_is_identified(self):
        """Test identification check."""
        assert BantuClass.M_WA.is_identified is True
        assert BantuClass.UNKNOWN.is_identified is False


class TestEtymology:
    """Tests for Etymology enum."""

    def test_etymology_values(self):
        """Test etymology values."""
        assert Etymology.BANTU.value == "bantu"
        assert Etymology.ARABIC.value == "arabic"
        assert Etymology.ENGLISH.value == "english"

    def test_is_native(self):
        """Test native origin check."""
        assert Etymology.BANTU.is_native is True
        assert Etymology.ARABIC.is_native is False
        assert Etymology.ENGLISH.is_native is False

    def test_is_loanword(self):
        """Test loanword check."""
        assert Etymology.BANTU.is_loanword is False
        assert Etymology.ARABIC.is_loanword is True
        assert Etymology.ENGLISH.is_loanword is True
        assert Etymology.UNKNOWN.is_loanword is False


class TestWordType:
    """Tests for WordType enum."""

    def test_word_type_values(self):
        """Test word type values."""
        assert WordType.NOUN.value == "noun"
        assert WordType.VERB.value == "verb"
        assert WordType.ADJECTIVE.value == "adjective"

    def test_is_content_word(self):
        """Test content word check."""
        assert WordType.NOUN.is_content_word is True
        assert WordType.VERB.is_content_word is True
        assert WordType.CONJUNCTION.is_content_word is False


class TestSentimentScore:
    """Tests for SentimentScore value object."""

    def test_valid_sentiment_score(self):
        """Test creating valid sentiment score."""
        score = SentimentScore(polarity=0.8, confidence=0.9)
        assert score.polarity == 0.8
        assert score.confidence == 0.9
        assert score.label == "positive"

    def test_invalid_polarity_raises_error(self):
        """Test invalid polarity raises ValueError."""
        with pytest.raises(ValueError, match="Polarity"):
            SentimentScore(polarity=1.5, confidence=0.9)

        with pytest.raises(ValueError, match="Polarity"):
            SentimentScore(polarity=-1.5, confidence=0.9)

    def test_invalid_confidence_raises_error(self):
        """Test invalid confidence raises ValueError."""
        with pytest.raises(ValueError, match="Confidence"):
            SentimentScore(polarity=0.5, confidence=1.5)

    def test_sentiment_labels(self):
        """Test sentiment label calculation."""
        positive = SentimentScore(polarity=0.8, confidence=0.9)
        assert positive.label == "positive"
        assert positive.is_positive is True

        negative = SentimentScore(polarity=-0.8, confidence=0.9)
        assert negative.label == "negative"
        assert negative.is_negative is True

        neutral = SentimentScore(polarity=0.05, confidence=0.9)
        assert neutral.label == "neutral"
        assert neutral.is_neutral is True

    def test_is_confident(self):
        """Test confidence threshold check."""
        high_conf = SentimentScore(polarity=0.8, confidence=0.9)
        assert high_conf.is_confident() is True

        low_conf = SentimentScore(polarity=0.8, confidence=0.5)
        assert low_conf.is_confident() is False

    def test_sentiment_str_representation(self):
        """Test string representation."""
        score = SentimentScore(polarity=0.75, confidence=0.85)
        str_repr = str(score)
        assert "positive" in str_repr
        assert "0.75" in str_repr
        assert "0.85" in str_repr


class TestMorphologicalRoot:
    """Tests for MorphologicalRoot value object."""

    def test_simple_root(self):
        """Test creating simple root."""
        root = MorphologicalRoot(root="soma")
        assert root.root == "soma"
        assert root.prefix is None
        assert root.suffix is None
        assert root.is_simple is True

    def test_root_with_prefix(self):
        """Test root with prefix."""
        root = MorphologicalRoot(root="soma", prefix="wa")
        assert root.root == "soma"
        assert root.prefix == "wa"
        assert root.has_prefix is True
        assert root.is_simple is False

    def test_root_with_suffix(self):
        """Test root with suffix."""
        root = MorphologicalRoot(root="som", suffix="a")
        assert root.root == "som"
        assert root.suffix == "a"
        assert root.has_suffix is True

    def test_full_word_reconstruction(self):
        """Test reconstructing full word."""
        root = MorphologicalRoot(root="som", prefix="wa", suffix="a")
        assert root.full_word == "wasoma"

    def test_empty_root_raises_error(self):
        """Test empty root raises ValueError."""
        with pytest.raises(ValueError, match="Root cannot be empty"):
            MorphologicalRoot(root="")

    def test_root_normalization(self):
        """Test root normalization to lowercase."""
        root = MorphologicalRoot(root="SOMA", prefix="WA")
        assert root.root == "soma"
        assert root.prefix == "wa"

    def test_root_str_representation(self):
        """Test string representation."""
        simple = MorphologicalRoot(root="soma")
        assert str(simple) == "[soma]"

        complex_root = MorphologicalRoot(root="som", prefix="wa", suffix="a")
        assert str(complex_root) == "[wa-som-a]"


class TestEntityType:
    """Tests for EntityType value object."""

    def test_valid_entity_types(self):
        """Test creating valid entity types."""
        person = EntityType(group="PER")
        assert person.group == "PER"
        assert person.is_person is True

        location = EntityType(group="LOC")
        assert location.is_location is True

        org = EntityType(group="ORG")
        assert org.is_organization is True

    def test_entity_with_subtype(self):
        """Test entity with subtype."""
        entity = EntityType(group="PER", subtype="politician")
        assert entity.group == "PER"
        assert entity.subtype == "politician"
        assert str(entity) == "PER:politician"

    def test_invalid_group_raises_error(self):
        """Test invalid group raises ValueError."""
        with pytest.raises(ValueError, match="Invalid entity group"):
            EntityType(group="INVALID")

    def test_group_normalization(self):
        """Test group normalization to uppercase."""
        entity = EntityType(group="per")
        assert entity.group == "PER"


class TestVerbComponents:
    """Tests for structured verbal morphology."""

    def test_verb_components_normalize_values(self):
        """Structured markers should normalize to lowercase."""
        components = VerbComponents(
            subject_marker="NI",
            tense_marker="NA",
            object_marker="KU",
            root="PEND",
            final_vowel="A",
            suffixes_extensions=["A"],
            full_prefix="NIKU",
        )

        assert components.subject_marker == "ni"
        assert components.tense_marker == "na"
        assert components.object_marker == "ku"
        assert components.root == "pend"
        assert components.final_vowel == "a"
        assert components.suffixes_extensions == ["a"]
        assert components.full_prefix == "niku"

    def test_verb_components_support_legacy_dict_access(self):
        """Existing morphology tests and callers can use dict-style access."""
        components = VerbComponents(
            subject_marker="ni",
            tense_marker="na",
            root="som",
            final_vowel="a",
        )

        assert components["subject"] == "ni"
        assert components["tense"] == "na"
        assert components["root"] == "som"
        assert components["final"] == "a"
        assert components["polarity"] == AFFIRMATIVE_POLARITY

    def test_verb_components_infer_negative_polarity(self):
        """Negative tense morphology should surface negative polarity."""
        components = VerbComponents(
            subject_marker="si",
            tense_marker="si",
            root="fany",
            final_vowel="a",
        )

        assert components.polarity == NEGATIVE_POLARITY


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
