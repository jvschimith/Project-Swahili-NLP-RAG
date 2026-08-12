"""
Domain Layer - Value Objects

Value Objects are immutable objects that represent domain concepts
through their attributes. Two Value Objects with the same attributes are
considered equal.

Characteristics:
- Immutable (frozen=True)
- No identity of their own
- Comparison by value
- Self-validating
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class BantuClass(str, Enum):
    """
    Value Object: Swahili Bantu noun classes (Ngeli).

    Swahili, as a Bantu language, has a noun-class system that groups
    nouns by semantic and morphological characteristics.
    
    Examples:
        M_WA (1/2): mtu (person) -> watu (people)
        M_MI (3/4): mti (tree) -> miti (trees)
        KI_VI (7/8): kiti (chair) -> viti (chairs)
    """
    M_WA = "1/2"          # People (Mtu/Watu)
    M_MI = "3/4"          # Plants, elongated objects (Mti/Miti)
    JI_MA = "5/6"         # Fruits, augmentatives (Tunda/Matunda)
    KI_VI = "7/8"         # Tools, artifacts (Kiti/Viti)
    N_N = "9/10"          # Animals, common objects (Nyumba/Nyumba)
    U = "11/14"           # Abstract concepts, singular (Uzuri)
    PA_KU_MU = "16/17/18" # Locatives (pahali, kule, ndani)
    UNKNOWN = "N/A"       # Unidentified class
    
    @property
    def description(self) -> str:
        """Return the semantic description of the class."""
        from .linguistic_rules import get_noun_class_description

        return get_noun_class_description(self.value)
    
    @property
    def is_identified(self) -> bool:
        """Check whether the class was identified."""
        return self != self.UNKNOWN


class Etymology(str, Enum):
    """
    Value Object: Etymological origin of Swahili words.

    Swahili is influenced by multiple sources:
    - Bantu: Grammatical base and core vocabulary
    - Arabic: ~40% of the vocabulary (trade, religion)
    - English: Modern loanwords (technology, administration)
    - Portuguese: Colonial-period borrowing
    - Others: German, Hindi, Persian
    """
    BANTU = "bantu"           # Bantu origin (native)
    ARABIC = "arabic"         # Arabic loanword
    ENGLISH = "english"       # English loanword
    PORTUGUESE = "portuguese" # Portuguese loanword
    GERMAN = "german"         # German loanword
    INDIAN = "indian"         # Loanword from Indian languages (Hindi, Gujarati)
    PERSIAN = "persian"       # Persian loanword
    UNKNOWN = "unknown"       # Unknown origin
    
    @property
    def is_native(self) -> bool:
        """Check whether the word is of Bantu origin (native)."""
        return self == self.BANTU
    
    @property
    def is_loanword(self) -> bool:
        """Check whether the word is borrowed from another language."""
        return self not in [self.BANTU, self.UNKNOWN]


class WordType(str, Enum):
    """
    Value Object: Grammatical type of a word.

    Basic morphosyntactic classification.
    """
    NOUN = "noun"               # Noun (nomino)
    VERB = "verb"               # Verb (kitenzi)
    ADJECTIVE = "adjective"     # Adjective (kivumishi)
    ADVERB = "adverb"           # Adverb (kielezi)
    PRONOUN = "pronoun"         # Pronoun
    CONJUNCTION = "conjunction" # Conjunction
    PREPOSITION = "preposition" # Preposition
    INTERJECTION = "interjection" # Interjection
    DETERMINER = "determiner"   # Determiner
    NUMERAL = "numeral"         # Numeral
    UNKNOWN = "unknown"         # Unknown type
    
    @property
    def is_content_word(self) -> bool:
        """Check whether this is a content word rather than a function word."""
        return self in [self.NOUN, self.VERB, self.ADJECTIVE, self.ADVERB]


@dataclass(frozen=True)
class SentimentScore:
    """
    Value Object: Sentiment score for a text.

    Represents the polarity and confidence of a sentiment analysis.
    Immutable and self-validating.
    
    Attributes:
        polarity: Sentiment polarity [-1.0, 1.0]
                 -1.0 = very negative
                  0.0 = neutral
                 +1.0 = very positive
        confidence: Confidence score [0.0, 1.0]
                   0.0 = no confidence
                   1.0 = full confidence
    
    Examples:
        >>> score = SentimentScore(polarity=0.8, confidence=0.9)
        >>> score.label
        'positive'
        >>> score.is_positive
        True
    """
    polarity: float
    confidence: float
    
    def __post_init__(self):
        """Validate values after initialization."""
        if not -1.0 <= self.polarity <= 1.0:
            raise ValueError(
                f"Polarity must be between -1.0 and 1.0, got {self.polarity}"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
    
    @property
    def label(self) -> str:
        """
        Return a categorical label based on polarity.
        
        Returns:
            'positive', 'negative', or 'neutral'
        """
        if self.polarity > 0.1:
            return "positive"
        elif self.polarity < -0.1:
            return "negative"
        return "neutral"
    
    @property
    def is_positive(self) -> bool:
        """Check whether the sentiment is positive."""
        return self.polarity > 0.1
    
    @property
    def is_negative(self) -> bool:
        """Check whether the sentiment is negative."""
        return self.polarity < -0.1
    
    @property
    def is_neutral(self) -> bool:
        """Check whether the sentiment is neutral."""
        return -0.1 <= self.polarity <= 0.1
    
    def is_confident(self, threshold: float = 0.7) -> bool:
        """Check whether the analysis has high confidence."""
        return self.confidence >= threshold
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.label} (polarity={self.polarity:.2f}, confidence={self.confidence:.2f})"


@dataclass(frozen=True)
class MorphologicalRoot:
    """
    Value Object: Morphological root of a Swahili word.

    Represents the morphological decomposition of a word into:
    - Prefix (optional): Grammatical markers (wa-, ki-, m-)
    - Root: Semantic core of the word
    - Suffix (optional): Final grammatical markers (-a, -i, -e)
    
    Examples:
        >>> root = MorphologicalRoot(root="som", prefix="wa", suffix="a")
        >>> root.full_word
        'wasoma'
        >>> root.has_prefix
        True
    """
    root: str
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    
    def __post_init__(self):
        """Validate the root."""
        if not self.root or len(self.root) < 1:
            raise ValueError("Root cannot be empty")
        
        # Normalize to lowercase
        object.__setattr__(self, 'root', self.root.lower())
        if self.prefix:
            object.__setattr__(self, 'prefix', self.prefix.lower())
        if self.suffix:
            object.__setattr__(self, 'suffix', self.suffix.lower())
    
    @property
    def full_word(self) -> str:
        """
        Reconstruct the full word from its components.
        
        Returns:
            Full word (prefix + root + suffix)
        """
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        parts.append(self.root)
        if self.suffix:
            parts.append(self.suffix)
        return ''.join(parts)
    
    @property
    def has_prefix(self) -> bool:
        """Check whether a prefix is present."""
        return self.prefix is not None
    
    @property
    def has_suffix(self) -> bool:
        """Check whether a suffix is present."""
        return self.suffix is not None
    
    @property
    def is_simple(self) -> bool:
        """Check whether this is a simple word without affixes."""
        return not (self.has_prefix or self.has_suffix)
    
    def __str__(self) -> str:
        """String representation."""
        if self.is_simple:
            return f"[{self.root}]"
        return f"[{self.prefix or ''}-{self.root}-{self.suffix or ''}]"


@dataclass(frozen=True)
class VerbComponents:
    """
    Value Object: Structured verbal morphology for a Swahili form.

    This captures the major agglutinative components exposed by the
    current morphology service while remaining lightweight enough for the
    domain layer to adopt before persistence changes.
    """
    subject_marker: Optional[str] = None
    tense_marker: Optional[str] = None
    object_marker: Optional[str] = None
    root: Optional[str] = None
    final_vowel: Optional[str] = None
    suffixes_extensions: List[str] = None
    full_prefix: Optional[str] = None
    polarity: Optional[str] = None

    def __post_init__(self):
        """Normalize all populated markers and components."""
        from .linguistic_rules import infer_verb_polarity, normalize_linguistic_text, normalize_suffixes

        if self.subject_marker:
            object.__setattr__(self, 'subject_marker', normalize_linguistic_text(self.subject_marker))
        if self.tense_marker:
            object.__setattr__(self, 'tense_marker', normalize_linguistic_text(self.tense_marker))
        if self.object_marker:
            object.__setattr__(self, 'object_marker', normalize_linguistic_text(self.object_marker))
        if self.root:
            object.__setattr__(self, 'root', normalize_linguistic_text(self.root))
        if self.final_vowel:
            object.__setattr__(self, 'final_vowel', normalize_linguistic_text(self.final_vowel))
        if self.full_prefix:
            object.__setattr__(self, 'full_prefix', normalize_linguistic_text(self.full_prefix))

        object.__setattr__(self, 'suffixes_extensions', normalize_suffixes(self.suffixes_extensions))

        if self.polarity:
            object.__setattr__(self, 'polarity', normalize_linguistic_text(self.polarity))
        else:
            object.__setattr__(self, 'polarity', infer_verb_polarity(self.tense_marker))

    def __getitem__(self, key: str):
        """
        Compatibility accessor for legacy dict-style morphology usage.

        Existing code and tests use keys like 'subject' and 'final'.
        """
        mapping = {
            'subject': self.subject_marker,
            'tense': self.tense_marker,
            'object': self.object_marker,
            'root': self.root,
            'final': self.final_vowel,
            'full_prefix': self.full_prefix,
            'suffixes_extensions': self.suffixes_extensions,
            'polarity': self.polarity,
        }
        return mapping[key]

    def to_dict(self) -> dict:
        """Export the structured components in the legacy dictionary shape."""
        return {
            'subject': self.subject_marker,
            'tense': self.tense_marker,
            'object': self.object_marker,
            'root': self.root,
            'final': self.final_vowel,
            'full_prefix': self.full_prefix,
            'suffixes_extensions': list(self.suffixes_extensions),
            'polarity': self.polarity,
        }


@dataclass(frozen=True)
class EntityType:
    """
    Value Object: Named entity type (NER).

    Represents Named Entity Recognition categories.
    
    Attributes:
        group: Entity group (PER, LOC, ORG, DATE, etc.)
        subtype: Optional subtype (e.g. 'country' for LOC)
    """
    group: str
    subtype: Optional[str] = None
    
    def __post_init__(self):
        """Validate and normalize the entity group."""
        valid_groups = {'PER', 'LOC', 'ORG', 'DATE', 'TIME', 'MONEY', 'PERCENT', 'MISC'}
        
        group_upper = self.group.upper()
        if group_upper not in valid_groups:
            raise ValueError(f"Invalid entity group: {self.group}")
        
        object.__setattr__(self, 'group', group_upper)
        
        if self.subtype:
            object.__setattr__(self, 'subtype', self.subtype.lower())
    
    @property
    def is_person(self) -> bool:
        """Check whether this is a person."""
        return self.group == 'PER'
    
    @property
    def is_location(self) -> bool:
        """Check whether this is a location."""
        return self.group == 'LOC'
    
    @property
    def is_organization(self) -> bool:
        """Check whether this is an organization."""
        return self.group == 'ORG'
    
    def __str__(self) -> str:
        """String representation."""
        if self.subtype:
            return f"{self.group}:{self.subtype}"
        return self.group


# Usage example (for tests/documentation)
if __name__ == "__main__":
    # Test BantuClass
    bantu = BantuClass.M_WA
    print(f"Class: {bantu}, Description: {bantu.description}")
    
    # Test SentimentScore
    sentiment = SentimentScore(polarity=0.75, confidence=0.85)
    print(f"Sentiment: {sentiment}")
    
    # Test MorphologicalRoot
    root = MorphologicalRoot(root="som", prefix="wa")
    print(f"Root: {root}, Full word: {root.full_word}")
    
    # Test EntityType
    entity = EntityType(group="PER", subtype="politician")
    print(f"Entity: {entity}, Is person: {entity.is_person}")
