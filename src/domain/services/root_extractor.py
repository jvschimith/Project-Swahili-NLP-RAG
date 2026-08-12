"""
Domain Service: Morphological Root Extractor

Responsibilities:
- Extract the morphological root of Swahili words
- Identify prefixes and suffixes
- Provide full morphological decomposition

This is a pure Domain Service with no infrastructure dependencies.
"""
from typing import Optional, List, Tuple
from loguru import logger

from ..linguistic_rules import (
    AFFIRMATIVE_POLARITY,
    NOMINAL_PREFIXES,
    NOMINAL_SUFFIXES,
    VERBAL_PREFIXES,
    VERBAL_SUFFIXES,
    VERB_OBJECT_MARKERS,
    VERB_SUBJECT_MARKERS,
    VERB_TENSE_MARKERS,
)
from ..value_objects import MorphologicalRoot, VerbComponents, WordType


class RootExtractorService:
    """
    Domain Service: Morphological root extraction.

    Swahili, as an agglutinative language, forms words by adding prefixes
    and suffixes to a root. This service identifies those components.

    Swahili morphological structure:
        VERB: (subject)-(tense)-(object)-root-(derivation)
        Example: ni-na-ku-som-a = I-present-you-read-final

        NOUN: (class_prefix)-root-(suffix)
        Example: ki-tabu = class_7-book

    Business Rules:
        - Verbal prefixes: ni-, u-, a-, tu-, m-, wa-, ku-, li-, ta-, na-, me-
        - Nominal prefixes: m-, wa-, mi-, ki-, vi-, ma-, u-
        - Verbal suffixes: -a, -e, -i, -o, -u
        - Minimum word size = a root of 2+ characters
    
    Examples:
        >>> extractor = RootExtractorService()
        >>> root = extractor.extract("ninasoma")
        >>> root.root
        'som'
        >>> root.prefix
        'nina'
    """
    
    # Common verbal prefixes (subject markers + tense markers)
    VERBAL_PREFIXES = VERBAL_PREFIXES
    
    # Nominal prefixes (noun class prefixes)
    NOMINAL_PREFIXES = NOMINAL_PREFIXES
    
    # All prefixes (union)
    ALL_PREFIXES = sorted(
        set(VERBAL_PREFIXES + NOMINAL_PREFIXES),
        key=len,
        reverse=True  # Try the longest ones first
    )
    
    # Common verbal suffixes
    VERBAL_SUFFIXES = VERBAL_SUFFIXES
    
    # Nominal suffixes
    NOMINAL_SUFFIXES = NOMINAL_SUFFIXES
    
    ALL_SUFFIXES = sorted(
        set(VERBAL_SUFFIXES + NOMINAL_SUFFIXES),
        key=len,
        reverse=True
    )
    
    @classmethod
    def extract(
        cls, 
        word: str, 
        word_type: Optional[WordType] = None,
        aggressive: bool = False
    ) -> MorphologicalRoot:
        """
        Extract the morphological root of a word.
        
        Args:
            word: Swahili word (normalized)
            word_type: Grammatical type (helps guide extraction)
            aggressive: If True, removes more affixes (may be imprecise)
            
        Returns:
            MorphologicalRoot with identified root and affixes
            
        Business Rules:
            - Minimum word size: 2 characters
            - Try longer prefixes first
            - Keep a root of at least 2 characters
            - Conservative mode: remove only known prefixes
            - Aggressive mode: also try removing suffixes
            
        Examples:
            >>> RootExtractorService.extract("ninasoma")
            MorphologicalRoot(root='som', prefix='nina', suffix='a')
            >>> RootExtractorService.extract("mtu")
            MorphologicalRoot(root='tu', prefix='m', suffix=None)
        """
        # Initial validation
        if not word:
            raise ValueError("Word cannot be empty")
        if len(word) < 2:
            logger.debug(f"Word too short: '{word}'")
            return MorphologicalRoot(root=word)
        
        # Normalize word
        original = word.lower().strip()
        prefix_found = None
        suffix_found = None
        root = original
        
        # Choose prefix list based on the word type
        if word_type == WordType.VERB:
            prefixes_to_try = cls.VERBAL_PREFIXES
        elif word_type == WordType.NOUN:
            prefixes_to_try = cls.NOMINAL_PREFIXES
        else:
            prefixes_to_try = cls.ALL_PREFIXES
        
        # 1. Try removing prefixes
        for prefix in prefixes_to_try:
            if root.startswith(prefix):
                # Ensure enough root material remains
                remaining = root[len(prefix):]
                if len(remaining) >= 2:  # Minimum root length: 2 characters
                    prefix_found = prefix
                    root = remaining
                    logger.debug(f"Removed prefix '{prefix}' from '{original}'")
                    break  # Only one prefix at a time
        
        # 2. Try removing suffixes (if aggressive mode or verb)
        if aggressive or word_type == WordType.VERB:
            # Choose appropriate suffixes
            if word_type == WordType.VERB:
                suffixes_to_try = cls.VERBAL_SUFFIXES
            else:
                suffixes_to_try = cls.ALL_SUFFIXES
            
            for suffix in suffixes_to_try:
                if root.endswith(suffix):
                    # Ensure enough root material remains
                    remaining = root[:-len(suffix)]
                    if len(remaining) >= 2:  # Minimum root length: 2 characters
                        suffix_found = suffix
                        root = remaining
                        logger.debug(f"Removed suffix '{suffix}' from '{original}'")
                        break  # Only one suffix at a time
        
        # 3. Create and return MorphologicalRoot
        result = MorphologicalRoot(
            root=root,
            prefix=prefix_found,
            suffix=suffix_found
        )
        
        logger.debug(f"Extracted: '{original}' → {result}")
        return result
    
    @classmethod
    def extract_verb_components(cls, verb: str) -> VerbComponents:
        """
        Extract components specific to Swahili verbs.

        Swahili verbs follow this structure:
        (subject)-(tense)-(object)-root-(final)
        
        Args:
            verb: Conjugated Swahili verb
            
        Returns:
            VerbComponents with identified components
            
        Examples:
            >>> RootExtractorService.extract_verb_components("ninakupenda")
            {'subject': 'ni', 'tense': 'na', 'object': 'ku', 'root': 'pend', 'final': 'a'}
        """
        original = verb.lower().strip()
        subject_marker = None
        tense_marker = None
        object_marker = None
        root = None
        final_vowel = None

        # Subject markers (1 or 2 chars)
        remaining = original
        full_prefix = ""
        
        # 1. Try to identify subject
        for marker, person in VERB_SUBJECT_MARKERS.items():
            if remaining.startswith(marker):
                subject_marker = marker
                full_prefix += marker
                remaining = remaining[len(marker):]
                break
        
        # 2. Try to identify tense
        for marker, tense in VERB_TENSE_MARKERS.items():
            if remaining.startswith(marker):
                tense_marker = marker
                full_prefix += marker
                remaining = remaining[len(marker):]
                break
        
        # 3. Try to identify object
        for marker in VERB_OBJECT_MARKERS:
            if remaining.startswith(marker) and len(remaining) > len(marker) + 2:
                object_marker = marker
                full_prefix += marker
                remaining = remaining[len(marker):]
                break
        
        # 4. Final verbal suffix (usually -a, -e, -i)
        if remaining and remaining[-1] in 'aeiou':
            final_vowel = remaining[-1]
            remaining = remaining[:-1]
        
        # 5. What remains is the root
        root = remaining if remaining else None

        return VerbComponents(
            subject_marker=subject_marker,
            tense_marker=tense_marker,
            object_marker=object_marker,
            root=root,
            final_vowel=final_vowel,
            suffixes_extensions=[final_vowel] if final_vowel else [],
            full_prefix=full_prefix if full_prefix else None,
            # A well-formed surface verb without an overt negative marker is
            # affirmative in this lightweight analysis. Negative morphology
            # is still inferred centrally by VerbComponents when present.
            polarity=AFFIRMATIVE_POLARITY if root and final_vowel else None,
        )
    
    @classmethod
    def is_likely_compound(cls, word: str) -> bool:
        """
        Check whether a word is likely to be morphologically compound.
        
        Args:
            word: Word to check
            
        Returns:
            True if the word is likely compound
            
        Examples:
            >>> RootExtractorService.is_likely_compound("ninakupenda")
            True
            >>> RootExtractorService.is_likely_compound("mtu")
            False
        """
        # Heuristic: long word with multiple known prefixes
        root = cls.extract(word, aggressive=False)
        
        # If it has both prefix and suffix, it is probably compound
        if root.has_prefix and root.has_suffix:
            return True
        
        # If the prefix is long (>3 chars), it is probably compound
        if root.prefix and len(root.prefix) > 3:
            return True
        
        return False


