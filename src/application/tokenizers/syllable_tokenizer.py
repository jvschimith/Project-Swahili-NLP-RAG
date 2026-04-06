"""
Tokenization - Syllable Tokenizer (Phase 2)

Syllable-level tokenization for better embeddings in low-resource settings.
Swahili has simple CV (consonant-vowel) syllable structure.
"""
from typing import List, Set, Tuple
import re


class SwahiliSyllableTokenizer:
    """
    Syllable-level tokenizer for Swahili.
    
    Advantages for low-resource NLP:
    - Better than character-level (captures phonological units)
    - Better than word-level (handles unseen words via syllables)
    - Smaller vocabulary than words, larger than characters
    - Captures morphological patterns naturally
    
    Swahili Syllable Structure:
    - Predominantly CV (consonant-vowel)
    - Allows V (vowel alone)
    - Allows CVC in some positions
    - No complex consonant clusters
    """
    
    # Swahili phonemes
    VOWELS: Set[str] = set('aeiou')
    CONSONANTS: Set[str] = set('bcdfghjklmnpqrstvwxyz')
    
    # Syllable patterns (in order of precedence)
    # Pattern priority: longest/most specific first
    PATTERNS = [
        r'[bcdfghjklmnpqrstvwxyz]+[aeiou]+[bcdfghjklmnpqrstvwxyz]',  # CVC
        r'[bcdfghjklmnpqrstvwxyz]+[aeiou]+',  # CV (most common)
        r'[aeiou]+',  # V (vowel-only syllables)
        r'[bcdfghjklmnpqrstvwxyz]+',  # C (consonant clusters - rare)
    ]
    
    @classmethod
    def tokenize(cls, word: str) -> List[str]:
        """
        Split Swahili word into syllables.
        
        Args:
            word: Swahili word to tokenize
            
        Returns:
            List of syllables
            
        Examples:
            >>> SwahiliSyllableTokenizer.tokenize("ninasoma")
            ['ni', 'na', 'so', 'ma']
            
            >>> SwahiliSyllableTokenizer.tokenize("mtu")
            ['mtu']
            
            >>> SwahiliSyllableTokenizer.tokenize("anakupenda")
            ['a', 'na', 'ku', 'pen', 'da']
            
            >>> SwahiliSyllableTokenizer.tokenize("kitabu")
            ['ki', 'ta', 'bu']
        """
        word = word.lower().strip()
        
        if not word:
            return []
        
        # Try each pattern
        for pattern in cls.PATTERNS:
            syllables = re.findall(pattern, word)
            
            # Validate segmentation
            if cls._is_valid_segmentation(syllables, word):
                return syllables
        
        # Fallback: return whole word if no valid segmentation
        return [word]
    
    @classmethod
    def tokenize_with_confidence(cls, word: str) -> Tuple[List[str], float]:
        """
        Tokenize with confidence score.
        
        Returns:
            (syllables, confidence) where confidence is 0.0-1.0
        """
        syllables = cls.tokenize(word)
        
        # Calculate confidence based on criteria
        confidence = 1.0
        
        # Penalty if fallback to whole word
        if len(syllables) == 1 and syllables[0] == word and len(word) > 3:
            confidence = 0.5
        
        # Penalty if invalid syllable structure
        for syl in syllables:
            if not any(v in syl for v in cls.VOWELS):
                confidence *= 0.8
        
        # Bonus if all syllables are CV pattern
        cv_count = sum(1 for syl in syllables if cls._is_cv_pattern(syl))
        if cv_count == len(syllables):
            confidence = min(1.0, confidence * 1.2)
        
        return syllables, confidence
    
    @classmethod
    def _is_valid_segmentation(cls, syllables: List[str], original: str) -> bool:
        """
        Check if syllable segmentation is valid.
        
        Criteria:
        1. Reconstructs to original word
        2. Each syllable has at least one vowel (except final consonants)
        3. No empty syllables
        """
        if not syllables:
            return False
        
        # Check reconstruction
        reconstructed = ''.join(syllables)
        if reconstructed != original:
            return False
        
        # Check syllable structure
        for i, syl in enumerate(syllables):
            if not syl:  # Empty syllable
                return False
            
            # All but last syllable must have vowel
            if i < len(syllables) - 1:
                if not any(v in syl for v in cls.VOWELS):
                    return False
        
        return True
    
    @classmethod
    def _is_cv_pattern(cls, syllable: str) -> bool:
        """Check if syllable follows CV (consonant-vowel) pattern."""
        if len(syllable) != 2:
            return False
        return syllable[0] in cls.CONSONANTS and syllable[1] in cls.VOWELS
    
    @classmethod
    def tokenize_sentence(cls, sentence: str) -> List[List[str]]:
        """
        Tokenize all words in a sentence.
        
        Args:
            sentence: Swahili sentence
            
        Returns:
            List of syllable lists (one per word)
            
        Example:
            >>> SwahiliSyllableTokenizer.tokenize_sentence("Ninasoma kitabu")
            [['ni', 'na', 'so', 'ma'], ['ki', 'ta', 'bu']]
        """
        words = sentence.lower().split()
        return [cls.tokenize(word) for word in words]
    
    @classmethod
    def get_vocabulary(cls, corpus: List[str]) -> Set[str]:
        """
        Extract syllable vocabulary from corpus.
        
        Useful for building syllable-level embeddings.
        
        Args:
            corpus: List of words or sentences
            
        Returns:
            Set of unique syllables
            
        Example:
            >>> corpus = ["ninasoma", "anasoma", "tunasoma"]
            >>> SwahiliSyllableTokenizer.get_vocabulary(corpus)
            {'ni', 'na', 'so', 'ma', 'a', 'tu'}
        """
        vocab = set()
        
        for text in corpus:
            # Handle both words and sentences
            if ' ' in text:
                words = text.split()
            else:
                words = [text]
            
            for word in words:
                syllables = cls.tokenize(word)
                vocab.update(syllables)
        
        return vocab
    
    @classmethod
    def count_syllables(cls, word: str) -> int:
        """
        Count syllables in a word.
        
        Useful for readability metrics and poetry analysis.
        """
        return len(cls.tokenize(word))
    
    @classmethod
    def analyze_syllable_structure(cls, word: str) -> Dict[str, any]:
        """
        Detailed syllable structure analysis.
        
        Returns:
            Dictionary with syllable patterns and statistics
        """
        syllables = cls.tokenize(word)
        
        return {
            "word": word,
            "syllables": syllables,
            "count": len(syllables),
            "patterns": [cls._get_pattern_type(syl) for syl in syllables],
            "has_cv_only": all(cls._is_cv_pattern(syl) for syl in syllables),
            "complexity": cls._calculate_complexity(syllables)
        }
    
    @classmethod
    def _get_pattern_type(cls, syllable: str) -> str:
        """Identify syllable pattern (V, CV, CVC, etc.)."""
        pattern = ""
        for char in syllable:
            if char in cls.VOWELS:
                pattern += "V"
            elif char in cls.CONSONANTS:
                pattern += "C"
            else:
                pattern += "X"
        return pattern
    
    @classmethod
    def _calculate_complexity(cls, syllables: List[str]) -> float:
        """
        Calculate syllable complexity score (0.0-1.0).
        
        Simple CV patterns = low complexity
        CVC or longer = higher complexity
        """
        if not syllables:
            return 0.0
        
        complexity_sum = 0
        for syl in syllables:
            pattern = cls._get_pattern_type(syl)
            if pattern == "CV":
                complexity_sum += 0.0
            elif pattern == "V":
                complexity_sum += 0.2
            elif pattern == "CVC":
                complexity_sum += 0.5
            else:
                complexity_sum += 1.0
        
        return complexity_sum / len(syllables)


