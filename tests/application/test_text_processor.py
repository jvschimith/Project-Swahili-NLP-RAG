"""
Unit Tests - Application Layer: Text Processor

Tests for Swahili text processing service.
"""

import pytest

from src.application.services.text_processor import SwahiliTextProcessor


class TestTextNormalization:
    """Tests for text normalization."""

    def test_normalize_lowercase(self):
        """Test lowercase conversion."""
        result = SwahiliTextProcessor.normalize("HABARI YAKO")
        assert result == "habari yako"

    def test_normalize_strip_spaces(self):
        """Test stripping extra spaces."""
        result = SwahiliTextProcessor.normalize("  habari   yako  ")
        assert result == "habari yako"

    def test_normalize_multiple_spaces(self):
        """Test removing multiple spaces."""
        result = SwahiliTextProcessor.normalize("habari    yako")
        assert result == "habari yako"

    def test_normalize_empty_string(self):
        """Test normalizing empty string."""
        result = SwahiliTextProcessor.normalize("")
        assert result == ""

    def test_normalize_none(self):
        """Test normalizing None."""
        result = SwahiliTextProcessor.normalize(None)
        assert result == ""


class TestTokenization:
    """Tests for tokenization."""

    def test_tokenize_simple_sentence(self):
        """Test tokenizing simple sentence."""
        tokens = SwahiliTextProcessor.tokenize("Ninasoma kitabu")
        assert tokens == ["ninasoma", "kitabu"]

    def test_tokenize_with_punctuation(self):
        """Test tokenizing with punctuation."""
        tokens = SwahiliTextProcessor.tokenize("Habari yako, rafiki!")
        assert "yako" in tokens
        assert "rafiki" in tokens
        assert "," not in tokens
        assert "!" not in tokens

    def test_tokenize_keeps_punctuation(self):
        """Test keeping punctuation when requested."""
        tokens = SwahiliTextProcessor.tokenize(
            "Habari yako, rafiki!", remove_punct=False
        )
        assert "," in tokens or any("," in t for t in tokens)

    def test_tokenize_empty_string(self):
        """Test tokenizing empty string."""
        tokens = SwahiliTextProcessor.tokenize("")
        assert tokens == []

    def test_tokenize_multiple_sentences(self):
        """Test tokenizing multiple sentences."""
        tokens = SwahiliTextProcessor.tokenize("Ninasoma kitabu. Kitabu ni nzuri.")
        assert "ninasoma" in tokens
        assert "kitabu" in tokens
        assert "nzuri" in tokens


class TestStopwordRemoval:
    """Tests for stopword removal."""

    def test_remove_stopwords(self):
        """Test removing stopwords."""
        tokens = ["ninasoma", "kitabu", "cha", "historia"]
        filtered = SwahiliTextProcessor.remove_stopwords(tokens)

        assert "ninasoma" in filtered
        assert "kitabu" in filtered
        assert "historia" in filtered
        assert "cha" not in filtered  # 'cha' is a stopword

    def test_remove_stopwords_empty_list(self):
        """Test removing stopwords from empty list."""
        filtered = SwahiliTextProcessor.remove_stopwords([])
        assert filtered == []

    def test_remove_stopwords_all_stopwords(self):
        """Test list with only stopwords."""
        tokens = ["na", "ya", "wa", "ni"]
        filtered = SwahiliTextProcessor.remove_stopwords(tokens)
        assert len(filtered) == 0


class TestNgramExtraction:
    """Tests for n-gram extraction."""

    def test_extract_bigrams(self):
        """Test extracting bigrams."""
        tokens = ["nina", "soma", "kitabu"]
        bigrams = SwahiliTextProcessor.extract_ngrams(tokens, 2)

        assert len(bigrams) == 2
        assert "nina soma" in bigrams
        assert "soma kitabu" in bigrams

    def test_extract_trigrams(self):
        """Test extracting trigrams."""
        tokens = ["nina", "soma", "kitabu", "nzuri"]
        trigrams = SwahiliTextProcessor.extract_ngrams(tokens, 3)

        assert len(trigrams) == 2
        assert "nina soma kitabu" in trigrams
        assert "soma kitabu nzuri" in trigrams

    def test_extract_ngrams_insufficient_tokens(self):
        """Test n-grams with insufficient tokens."""
        tokens = ["nina"]
        bigrams = SwahiliTextProcessor.extract_ngrams(tokens, 2)
        assert bigrams == []

    def test_extract_ngrams_empty_list(self):
        """Test n-grams with empty list."""
        ngrams = SwahiliTextProcessor.extract_ngrams([], 2)
        assert ngrams == []


