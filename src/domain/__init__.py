"""
Domain Layer

Camada de domínio contendo:
- Value Objects: Objetos imutáveis identificados por valor
- Entities: Objetos com identidade única
- Domain Services: Lógica de negócio complexa
- Repository Interfaces: Contratos de persistência

Esta camada é o núcleo do sistema e não deve depender de
frameworks ou detalhes de infraestrutura.
"""

# Value Objects
from .value_objects import (
    BantuClass,
    Etymology,
    WordType,
    SentimentScore,
    MorphologicalRoot,
    EntityType,
)

# Entities
from .entities import (
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
from .services.root_extractor import RootExtractorService

__all__ = [
    # Value Objects
    "BantuClass",
    "Etymology",
    "WordType",
    "SentimentScore",
    "MorphologicalRoot",
    "EntityType",
    # Entities
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
    "RootExtractorService",
]
