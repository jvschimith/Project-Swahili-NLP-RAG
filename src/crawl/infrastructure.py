"""Infrastructure adapters for responsible crawl orchestration."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone

from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.acquisition.pipeline import AcquisitionPipeline
from src.application.services.url_analyzer import URLNewsAnalyzer
from src.infrastructure.database.models import DBCrawlFrontier, DBCrawlJob

from .application import AcquisitionOutcome, RobotsResource
from .domain import (
    CandidatePriority,
    CrawlBudget,
    CrawlJob,
    CrawlRepository,
    CrawlStatus,
    CrawlUrl,
    FrontierEntry,
    FrontierState,
    ResourceKind,
    TerminationReason,
)


def _utc(value: datetime) -> datetime:
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value


class SqlAlchemyCrawlRepository(CrawlRepository):
    """SQLite-tested SQLAlchemy repository for crawl jobs and their frontiers."""

    def __init__(self, session: Session):
        self.session = session

    def save_job(self, job: CrawlJob) -> None:
        self._upsert_job(job)
        self.session.commit()

    def _upsert_job(self, job: CrawlJob) -> None:
        row = self.session.get(DBCrawlJob, job.id)
        values = self._job_values(job)
        if row is None:
            row = DBCrawlJob(**values)
            self.session.add(row)
        else:
            for key, value in values.items():
                setattr(row, key, value)

    def get_job(self, job_id: str) -> CrawlJob | None:
        row = self.session.get(DBCrawlJob, job_id)
        return self._to_job(row) if row else None

    def add_entry(self, entry: FrontierEntry) -> bool:
        existing = (
            self.session.query(DBCrawlFrontier.id)
            .filter(
                DBCrawlFrontier.job_id == entry.job_id,
                DBCrawlFrontier.canonical_url == entry.url.value,
            )
            .first()
        )
        if existing:
            return False
        row = DBCrawlFrontier(**self._entry_values(entry))
        self.session.add(row)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            return False
        entry.id = row.id
        return True

    def save_entry(self, entry: FrontierEntry) -> None:
        self._upsert_entry(entry)
        self.session.commit()

    def _upsert_entry(self, entry: FrontierEntry) -> None:
        if entry.id is None:
            raise ValueError("Cannot update a frontier entry without persistence identity")
        row = self.session.get(DBCrawlFrontier, entry.id)
        if row is None:
            raise ValueError(f"Frontier entry not found: {entry.id}")
        for key, value in self._entry_values(entry).items():
            setattr(row, key, value)

    def checkpoint(self, job: CrawlJob, entry: FrontierEntry) -> None:
        """Persist aggregate counters and the current entry in one transaction."""
        self._upsert_job(job)
        self._upsert_entry(entry)
        self.session.commit()

    def next_queued(self, job_id: str) -> FrontierEntry | None:
        row = (
            self.session.query(DBCrawlFrontier)
            .filter(
                DBCrawlFrontier.job_id == job_id,
                DBCrawlFrontier.state == FrontierState.QUEUED.value,
            )
            .order_by(
                DBCrawlFrontier.depth.asc(),
                DBCrawlFrontier.priority.desc(),
                DBCrawlFrontier.id.asc(),
            )
            .first()
        )
        return self._to_entry(row) if row else None

    def list_entries(self, job_id: str) -> list[FrontierEntry]:
        rows = (
            self.session.query(DBCrawlFrontier)
            .filter(DBCrawlFrontier.job_id == job_id)
            .order_by(DBCrawlFrontier.id.asc())
            .all()
        )
        return [self._to_entry(row) for row in rows]

    def recover_processing(self, job_id: str) -> int:
        rows = (
            self.session.query(DBCrawlFrontier)
            .filter(
                DBCrawlFrontier.job_id == job_id,
                DBCrawlFrontier.state == FrontierState.PROCESSING.value,
            )
            .all()
        )
        for row in rows:
            row.state = FrontierState.QUEUED.value
            row.updated_at = datetime.now(timezone.utc)
        self.session.commit()
        return len(rows)

    def count_attempted_for_origin(self, job_id: str, origin: str) -> int:
        return int(
            self.session.query(DBCrawlFrontier)
            .filter(
                DBCrawlFrontier.job_id == job_id,
                DBCrawlFrontier.origin == origin,
                DBCrawlFrontier.state.in_(
                    {FrontierState.COMPLETED.value, FrontierState.FAILED.value}
                ),
            )
            .count()
        )

    @staticmethod
    def _job_values(job: CrawlJob) -> dict[str, object]:
        return {
            "id": job.id,
            "seeds_json": json.dumps(job.seeds),
            "allowed_origins_json": json.dumps(sorted(job.allowed_origins)),
            "max_pages": job.budget.max_pages,
            "max_depth": job.budget.max_depth,
            "max_failures": job.budget.max_failures,
            "per_origin_pages": job.budget.per_origin_pages,
            "min_delay_seconds": job.min_delay_seconds,
            "user_agent": job.user_agent,
            "status": job.status.value,
            "termination_reason": job.termination_reason.value if job.termination_reason else None,
            "pages_attempted": job.pages_attempted,
            "pages_completed": job.pages_completed,
            "pages_failed": job.pages_failed,
            "pages_skipped": job.pages_skipped,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
        }

    @staticmethod
    def _entry_values(entry: FrontierEntry) -> dict[str, object]:
        return {
            "job_id": entry.job_id,
            "canonical_url": entry.url.value,
            "origin": entry.url.origin,
            "parent_url": entry.parent_url,
            "depth": entry.depth,
            "state": entry.state.value,
            "discovered_at": entry.discovered_at,
            "updated_at": entry.updated_at,
            "skip_reason": entry.skip_reason,
            "error": entry.error,
            "attempts": entry.attempts,
            "priority": int(entry.priority),
            "resource_kind": entry.resource_kind.value,
            "candidate_evidence_json": json.dumps(entry.candidate_evidence),
            "acquisition_stage": entry.acquisition_stage,
            "acquisition_reason": entry.acquisition_reason,
            "artifact_id": entry.artifact_id,
            "artifact_created": entry.artifact_created,
            "duplicate_reason": entry.duplicate_reason,
        }

    @staticmethod
    def _to_job(row: DBCrawlJob) -> CrawlJob:
        return CrawlJob(
            id=row.id,
            seeds=tuple(json.loads(row.seeds_json)),
            allowed_origins=frozenset(json.loads(row.allowed_origins_json)),
            budget=CrawlBudget(
                row.max_pages, row.max_depth, row.max_failures, row.per_origin_pages
            ),
            min_delay_seconds=row.min_delay_seconds,
            user_agent=row.user_agent,
            status=CrawlStatus(row.status),
            termination_reason=(
                TerminationReason(row.termination_reason) if row.termination_reason else None
            ),
            pages_attempted=row.pages_attempted,
            pages_completed=row.pages_completed,
            pages_failed=row.pages_failed,
            pages_skipped=row.pages_skipped,
            created_at=_utc(row.created_at),
            updated_at=_utc(row.updated_at),
        )

    @staticmethod
    def _to_entry(row: DBCrawlFrontier) -> FrontierEntry:
        return FrontierEntry(
            id=row.id,
            job_id=row.job_id,
            url=CrawlUrl(row.canonical_url),
            depth=row.depth,
            state=FrontierState(row.state),
            parent_url=row.parent_url,
            discovered_at=_utc(row.discovered_at),
            updated_at=_utc(row.updated_at),
            skip_reason=row.skip_reason,
            error=row.error,
            attempts=row.attempts,
            priority=CandidatePriority(row.priority),
            resource_kind=ResourceKind(row.resource_kind),
            candidate_evidence=tuple(json.loads(row.candidate_evidence_json)),
            acquisition_stage=row.acquisition_stage,
            acquisition_reason=row.acquisition_reason,
            artifact_id=row.artifact_id,
            artifact_created=row.artifact_created,
            duplicate_reason=row.duplicate_reason,
        )


class PublicUrlSafetyAdapter:
    def is_safe(self, url: str) -> bool:
        try:
            URLNewsAnalyzer.validate_public_url(url)
        except ValueError:
            return False
        return True


class SafeRobotsRetriever:
    """Retrieve robots.txt through the existing SSRF-aware HTTP boundary."""

    def __init__(self, analyzer: URLNewsAnalyzer | None = None):
        self.analyzer = analyzer or URLNewsAnalyzer()

    def retrieve(self, origin: str) -> RobotsResource:
        result = self.analyzer.fetch_result(
            f"{origin}/robots.txt",
            allowed_content_types=("text/plain", "text/html", "application/octet-stream"),
            accepted_status_codes=frozenset({404, 410}),
        )
        if result is None:
            return RobotsResource("unreachable")
        if result.status_code in {404, 410}:
            return RobotsResource("missing")
        return RobotsResource("available", result.html)


class SystemClock:
    def monotonic(self) -> float:
        return time.monotonic()

    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)


class WebAcquisitionAdapter:
    """Anti-corruption adapter around safe fetch and Web Corpus Acquisition v1."""

    def __init__(self, analyzer: URLNewsAnalyzer, pipeline: AcquisitionPipeline):
        self.analyzer = analyzer
        self.pipeline = pipeline

    def acquire(self, url: str) -> AcquisitionOutcome:
        fetched = self.analyzer.fetch_result(url)
        if fetched is None:
            return AcquisitionOutcome(False, url, reason="network_failure", stage="fetch")
        soup = BeautifulSoup(fetched.html, "html.parser")
        links = tuple(
            href
            for node in soup.find_all("a", href=True)
            if isinstance((href := node.get("href")), str)
        )
        result = self.pipeline.process_html(
            url,
            fetched.html,
            final_url=fetched.final_url,
            retrieved_at=fetched.retrieved_at,
        )
        if result.document is None:
            observation = result.observation
            return AcquisitionOutcome(
                False,
                fetched.final_url,
                reason=observation.reason.value if observation else result.status,
                stage=observation.stage.value if observation else None,
                details=observation_details(observation),
                discovered_links=links,
            )
        return AcquisitionOutcome(
            True,
            fetched.final_url,
            fetched.html,
            links,
            result.document.document_id,
            reason=result.observation.reason.value if result.observation else "accepted",
            stage=result.observation.stage.value if result.observation else "storage",
            details=observation_details(result.observation),
            artifact_created=result.status == "stored",
            duplicate_reason=result.duplicate_reason,
        )


def observation_details(observation) -> tuple[tuple[str, object], ...]:
    if observation is None:
        return ()
    values = (
        ("extraction_strategy", observation.extraction_strategy),
        ("html_language", observation.html_language),
        ("article_container", observation.article_container),
        ("main_container", observation.main_container),
        ("json_ld_article", observation.json_ld_article),
        ("paragraph_count", observation.paragraph_count),
        ("extracted_character_count", observation.extracted_character_count),
        ("dynamic_signal", observation.dynamic_signal),
        ("language_status", observation.language_status),
        ("language_evidence_score", observation.language_evidence_score),
        ("language_evidence", observation.language_evidence),
    )
    return tuple((key, value) for key, value in values if value is not None and value != ())
