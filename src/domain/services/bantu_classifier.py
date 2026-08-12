"""
Domain Service: Bantu Classifier

Domain Services encapsulate business logic that does not naturally
belong to a specific Entity or Value Object.

Responsibilities:
- Infer Bantu noun classes from morphological prefixes
- Provide semantic descriptions of the classes
- Validate class consistency

This is a pure Domain Service:
- No infrastructure dependencies
- No side effects
- Testable in isolation
- Complex domain logic
"""
from typing import Dict, Tuple, Optional
from loguru import logger

from ..linguistic_rules import (
    NOUN_CLASS_EXAMPLES,
    NOUN_CLASS_PREFIX_RULES,
    NOUN_CLASS_SPECIAL_CASES,
)
from ..value_objects import BantuClass, WordType


class BantuClassifierService:
    """
    Domain Service: Bantu noun-class classification.

    Swahili has a noun-class system inherited from Bantu languages, in
    which nouns are grouped by prefixes that signal semantic and
    grammatical properties.

    Main classes:
        1/2 (M-WA): People (mtu/watu - person/people)
        3/4 (M-MI): Plants (mti/miti - tree/trees)
        5/6 (JI-MA): Fruits, pairs (jicho/macho - eye/eyes)
        7/8 (KI-VI): Tools (kisu/visu - knife/knives)
        9/10 (N-N): Animals (nyumba/nyumba - house/houses)
        11/14 (U): Abstract concepts (uzuri - beauty)
        16/17/18 (PA-KU-MU): Locatives (pahali - place)

    Business Rules:
        - Only nouns have noun classes
        - Prefixes may vary between singular and plural
        - Some words can belong to multiple classes (polysemy)
        - Loanwords from other languages often default to class 9/10
    
    Examples:
        >>> classifier = BantuClassifierService()
        >>> classifier.infer_class("mtu", WordType.NOUN)
        BantuClass.M_WA
        >>> classifier.infer_class("kiti", WordType.NOUN)
        BantuClass.KI_VI
        >>> classifier.infer_class("soma", WordType.VERB)
        BantuClass.UNKNOWN
    """
    
    # Mapping from prefixes to classes
    # Format: {(singular_prefixes, plural_prefixes): BantuClass}
    PREFIX_TO_CLASS: Dict[Tuple[str, ...], BantuClass] = {
        prefixes: BantuClass(class_value)
        for prefixes, class_value in NOUN_CLASS_PREFIX_RULES.items()
    }
    
    # Special cases (words that do not follow regular patterns)
    SPECIAL_CASES: Dict[str, BantuClass] = {
        word: BantuClass(class_value)
        for word, class_value in NOUN_CLASS_SPECIAL_CASES.items()
    }
    
    @classmethod
    def infer_class(cls, word: str, word_type: WordType = WordType.NOUN) -> BantuClass:
        """
        Infer the Bantu class of a word.

        Business Rules:
            - Only nouns have meaningful Bantu classes
            - Check special cases first
            - Use prefix matching for general cases
            - Return UNKNOWN if classification fails
        
        Args:
            word: Swahili word (normalized)
            word_type: Grammatical type of the word
            
        Returns:
            Inferred BantuClass
            
        Examples:
            >>> BantuClassifierService.infer_class("mtu", WordType.NOUN)
            BantuClass.M_WA
            >>> BantuClassifierService.infer_class("soma", WordType.VERB)
            BantuClass.UNKNOWN
        """
        # Rule 1: Only nouns have Bantu classes
        if word_type not in [WordType.NOUN, WordType.UNKNOWN]:
            logger.debug(
                f"Word '{word}' is {word_type.value}, not a noun. "
                f"Skipping Bantu class inference."
            )
            return BantuClass.UNKNOWN
        
        # Normalize word
        word_lower = word.lower().strip()
        
        # Rule 2: Check special cases first
        if word_lower in cls.SPECIAL_CASES:
            result = cls.SPECIAL_CASES[word_lower]
            logger.debug(f"Found special case: '{word}' → {result.value}")
            return result
        
        # Rule 3: Try prefix matching
        for prefixes, bantu_class in cls.PREFIX_TO_CLASS.items():
            for prefix in prefixes:
                if word_lower.startswith(prefix):
                    # Ensure the word is not just the prefix (it must have a root)
                    if len(word_lower) > len(prefix) + 1:
                        logger.debug(
                            f"Matched '{word}' to {bantu_class.value} "
                            f"via prefix '{prefix}'"
                        )
                        return bantu_class
        
        # Rule 4: If classification failed
        logger.debug(f"Could not infer Bantu class for '{word}'")
        return BantuClass.UNKNOWN
    
    @classmethod
    def get_class_description(cls, bantu_class: BantuClass) -> str:
        """
        Return a detailed semantic description of the Bantu class.
        
        Args:
            bantu_class: Bantu class
            
        Returns:
            English description
            
        Examples:
            >>> desc = BantuClassifierService.get_class_description(BantuClass.M_WA)
            >>> "Pessoas" in desc
            True
        """
        return bantu_class.description
    
    @classmethod
    def get_typical_examples(cls, bantu_class: BantuClass) -> list:
        """
        Return typical word examples for the class.
        
        Args:
            bantu_class: Bantu class
            
        Returns:
            List of examples (singular/plural)
            
        Examples:
            >>> examples = BantuClassifierService.get_typical_examples(BantuClass.M_WA)
            >>> ("mtu", "watu") in examples
            True
        """
        return NOUN_CLASS_EXAMPLES.get(bantu_class.value, [])
    
    @classmethod
    def validate_class_for_word(cls, word: str, claimed_class: BantuClass) -> bool:
        """
        Validate whether a Bantu class is consistent with a word.

        Useful for validating external dictionary data.
        
        Args:
            word: Swahili word
            claimed_class: Claimed class
            
        Returns:
            True if consistent, False otherwise
            
        Examples:
            >>> BantuClassifierService.validate_class_for_word("mtu", BantuClass.M_WA)
            True
            >>> BantuClassifierService.validate_class_for_word("mtu", BantuClass.KI_VI)
            False
        """
        inferred = cls.infer_class(word, WordType.NOUN)
        
        # If we cannot infer it, we cannot validate it
        if inferred == BantuClass.UNKNOWN:
            logger.warning(
                f"Cannot validate class for '{word}': inference returned UNKNOWN"
            )
            return True  # Assume valid if inference is unavailable
        
        # Compare against the claimed class
        is_valid = inferred == claimed_class
        
        if not is_valid:
            logger.warning(
                f"Class mismatch for '{word}': "
                f"claimed {claimed_class.value}, inferred {inferred.value}"
            )
        
        return is_valid
    
    @classmethod
    def get_all_classes(cls) -> list:
        """
        Return a list of all available Bantu classes.
        
        Returns:
            List of BantuClass values
        """
        return [
            BantuClass.M_WA,
            BantuClass.M_MI,
            BantuClass.JI_MA,
            BantuClass.KI_VI,
            BantuClass.N_N,
            BantuClass.U,
            BantuClass.PA_KU_MU,
        ]


