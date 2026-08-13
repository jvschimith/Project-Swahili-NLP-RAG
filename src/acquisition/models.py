"""Canonical, serializable models for static web corpus acquisition."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum


class ExtractionStrategy(str, Enum):
    JSON_LD_ARTICLE = "json_ld_article"
    SEMANTIC_ARTICLE = "semantic_article"
    MAIN_CONTENT = "main_content"
    GENERIC_PARAGRAPH = "generic_paragraph"
    DYNAMIC_BROWSER_REQUIRED = "dynamic_browser_required"
    UNSUPPORTED = "unsupported"


class LanguageStatus(str, Enum):
    LIKELY_SWAHILI = "likely_swahili"
    MULTILINGUAL = "multilingual"
    LIKELY_NON_SWAHILI = "likely_non_swahili"
    UNCERTAIN = "uncertain"


@dataclass(frozen=True)
class LanguageValidationResult:
    language: str | None
    confidence: float
    evidence: tuple[str, ...]
    status: LanguageStatus
    is_acceptable: bool


@dataclass(frozen=True)
class ExtractionResult:
    strategy: ExtractionStrategy
    raw_text: str
    title: str | None = None
    author: str | None = None
    published_at: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class WebDocument:
    document_id: str
    original_url: str
    final_url: str
    canonical_url: str
    source_domain: str
    title: str | None
    author: str | None
    published_at: str | None
    retrieved_at: str
    language: str | None
    language_confidence: float
    language_evidence: tuple[str, ...]
    raw_text: str
    normalized_text: str
    content_hash: str
    extraction_method: str
    extraction_metadata: dict[str, object]
    provenance: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class IngestionResult:
    status: str
    document: WebDocument | None
    duplicate_reason: str | None = None
    storage_path: str | None = None
