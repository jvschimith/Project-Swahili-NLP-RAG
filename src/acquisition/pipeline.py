"""End-to-end static HTML to provenance-preserving corpus document pipeline."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urlsplit

from .content import (
    StaticArticleExtractor,
    canonicalize_url,
    content_hash,
    normalize_text,
    validate_language,
)
from .inspector import PageInspector
from .models import IngestionResult, WebDocument
from .storage import CorpusStore

ACQUISITION_VERSION = "web-corpus-v1"


class AcquisitionPipeline:
    """Coordinate inspection through optional storage without morphology coupling."""

    def __init__(self, store: CorpusStore | None = None):
        self.store = store
        self.metrics: Counter[str] = Counter()

    def process_html(
        self,
        original_url: str,
        html: str,
        *,
        final_url: str | None = None,
        retrieved_at: datetime | None = None,
        persist: bool = True,
    ) -> IngestionResult:
        self.metrics["pages_inspected"] += 1
        final_url = final_url or original_url
        inspection = PageInspector.inspect_html(final_url, html)
        extraction = StaticArticleExtractor.extract(html, inspection)
        if not extraction.raw_text:
            key = "dynamic_pages_detected" if inspection.likely_dynamic else "pages_failed"
            self.metrics[key] += 1
            return IngestionResult("unsupported", None, extraction.strategy.value)

        raw_text = extraction.raw_text.strip()
        normalized = normalize_text(raw_text)
        metadata_language = extraction.metadata.get("in_language")
        language = validate_language(
            normalized,
            html_language=inspection.html_language,
            metadata_language=metadata_language if isinstance(metadata_language, str) else None,
        )
        if not language.is_acceptable:
            metric = (
                "uncertain_language"
                if language.status.value == "uncertain"
                else "non_swahili_rejected"
            )
            self.metrics[metric] += 1
            return IngestionResult("language_rejected", None, language.status.value)

        digest = content_hash(normalized)
        try:
            canonical = canonicalize_url(inspection.canonical_url or final_url)
        except ValueError:
            canonical = canonicalize_url(final_url)
        timestamp = (
            (retrieved_at or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat()
        )
        document = WebDocument(
            document_id=digest[:20],
            original_url=original_url,
            final_url=final_url,
            canonical_url=canonical,
            source_domain=urlsplit(canonical).hostname or "",
            title=extraction.title or inspection.open_graph.get("og:title") or inspection.title,
            author=extraction.author,
            published_at=extraction.published_at,
            retrieved_at=timestamp,
            language=language.language,
            language_confidence=language.confidence,
            language_evidence=language.evidence,
            raw_text=raw_text,
            normalized_text=normalized,
            content_hash=digest,
            extraction_method=extraction.strategy.value,
            extraction_metadata={**extraction.metadata, "inspection": inspection.to_dict()},
            provenance={
                "original_url": original_url,
                "final_url": final_url,
                "canonical_url": canonical,
                "retrieved_at": timestamp,
                "acquisition_version": ACQUISITION_VERSION,
            },
        )
        self.metrics["documents_extracted"] += 1
        self.metrics["swahili_documents"] += 1
        if not persist:
            return IngestionResult("dry_run", document)
        if self.store is None:
            raise ValueError("A corpus store is required when persist=True")
        result = self.store.save(document)
        if result.duplicate_reason:
            self.metrics[f"duplicates_by_{result.duplicate_reason.split('_')[0]}"] += 1
        return result