# Usage example (for tests/documentation)
if __name__ == "__main__":
    print("=== Bantu Classifier Service ===\n")
    
    # Test classification
    test_words = [
        ("mtu", WordType.NOUN),
        ("watu", WordType.NOUN),
        ("kiti", WordType.NOUN),
        ("mti", WordType.NOUN),
        ("uzuri", WordType.NOUN),
        ("soma", WordType.VERB),
    ]
    
    print("Classifying words:\n")
    for word, wtype in test_words:
        cls = BantuClassifierService.infer_class(word, wtype)
        print(f"{word:15} ({wtype.value:10}) → {cls.value:10} - {cls.description}")
    
    # Show examples
    print("\n\nExamples by class:\n")
    for bantu_class in BantuClassifierService.get_all_classes():
        examples = BantuClassifierService.get_typical_examples(bantu_class)
        print(f"\n{bantu_class.value} - {bantu_class.description}:")
        for ex in examples[:2]:  # Show 2 examples
            if ex[1]:  # If it has a plural form
                print(f"  {ex[0]:15} / {ex[1]:15} ({ex[2]})")
            else:
                print(f"  {ex[0]:15} ({ex[2]})")
    
    # Test validation
    print("\n\nClass validation:\n")
    validations = [
        ("mtu", BantuClass.M_WA, True),
        ("mtu", BantuClass.KI_VI, False),
        ("kiti", BantuClass.KI_VI, True),
    ]
    
    for word, cls, expected in validations:
        result = BantuClassifierService.validate_class_for_word(word, cls)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{word}' as {cls.value}: {result}")
