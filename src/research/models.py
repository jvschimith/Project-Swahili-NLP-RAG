"""Research experiment models kept outside linguistic and crawl domains."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from src.acquisition.pipeline import ACQUISITION_VERSION

CANDIDATE_POLICY_VERSION = "candidate-quality-v1"


class PilotState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


class ReviewLabel(str, Enum):
    GOOD_ARTICLE = "good_article"
    ACCEPTABLE = "acceptable"
    BOILERPLATE_HEAVY = "boilerplate_heavy"
    TOO_SHORT = "too_short"
    MIXED_LANGUAGE = "mixed_language"
    MEDIA_PLACEHOLDER_HEAVY = "media_placeholder_heavy"
    WRONG_CONTENT_TYPE = "wrong_content_type"
    NEEDS_REVIEW = "needs_review"


@dataclass(frozen=True)
class PilotSource:
    name: str
    seed_url: str
    category: str
    rationale: str
    expected_language_route: str | None = None
    robots_status: str | None = None
    static_suitability: str | None = None
    candidate_availability: str | None = None
    dynamic_dependence: str | None = None


@dataclass(frozen=True)
class PilotConfiguration:
    sources: tuple[PilotSource, ...]
    max_pages_per_source: int = 10
    max_depth: int = 1
    min_delay_seconds: float = 2.0
    expected_language: str = "sw"
    acquisition_version: str = ACQUISITION_VERSION
    candidate_policy_version: str = CANDIDATE_POLICY_VERSION

    def __post_init__(self) -> None:
        if not 1 <= len(self.sources) <= 8:
            raise ValueError("Pilot requires between one and eight bounded sources")
        if not 1 <= self.max_pages_per_source <= 20:
            raise ValueError("Per-source pilot budget must be between 1 and 20")
        if self.max_pages_per_source * len(self.sources) > 100:
            raise ValueError("Pilot acquisition budget cannot exceed 100 attempts")
        if self.max_depth not in {0, 1, 2}:
            raise ValueError("Pilot depth must be between zero and two")
        if self.min_delay_seconds < 1:
            raise ValueError("Pilot rate delay must be at least one second")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class CorpusPilotRun:
    id: str
    configuration: PilotConfiguration
    state: PilotState = PilotState.CREATED
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    crawl_job_ids: list[str] = field(default_factory=list)
    error: str | None = None

    @classmethod
    def create(cls, configuration: PilotConfiguration) -> CorpusPilotRun:
        return cls(str(uuid4()), configuration)

    def start(self) -> None:
        if self.state != PilotState.CREATED:
            raise ValueError("Only a created pilot can start")
        self.state = PilotState.RUNNING

    def associate_job(self, job_id: str) -> None:
        if self.state != PilotState.RUNNING:
            raise ValueError("Crawl jobs can only be associated while a pilot is running")
        if job_id not in self.crawl_job_ids:
            self.crawl_job_ids.append(job_id)

    def complete(self) -> None:
        if self.state != PilotState.RUNNING:
            raise ValueError("Only a running pilot can complete")
        self.state = PilotState.COMPLETED
        self.finished_at = datetime.now(timezone.utc)

    def interrupt(self) -> None:
        if self.state != PilotState.RUNNING:
            raise ValueError("Only a running pilot can be interrupted")
        self.state = PilotState.INTERRUPTED
        self.finished_at = datetime.now(timezone.utc)

    def fail(self, reason: str) -> None:
        self.state = PilotState.FAILED
        self.error = reason[:1000]
        self.finished_at = datetime.now(timezone.utc)


@dataclass(frozen=True)
class ArtifactReview:
    pilot_id: str
    artifact_id: str
    label: ReviewLabel
    note: str | None
    reviewed_at: datetime

    @classmethod
    def create(
        cls, pilot_id: str, artifact_id: str, label: ReviewLabel, note: str | None = None
    ) -> ArtifactReview:
        clean_note = note.strip() if note else None
        if clean_note and len(clean_note) > 1000:
            raise ValueError("Review note cannot exceed 1000 characters")
        return cls(pilot_id, artifact_id, label, clean_note, datetime.now(timezone.utc))


def deterministic_sample(
    artifacts: list[dict[str, object]], *, per_source: int = 3, weak_limit: int = 5
) -> list[str]:
    """Select reproducibly by source, then include the shortest weak candidates."""
    by_source: dict[str, list[dict[str, object]]] = {}
    for artifact in artifacts:
        by_source.setdefault(str(artifact.get("domain", "unknown")), []).append(artifact)
    selected: list[str] = []
    for domain in sorted(by_source):
        ordered = sorted(by_source[domain], key=lambda item: str(item.get("document_id", "")))
        selected.extend(str(item["document_id"]) for item in ordered[:per_source])
    shortest = sorted(
        artifacts,
        key=lambda item: (
            int(str(item.get("text_length", 0))),
            str(item.get("document_id", "")),
        ),
    )[:weak_limit]
    selected.extend(str(item["document_id"]) for item in shortest)
    return list(dict.fromkeys(selected))
