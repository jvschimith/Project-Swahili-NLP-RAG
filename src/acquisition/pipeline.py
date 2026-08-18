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
from .models import (
    AcquisitionObservation,
    AcquisitionReason,
    AcquisitionStage,
    IngestionResult,
    WebDocument,
)
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
            reason = (
                AcquisitionReason.DYNAMIC_BROWSER_REQUIRED
                if inspection.likely_dynamic
                else AcquisitionReason.INSUFFICIENT_STATIC_CONTENT
            )
            return IngestionResult(
                "unsupported",
                None,
                extraction.strategy.value,
                observation=self._observation(
                    inspection,
                    extraction.strategy.value,
                    AcquisitionStage.STATIC_EXTRACTION,
                    reason,
                    extracted_character_count=0,
                ),
            )

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
            reason = (
                AcquisitionReason.UNCERTAIN_LANGUAGE
                if language.status.value == "uncertain"
                else AcquisitionReason.LIKELY_NON_SWAHILI
            )
            return IngestionResult(
                "language_rejected",
                None,
                language.status.value,
                observation=self._observation(
                    inspection,
                    extraction.strategy.value,
                    AcquisitionStage.LANGUAGE_VALIDATION,
                    reason,
                    extracted_character_count=len(normalized),
                    language_status=language.status.value,
                    language_evidence_score=language.confidence,
                    language_evidence=language.evidence,
                ),
            )

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
            return IngestionResult(
                "dry_run",
                document,
                observation=self._observation(
                    inspection,
                    extraction.strategy.value,
                    AcquisitionStage.STORAGE,
                    AcquisitionReason.ACCEPTED,
                    extracted_character_count=len(normalized),
                    language_status=language.status.value,
                    language_evidence_score=language.confidence,
                    language_evidence=language.evidence,
                ),
            )
        if self.store is None:
            raise ValueError("A corpus store is required when persist=True")
        result = self.store.save(document)
        if result.duplicate_reason:
            self.metrics[f"duplicates_by_{result.duplicate_reason.split('_')[0]}"] += 1
        duplicate_reason = (
            {
                "canonical_url": AcquisitionReason.DUPLICATE_CANONICAL_URL,
                "content_hash": AcquisitionReason.DUPLICATE_CONTENT,
            }.get(result.duplicate_reason)
            if result.duplicate_reason
            else None
        )
        observation = self._observation(
            inspection,
            extraction.strategy.value,
            AcquisitionStage.DEDUPLICATION if duplicate_reason else AcquisitionStage.STORAGE,
            duplicate_reason or AcquisitionReason.ACCEPTED,
            extracted_character_count=len(normalized),
            language_status=language.status.value,
            language_evidence_score=language.confidence,
            language_evidence=language.evidence,
        )
        return IngestionResult(
            result.status,
            result.document,
            result.duplicate_reason,
            result.storage_path,
            observation,
        )

    @staticmethod
    def _observation(
        inspection,
        strategy: str,
        stage: AcquisitionStage,
        reason: AcquisitionReason,
        **details,
    ) -> AcquisitionObservation:
        return AcquisitionObservation(
            stage=stage,
            reason=reason,
            extraction_strategy=strategy,
            html_language=inspection.html_language,
            article_container=inspection.has_article,
            main_container=inspection.has_main,
            json_ld_article=bool(
                PageInspector.ARTICLE_TYPES.intersection(inspection.json_ld_types)
            ),
            paragraph_count=inspection.paragraph_count,
            dynamic_signal=inspection.likely_dynamic,
            title=inspection.title,
            **details,
        )
