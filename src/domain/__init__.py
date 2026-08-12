"""
Domain Layer

Domain layer containing:
- Value Objects: Immutable objects identified by value
- Entities: Objects with unique identity
- Domain Services: Complex business logic
- Repository Interfaces: Persistence contracts

This layer is the core of the system and should not depend on
frameworks or infrastructure details.
"""

# Value Objects
from .value_objects import (
    BantuClass,
    Etymology,
    WordType,
    SentimentScore,
    MorphologicalRoot,
    VerbComponents,
    EntityType,
)
from .linguistic_rules import (
    CORE_WORD_TYPE_VALUES,
    AFFIRMATIVE_POLARITY,
    NEGATIVE_POLARITY,
)

# Entities
from .entities import (
    Lexeme,
    WordForm,
    Meaning,
    Context,
    Derivation,
    SwahiliTerm,
    DictionaryEntry,
    VerbConjugation,
    POSRecord,
    NewsArticle,
)

# Repository Interfaces
from .repositories import (
    ITermRepository,
    IDictionaryRepository,
    IConjugationRepository,
    IPOSRepository,
    INewsRepository,
)

# Domain Services
from .services.bantu_classifier import BantuClassifierService
from .services.linguistic_analysis import (
    LinguisticAnalysisResult,
    LinguisticAnalysisService,
)
from .services.root_extractor import RootExtractorService

__all__ = [
    # Value Objects
    "BantuClass",
    "Etymology",
    "WordType",
    "SentimentScore",
    "MorphologicalRoot",
    "VerbComponents",
    "EntityType",
    "CORE_WORD_TYPE_VALUES",
    "AFFIRMATIVE_POLARITY",
    "NEGATIVE_POLARITY",
    # Entities
    "Lexeme",
    "WordForm",
    "Meaning",
    "Context",
    "Derivation",
    "SwahiliTerm",
    "DictionaryEntry",
    "VerbConjugation",
    "POSRecord",
    "NewsArticle",
    # Repositories
    "ITermRepository",
    "IDictionaryRepository",
    "IConjugationRepository",
    "IPOSRepository",
    "INewsRepository",
    # Domain Services
    "BantuClassifierService",
    "LinguisticAnalysisResult",
    "LinguisticAnalysisService",
    "RootExtractorService",
]