class TestTextCleaning:
    """Tests for text cleaning."""

    def test_clean_for_db(self):
        """Test cleaning text for database."""
        text = "  SAMPLE TEXT  "
        cleaned = SwahiliTextProcessor.clean_for_db(text)
        assert cleaned == "sample text"

    def test_clean_for_db_remove_control_chars(self):
        """Test removing control characters."""
        text = "text\x00with\x1fcontrol"
        cleaned = SwahiliTextProcessor.clean_for_db(text)
        assert "\x00" not in cleaned
        assert "\x1f" not in cleaned

    def test_clean_for_db_truncate_long_text(self):
        """Test truncating long text."""
        long_text = "a" * 1000
        cleaned = SwahiliTextProcessor.clean_for_db(long_text, max_length=100)
        assert len(cleaned) <= 103  # 100 + "..."
        assert cleaned.endswith("...")


class TestSentenceExtraction:
    """Tests for sentence extraction."""

    def test_extract_sentences(self):
        """Test extracting sentences."""
        text = "Habari yako. Ninasoma kitabu. Asante sana!"
        sentences = SwahiliTextProcessor.extract_sentences(text)

        assert len(sentences) == 3
        assert "Habari yako" in sentences
        assert "Ninasoma kitabu" in sentences
        assert "Asante sana" in sentences

    def test_extract_sentences_different_punctuation(self):
        """Test with different punctuation."""
        text = "Habari? Nzuri! Asante."
        sentences = SwahiliTextProcessor.extract_sentences(text)
        assert len(sentences) == 3

    def test_extract_sentences_no_punctuation(self):
        """Test text without punctuation."""
        text = "habari yako"
        sentences = SwahiliTextProcessor.extract_sentences(text)
        assert len(sentences) == 1


class TestWordCounting:
    """Tests for word counting."""

    def test_count_words(self):
        """Test counting words."""
        text = "Ninasoma kitabu cha historia"
        count = SwahiliTextProcessor.count_words(text)
        assert count == 4

    def test_count_words_with_punctuation(self):
        """Test counting with punctuation."""
        text = "Habari yako, rafiki!"
        count = SwahiliTextProcessor.count_words(text)
        assert count == 3

    def test_count_words_empty(self):
        """Test counting empty text."""
        count = SwahiliTextProcessor.count_words("")
        assert count == 0


class TestWordFrequency:
    """Tests for word frequency."""

    def test_get_word_frequency(self):
        """Test getting word frequency."""
        text = "kitabu cha kitabu historia kitabu"
        freq = SwahiliTextProcessor.get_word_frequency(text)

        assert freq["kitabu"] == 3
        assert freq["cha"] == 1
        assert freq["historia"] == 1

    def test_get_word_frequency_empty(self):
        """Test frequency of empty text."""
        freq = SwahiliTextProcessor.get_word_frequency("")
        assert freq == {}

    def test_get_word_frequency_case_insensitive(self):
        """Test case-insensitive frequency."""
        text = "Kitabu kitabu KITABU"
        freq = SwahiliTextProcessor.get_word_frequency(text)
        assert freq["kitabu"] == 3


# Integration tests
class TestTextProcessorIntegration:
    """Integration tests for text processor."""

    def test_full_pipeline(self):
        """Test full text processing pipeline."""
        text = "  NINASOMA kitabu cha HISTORIA. Kitabu ni nzuri!  "

        # Normalize
        normalized = SwahiliTextProcessor.normalize(text)
        assert normalized == "ninasoma kitabu cha historia. kitabu ni nzuri!"

        # Tokenize
        tokens = SwahiliTextProcessor.tokenize(normalized)
        assert "ninasoma" in tokens

        # Remove stopwords
        filtered = SwahiliTextProcessor.remove_stopwords(tokens)
        assert "cha" not in filtered
        assert "ni" not in filtered

        # Extract bigrams
        bigrams = SwahiliTextProcessor.extract_ngrams(filtered, 2)
        assert len(bigrams) > 0


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
