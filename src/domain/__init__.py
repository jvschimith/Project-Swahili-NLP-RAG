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
# Entities
from .entities import (
    Context,
    Derivation,
    DictionaryEntry,
    Lexeme,
    Meaning,
    NewsArticle,
    POSRecord,
    SwahiliTerm,
    VerbConjugation,
    WordForm,
)
from .linguistic_rules import (
    AFFIRMATIVE_POLARITY,
    CORE_WORD_TYPE_VALUES,
    NEGATIVE_POLARITY,
)

# Repository Interfaces
from .repositories import (
    IConjugationRepository,
    IDictionaryRepository,
    INewsRepository,
    IPOSRepository,
    ITermRepository,
)

# Domain Services
from .services.bantu_classifier import BantuClassifierService
from .services.linguistic_analysis import (
    LinguisticAnalysisResult,
    LinguisticAnalysisService,
)
from .services.root_extractor import RootExtractorService
from .value_objects import (
    BantuClass,
    EntityType,
    Etymology,
    MorphologicalRoot,
    SentimentScore,
    VerbComponents,
    WordType,
)

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
