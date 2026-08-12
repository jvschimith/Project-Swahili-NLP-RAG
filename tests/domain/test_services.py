"""
Unit Tests - Domain Layer: Domain Services

Tests for BantuClassifier and RootExtractor services.
"""

import pytest

from src.domain.services.bantu_classifier import BantuClassifierService
from src.domain.services.root_extractor import RootExtractorService
from src.domain.value_objects import BantuClass, WordType


class TestBantuClassifierService:
    """Tests for Bantu classification service."""

    def test_classify_m_wa_class(self):
        """Test M-WA class (people) classification."""
        result = BantuClassifierService.infer_class("mtu", WordType.NOUN)
        assert result == BantuClass.M_WA

        result = BantuClassifierService.infer_class("watu", WordType.NOUN)
        assert result == BantuClass.M_WA

    def test_classify_ki_vi_class(self):
        """Test KI-VI class (tools) classification."""
        result = BantuClassifierService.infer_class("kiti", WordType.NOUN)
        assert result == BantuClass.KI_VI

        result = BantuClassifierService.infer_class("viti", WordType.NOUN)
        assert result == BantuClass.KI_VI

    def test_classify_m_mi_class(self):
        """Test M-MI class (plants) classification."""
        result = BantuClassifierService.infer_class("mti", WordType.NOUN)
        assert result == BantuClass.M_MI

        result = BantuClassifierService.infer_class("miti", WordType.NOUN)
        assert result == BantuClass.M_MI

    def test_classify_unknown_word(self):
        """Test unknown word returns UNKNOWN."""
        result = BantuClassifierService.infer_class("xyz", WordType.NOUN)
        assert result == BantuClass.UNKNOWN

    def test_non_noun_returns_unknown(self):
        """Test non-nouns return UNKNOWN."""
        result = BantuClassifierService.infer_class("soma", WordType.VERB)
        assert result == BantuClass.UNKNOWN

        result = BantuClassifierService.infer_class("nzuri", WordType.ADJECTIVE)
        assert result == BantuClass.UNKNOWN

    def test_special_cases(self):
        """Test special case handling."""
        result = BantuClassifierService.infer_class("mtu", WordType.NOUN)
        assert result == BantuClass.M_WA

        result = BantuClassifierService.infer_class("nyumba", WordType.NOUN)
        assert result == BantuClass.N_N

    def test_get_class_description(self):
        """Test getting class description."""
        desc = BantuClassifierService.get_class_description(BantuClass.M_WA)
        assert "People" in desc

        desc = BantuClassifierService.get_class_description(BantuClass.KI_VI)
        assert "Tools" in desc

    def test_get_typical_examples(self):
        """Test getting typical examples."""
        examples = BantuClassifierService.get_typical_examples(BantuClass.M_WA)
        assert len(examples) > 0
        assert any("mtu" in str(ex) for ex in examples)
        assert any("person" in str(ex) for ex in examples)

    def test_validate_class_for_word(self):
        """Test class validation."""
        # Valid classification
        assert (
            BantuClassifierService.validate_class_for_word("mtu", BantuClass.M_WA)
            is True
        )

        # Invalid classification
        assert (
            BantuClassifierService.validate_class_for_word("mtu", BantuClass.KI_VI)
            is False
        )

    def test_get_all_classes(self):
        """Test getting all classes."""
        classes = BantuClassifierService.get_all_classes()
        assert len(classes) == 7  # All non-UNKNOWN classes
        assert BantuClass.M_WA in classes
        assert BantuClass.UNKNOWN not in classes


class TestRootExtractorService:
    """Tests for root extraction service."""

    def test_extract_simple_word(self):
        """Test extracting root from simple word."""
        root = RootExtractorService.extract("soma")
        assert root.root == "soma"
        assert root.prefix is None
        assert root.suffix is None

    def test_extract_word_with_prefix(self):
        """Test extracting root with prefix."""
        root = RootExtractorService.extract("wasoma", WordType.VERB)
        # The analyzer exposes a consonantal stem/root plus the final vowel,
        # matching the frozen morphology contract (som + a).
        assert root.root == "som"
        assert root.suffix == "a"
        assert root.prefix == "wa"

    def test_extract_word_with_prefix_and_suffix(self):
        """Test extracting root with prefix and suffix."""
        root = RootExtractorService.extract("ninasoma", WordType.VERB, aggressive=True)
        assert "som" in root.root
        assert root.prefix is not None

    def test_extract_noun(self):
        """Test extracting noun root."""
        root = RootExtractorService.extract("kitabu", WordType.NOUN)
        assert root.root == "tabu"
        assert root.prefix == "ki"

    def test_extract_preserves_minimum_root(self):
        """Test minimum root length is preserved."""
        root = RootExtractorService.extract("wa", WordType.NOUN)
        # Should not strip everything - needs minimum 2 chars
        assert len(root.root) >= 2 or root.root == "wa"

    def test_extract_verb_components(self):
        """Test extracting verb components."""
        components = RootExtractorService.extract_verb_components("ninasoma")

        assert components["subject"] == "ni"
        assert components["tense"] == "na"
        assert "som" in components["root"]
        assert components["final"] == "a"
        assert components["polarity"] == "affirmative"

    def test_extract_verb_components_complex(self):
        """Test extracting complex verb components."""
        components = RootExtractorService.extract_verb_components("anakupenda")

        assert components["subject"] == "a"
        assert components["tense"] == "na"
        assert components["object"] == "ku"
        assert "pend" in components["root"]
        assert components["polarity"] == "affirmative"

    def test_is_likely_compound(self):
        """Test compound word detection."""
        assert RootExtractorService.is_likely_compound("ninakupenda") is True
        assert RootExtractorService.is_likely_compound("mtu") is False
        assert RootExtractorService.is_likely_compound("kitabu") is False

    def test_empty_word(self):
        """Empty input cannot produce a valid morphological root."""
        with pytest.raises(ValueError, match="Word cannot be empty"):
            RootExtractorService.extract("")

    def test_short_word(self):
        """Test handling very short word."""
        root = RootExtractorService.extract("a")
        assert root.root == "a"


# Integration tests
class TestServiceIntegration:
    """Integration tests between services."""

    def test_classify_then_extract(self):
        """Test classifying then extracting root."""
        word = "kitabu"

        # Classify
        bantu_class = BantuClassifierService.infer_class(word, WordType.NOUN)
        assert bantu_class == BantuClass.KI_VI

        # Extract root
        root = RootExtractorService.extract(word, WordType.NOUN)
        assert root.prefix == "ki"
        assert "tabu" in root.root

    def test_extract_then_classify(self):
        """Test extracting root then classifying."""
        word = "wasoma"

        # Extract
        root = RootExtractorService.extract(word, WordType.VERB)

        # Try to classify (verbs return UNKNOWN)
        bantu_class = BantuClassifierService.infer_class(word, WordType.VERB)
        assert bantu_class == BantuClass.UNKNOWN


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