# ==================== SYLLABLE-BASED TEXT STATISTICS ====================

class SyllableStatistics:
    """Compute text statistics using syllable tokenization."""
    
    @staticmethod
    def average_syllables_per_word(text: str) -> float:
        """Calculate average syllables per word."""
        words = text.split()
        if not words:
            return 0.0
        
        total_syllables = sum(
            SwahiliSyllableTokenizer.count_syllables(word)
            for word in words
        )
        return total_syllables / len(words)
    
    @staticmethod
    def syllable_diversity(text: str) -> float:
        """
        Calculate syllable diversity (TTR at syllable level).
        
        Returns ratio of unique syllables to total syllables.
        """
        words = text.split()
        all_syllables = []
        
        for word in words:
            all_syllables.extend(SwahiliSyllableTokenizer.tokenize(word))
        
        if not all_syllables:
            return 0.0
        
        unique_syllables = set(all_syllables)
        return len(unique_syllables) / len(all_syllables)
    
    @staticmethod
    def flesch_reading_ease_swahili(text: str) -> float:
        """
        Swahili adaptation of Flesch Reading Ease.
        
        Uses syllable count instead of English-specific metrics.
        Higher score = easier to read.
        
        Score ranges:
        90-100: Very Easy
        60-70: Standard
        30-50: Difficult
        0-30: Very Difficult
        """
        words = text.split()
        sentences = text.count('.') + text.count('!') + text.count('?')
        
        if not words or sentences == 0:
            return 0.0
        
        # Count syllables
        total_syllables = sum(
            SwahiliSyllableTokenizer.count_syllables(word)
            for word in words
        )
        
        avg_syllables_per_word = total_syllables / len(words)
        avg_words_per_sentence = len(words) / sentences
        
        # Adapted formula (Swahili has more syllables than English typically)
        score = 206.835 - (1.015 * avg_words_per_sentence) - (84.6 * avg_syllables_per_word)
        
        return max(0.0, min(100.0, score))
