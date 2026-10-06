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


class AcquisitionStage(str, Enum):
    STATIC_EXTRACTION = "static_extraction"
    LANGUAGE_VALIDATION = "language_validation"
    DEDUPLICATION = "deduplication"
    STORAGE = "storage"


class AcquisitionReason(str, Enum):
    ACCEPTED = "accepted"
    INSUFFICIENT_STATIC_CONTENT = "insufficient_static_content"
    DYNAMIC_BROWSER_REQUIRED = "dynamic_browser_required"
    LIKELY_NON_SWAHILI = "likely_non_swahili"
    UNCERTAIN_LANGUAGE = "uncertain_language"
    DUPLICATE_CANONICAL_URL = "duplicate_canonical_url"
    DUPLICATE_CONTENT = "duplicate_content"


@dataclass(frozen=True)
class AcquisitionObservation:
    """Typed evidence explaining the terminal Web Acquisition decision."""

    stage: AcquisitionStage
    reason: AcquisitionReason
    extraction_strategy: str | None = None
    html_language: str | None = None
    article_container: bool | None = None
    main_container: bool | None = None
    json_ld_article: bool | None = None
    paragraph_count: int | None = None
    extracted_character_count: int | None = None
    dynamic_signal: bool | None = None
    language_status: str | None = None
    language_evidence_score: float | None = None
    language_evidence: tuple[str, ...] = ()
    title: str | None = None


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
    observation: AcquisitionObservation | None = None