# Usage example (for tests/documentation)
if __name__ == "__main__":
    print("=== Root Extractor Service ===\n")
    
    # Test root extraction
    test_words = [
        ("mtu", WordType.NOUN),
        ("watu", WordType.NOUN),
        ("kitabu", WordType.NOUN),
        ("ninasoma", WordType.VERB),
        ("anakupenda", WordType.VERB),
        ("tumemaliza", WordType.VERB),
        ("uzuri", WordType.NOUN),
    ]
    
    print("Extracting roots:\n")
    for word, wtype in test_words:
        root = RootExtractorService.extract(word, wtype)
        print(f"{word:15} → {root}")
    
    # Test verbal component extraction
    print("\n\nVerbal components:\n")
    verbs = ["ninasoma", "anakupenda", "tumemaliza", "wataenda"]
    
    for verb in verbs:
        components = RootExtractorService.extract_verb_components(verb)
        print(f"\n{verb}:")
        for key, value in components.items():
            if value:
                print(f"  {key:12}: {value}")
    
    # Test compound detection
    print("\n\nCompound words:\n")
    words = ["ninakupenda", "mtu", "tumemaliza", "uzuri"]
    
    for word in words:
        is_compound = RootExtractorService.is_likely_compound(word)
        status = "✓ Compound" if is_compound else "✗ Simple"
        print(f"{status:15} - {word}")
