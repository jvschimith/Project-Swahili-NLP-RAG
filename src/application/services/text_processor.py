"""
Application Layer - Text Processing Service

Application service for text processing operations.
Handles tokenization, normalization, and text cleaning.
"""
import re
from typing import List, Set, Tuple
from loguru import logger


class SwahiliTextProcessor:
    """
    Text processor specialized for Swahili language.
    
    Provides:
    - Tokenization
    - Normalization
    - Stopword removal
    - N-gram extraction
    - Text cleaning
    
    Examples:
        >>> processor = SwahiliTextProcessor()
        >>> tokens = processor.tokenize("Ninasoma kitabu")
        >>> ['ninasoma', 'kitabu']
    """
    
    # Swahili stopwords (common function words)
    STOPWORDS: Set[str] = {
        # Conjunctions
        'na', 'au', 'lakini', 'kwa', 'kwamba',
        # Pronouns
        'mimi', 'wewe', 'yeye', 'sisi', 'ninyi', 'wao',
        # Articles/Determiners
        'hii', 'hizi', 'hilo', 'hiyo', 'ile', 'wale', 'yule',
        # Prepositions
        'ya', 'wa', 'la', 'za', 'katika', 'kwa', 'kutoka',
        # Copula/Auxiliary
        'ni', 'si', 'ndi', 'ndo',
        # Common verbs
        'kuwa', 'kuna',
        # Locatives
        'pale', 'hapa', 'huko', 'hapo',
    }
    
    # Punctuation pattern
    PUNCTUATION = r'[.,!?;:()\[\]{}"\'«»—…]'
    
    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalize text: lowercase, remove extra spaces.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
            
        Examples:
            >>> SwahiliTextProcessor.normalize("  HABARI  Yako  ")
            'habari yako'
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower().strip()
        
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        return text
    
    @staticmethod
    def tokenize(text: str, remove_punct: bool = True) -> List[str]:
        """
        Tokenize Swahili text.
        
        Args:
            text: Input text
            remove_punct: Remove punctuation if True
            
        Returns:
            List of tokens
            
        Examples:
            >>> SwahiliTextProcessor.tokenize("Ninasoma kitabu cha historia")
            ['ninasoma', 'kitabu', 'cha', 'historia']
        """
        if not text:
            return []
        
        # Normalize first
        text = SwahiliTextProcessor.normalize(text)
        
        # Remove punctuation if requested
        if remove_punct:
            text = re.sub(SwahiliTextProcessor.PUNCTUATION, ' ', text)
        
        # Split by whitespace
        tokens = text.split()
        
        # Filter empty tokens
        tokens = [t for t in tokens if t]
        
        return tokens
    
    @staticmethod
    def remove_stopwords(tokens: List[str]) -> List[str]:
        """
        Remove stopwords from token list.
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered tokens
            
        Examples:
            >>> tokens = ['ninasoma', 'kitabu', 'cha', 'historia']
            >>> SwahiliTextProcessor.remove_stopwords(tokens)
            ['ninasoma', 'kitabu', 'historia']
        """
        return [t for t in tokens if t not in SwahiliTextProcessor.STOPWORDS]
    
    @staticmethod
    def extract_ngrams(tokens: List[str], n: int = 2) -> List[str]:
        """
        Extract n-grams from token list.
        
        Args:
            tokens: List of tokens
            n: N-gram size (default: 2 = bigrams)
            
        Returns:
            List of n-grams as strings
            
        Examples:
            >>> tokens = ['nina', 'soma', 'kitabu']
            >>> SwahiliTextProcessor.extract_ngrams(tokens, 2)
            ['nina soma', 'soma kitabu']
        """
        if len(tokens) < n:
            return []
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i+n])
            ngrams.append(ngram)
        
        return ngrams
    
    @staticmethod
    def clean_for_db(text: str, max_length: int = 500) -> str:
        """
        Clean text for database insertion.
        
        Args:
            text: Input text
            max_length: Maximum length
            
        Returns:
            Cleaned text
            
        Examples:
            >>> SwahiliTextProcessor.clean_for_db("Text\\x00with\\x1fcontrol")
            'Textwithcontrol'
        """
        text = SwahiliTextProcessor.normalize(text)
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Truncate if necessary
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    @staticmethod
    def extract_sentences(text: str) -> List[str]:
        """
        Split text into sentences.
        
        Args:
            text: Input text
            
        Returns:
            List of sentences
            
        Examples:
            >>> text = "Habari yako. Ninasoma kitabu."
            >>> SwahiliTextProcessor.extract_sentences(text)
            ['Habari yako', 'Ninasoma kitabu']
        """
        # Split by sentence-ending punctuation
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter empty
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Input text
            
        Returns:
            Word count
        """
        tokens = SwahiliTextProcessor.tokenize(text)
        return len(tokens)
    
    @staticmethod
    def get_word_frequency(text: str) -> dict:
        """
        Get word frequency distribution.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary {word: count}
            
        Examples:
            >>> text = "kitabu cha kitabu"
            >>> SwahiliTextProcessor.get_word_frequency(text)
            {'kitabu': 2, 'cha': 1}
        """
        tokens = SwahiliTextProcessor.tokenize(text)
        
        frequency = {}
        for token in tokens:
            frequency[token] = frequency.get(token, 0) + 1
        
        return frequency


# Usage example
if __name__ == "__main__":
    print("=== Swahili Text Processor ===\n")
    
    # Test text
    text = "Ninasoma kitabu cha historia. Kitabu hiki ni nzuri sana!"
    
    print(f"Original: {text}\n")
    
    # Normalize
    normalized = SwahiliTextProcessor.normalize(text)
    print(f"Normalized: {normalized}")
    
    # Tokenize
    tokens = SwahiliTextProcessor.tokenize(text)
    print(f"\nTokens: {tokens}")
    print(f"Token count: {len(tokens)}")
    
    # Remove stopwords
    filtered = SwahiliTextProcessor.remove_stopwords(tokens)
    print(f"\nFiltered (no stopwords): {filtered}")
    
    # Extract bigrams
    bigrams = SwahiliTextProcessor.extract_ngrams(tokens, 2)
    print(f"\nBigrams: {bigrams[:5]}")
    
    # Word frequency
    freq = SwahiliTextProcessor.get_word_frequency(text)
    print(f"\nWord Frequency:")
    for word, count in sorted(freq.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {word}: {count}")
    
    # Extract sentences
    sentences = SwahiliTextProcessor.extract_sentences(text)
    print(f"\nSentences ({len(sentences)}):")
    for i, sent in enumerate(sentences, 1):
        print(f"  {i}. {sent}")
    
    print("\n✓ Text processor test complete!")
