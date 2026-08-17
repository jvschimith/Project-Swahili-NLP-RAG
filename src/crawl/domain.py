"""Domain model for responsible crawl orchestration."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, IntEnum
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import uuid4

TRACKING_PARAMETERS = {"fbclid", "gclid", "mc_cid", "mc_eid"}


class FrontierState(str, Enum):
    DISCOVERED = "discovered"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class CrawlStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    INTERRUPTED = "interrupted"
    COMPLETED = "completed"
    STOPPED = "stopped"


class TerminationReason(str, Enum):
    FRONTIER_EXHAUSTED = "frontier_exhausted"
    PAGE_BUDGET_EXHAUSTED = "page_budget_exhausted"
    FAILURE_BUDGET_EXHAUSTED = "failure_budget_exhausted"
    MANUALLY_STOPPED = "manually_stopped"
    INTERRUPTED = "interrupted"
    UNRECOVERABLE_FAILURE = "unrecoverable_failure"


class SkipReason(str, Enum):
    ROBOTS_DENIED = "robots_denied"
    EXTERNAL_ORIGIN = "external_origin"
    DEPTH_LIMIT = "depth_limit"
    UNSAFE_URL = "unsafe_url"
    UNSUPPORTED_SCHEME = "unsupported_scheme"
    DUPLICATE = "duplicate"
    PER_ORIGIN_LIMIT = "per_origin_limit"
    UNSUPPORTED_RESOURCE_KIND = "unsupported_resource_kind"
    COMPETING_LANGUAGE_PATH = "competing_language_path"


class CandidatePriority(IntEnum):
    """Durable ordering value; it never grants permission to fetch a URL."""

    LOW = 10
    NORMAL = 50
    HIGH = 90


class ResourceKind(str, Enum):
    ARTICLE = "article"
    SECTION = "section"
    VIDEO = "video"
    AUDIO = "audio"
    UNSUPPORTED_FILE = "unsupported_file"
    UNKNOWN = "unknown"


class CandidateEvidence(str, Enum):
    EXPECTED_LANGUAGE_PATH = "expected_language_path"
    COMPETING_LANGUAGE_PATH = "competing_language_path"
    ARTICLE_LIKE_PATH = "article_like_path"
    DATE_LIKE_PATH = "date_like_path"
    CATEGORY_LIKE_PATH = "category_like_path"
    VIDEO_LIKE_PATH = "video_like_path"
    AUDIO_LIKE_PATH = "audio_like_path"
    UNSUPPORTED_RESOURCE = "unsupported_resource_kind"


@dataclass(frozen=True)
class CandidateDecision:
    """Explain whether a URL is worth queueing, without accepting its content."""

    eligible: bool
    priority: CandidatePriority
    resource_kind: ResourceKind
    evidence: tuple[CandidateEvidence, ...] = ()
    reason: SkipReason | None = None


class LinkEligibilityPolicy:
    """Conservative, site-neutral URL evidence for bounded frontier selection."""

    _TARGET_SEGMENTS = frozenset({"sw", "swahili", "kiswahili"})
    # Deliberately small: only clear language-selector route markers seen commonly.
    _COMPETING_SEGMENTS = frozenset({"ar", "arabic", "zh", "chinese", "en", "english"})
    _SECTION_SEGMENTS = frozenset(
        {"category", "categories", "section", "sections", "tag", "tags", "author", "archive"}
    )
    _VIDEO_SEGMENTS = frozenset({"video", "videos", "vidio", "watch", "player", "embed"})
    _AUDIO_SEGMENTS = frozenset({"audio", "podcast", "podcasts", "sauti"})
    _NON_CORPUS_SEGMENTS = frozenset({"login", "signin", "account", "search", "share"})
    _UNSUPPORTED_SUFFIXES = frozenset(
        {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".svg",
            ".mp3",
            ".wav",
            ".ogg",
            ".mp4",
            ".webm",
            ".avi",
            ".pdf",
            ".css",
            ".js",
            ".xml",
            ".rss",
            ".atom",
            ".zip",
        }
    )

    @classmethod
    def evaluate(cls, url: CrawlUrl) -> CandidateDecision:
        import re

        parsed = urlsplit(url.value)
        path = parsed.path.lower()
        segments = tuple(segment for segment in path.split("/") if segment)
        tokens = tuple(re.findall(r"[a-z]+", path))
        evidence: list[CandidateEvidence] = []
        if any(path.endswith(suffix) for suffix in cls._UNSUPPORTED_SUFFIXES):
            return CandidateDecision(
                False,
                CandidatePriority.LOW,
                ResourceKind.UNSUPPORTED_FILE,
                (CandidateEvidence.UNSUPPORTED_RESOURCE,),
                SkipReason.UNSUPPORTED_RESOURCE_KIND,
            )
        if any(segment in cls._COMPETING_SEGMENTS for segment in segments):
            return CandidateDecision(
                False,
                CandidatePriority.LOW,
                ResourceKind.UNKNOWN,
                (CandidateEvidence.COMPETING_LANGUAGE_PATH,),
                SkipReason.COMPETING_LANGUAGE_PATH,
            )
        score = int(CandidatePriority.NORMAL)
        if any(segment in cls._TARGET_SEGMENTS for segment in segments):
            evidence.append(CandidateEvidence.EXPECTED_LANGUAGE_PATH)
            score += 10
        date_like = bool(re.search(r"/(?:19|20)\d{2}/(?:0?[1-9]|1[0-2])(?:/|$)", path))
        editorial_id = bool(re.search(r"/(?:a-\d+|a/.+\d+\.html)(?:/|$)", path))
        article_like = date_like or editorial_id or any(
            token in {"article", "articles", "story", "stories"} for token in tokens
        )
        if article_like:
            evidence.append(CandidateEvidence.ARTICLE_LIKE_PATH)
            score += 20
        if date_like:
            evidence.append(CandidateEvidence.DATE_LIKE_PATH)
            score += 10
        category_like = any(
            segment in cls._SECTION_SEGMENTS or segment in cls._NON_CORPUS_SEGMENTS
            for segment in segments
        )
        if category_like:
            evidence.append(CandidateEvidence.CATEGORY_LIKE_PATH)
            score -= 30
        query_values = {
            item.lower() for pair in parse_qsl(parsed.query) for item in pair if isinstance(item, str)
        }
        video_like = any(token in cls._VIDEO_SEGMENTS for token in tokens) or bool(
            {"video", "videos", "vidio"}.intersection(query_values)
        )
        if video_like:
            evidence.append(CandidateEvidence.VIDEO_LIKE_PATH)
            score -= 30
        audio_like = any(token in cls._AUDIO_SEGMENTS for token in tokens)
        if audio_like:
            evidence.append(CandidateEvidence.AUDIO_LIKE_PATH)
            score -= 30
        kind = (
            ResourceKind.VIDEO
            if video_like
            else (
                ResourceKind.AUDIO
                if audio_like
                else (
                    ResourceKind.SECTION
                    if category_like
                    else ResourceKind.ARTICLE if article_like else ResourceKind.UNKNOWN
                )
            )
        )
        priority = (
            CandidatePriority.HIGH
            if score >= 70
            else CandidatePriority.LOW if score < 50 else CandidatePriority.NORMAL
        )
        return CandidateDecision(True, priority, kind, tuple(evidence))


@dataclass(frozen=True)
class CrawlUrl:
    """Canonical HTTP(S) URL identity used by a crawl frontier."""

    value: str

    def __post_init__(self) -> None:
        parsed = urlsplit(self.value)
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Crawl URL must use HTTP or HTTPS")
        if not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Crawl URL must have a host and no credentials")

    @classmethod
    def parse(cls, value: str) -> CrawlUrl:
        parsed = urlsplit(value)
        scheme = parsed.scheme.lower()
        if scheme not in {"http", "https"}:
            raise ValueError("Crawl URL must use HTTP or HTTPS")
        if not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Crawl URL must have a host and no credentials")
        hostname = parsed.hostname.lower().rstrip(".")
        port = parsed.port
        netloc = hostname
        if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
            netloc = f"{hostname}:{port}"
        query = urlencode(
            sorted(
                (key, item)
                for key, item in parse_qsl(parsed.query, keep_blank_values=True)
                if not key.lower().startswith("utm_") and key.lower() not in TRACKING_PARAMETERS
            )
        )
        return cls(urlunsplit((scheme, netloc, parsed.path or "/", query, "")))

    @property
    def origin(self) -> str:
        parsed = urlsplit(self.value)
        return f"{parsed.scheme}://{parsed.netloc}"


@dataclass(frozen=True)
class CrawlBudget:
    max_pages: int = 25
    max_depth: int = 2
    max_failures: int = 5
    per_origin_pages: int = 25

    def __post_init__(self) -> None:
        if self.max_pages < 1 or self.per_origin_pages < 1:
            raise ValueError("Page budgets must be positive")
        if self.max_depth < 0 or self.max_failures < 1:
            raise ValueError("Depth must be non-negative and failure budget positive")
        if self.per_origin_pages > self.max_pages:
            raise ValueError("Per-origin page budget cannot exceed total page budget")


ALLOWED_TRANSITIONS = {
    FrontierState.DISCOVERED: {FrontierState.QUEUED, FrontierState.SKIPPED},
    FrontierState.QUEUED: {FrontierState.PROCESSING, FrontierState.SKIPPED},
    FrontierState.PROCESSING: {
        FrontierState.COMPLETED,
        FrontierState.FAILED,
        FrontierState.QUEUED,
        FrontierState.SKIPPED,
    },
    FrontierState.COMPLETED: set(),
    FrontierState.SKIPPED: set(),
    FrontierState.FAILED: set(),
}


@dataclass
class FrontierEntry:
    id: int | None
    job_id: str
    url: CrawlUrl
    depth: int
    state: FrontierState = FrontierState.DISCOVERED
    parent_url: str | None = None
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    skip_reason: str | None = None
    error: str | None = None
    attempts: int = 0
    priority: CandidatePriority = CandidatePriority.NORMAL
    resource_kind: ResourceKind = ResourceKind.UNKNOWN
    candidate_evidence: tuple[str, ...] = ()
    acquisition_stage: str | None = None
    acquisition_reason: str | None = None
    artifact_id: str | None = None
    artifact_created: bool = False
    duplicate_reason: str | None = None

    def transition(
        self, target: FrontierState, *, reason: str | None = None, now: datetime | None = None
    ) -> None:
        if target not in ALLOWED_TRANSITIONS[self.state]:
            raise ValueError(f"Forbidden frontier transition: {self.state.value} -> {target.value}")
        self.state = target
        self.updated_at = now or datetime.now(timezone.utc)
        if target == FrontierState.PROCESSING:
            self.attempts += 1
        elif target == FrontierState.SKIPPED:
            self.skip_reason = reason
        elif target == FrontierState.FAILED:
            self.error = reason


@dataclass
class CrawlJob:
    id: str
    seeds: tuple[str, ...]
    allowed_origins: frozenset[str]
    budget: CrawlBudget
    min_delay_seconds: float
    user_agent: str
    status: CrawlStatus = CrawlStatus.CREATED
    termination_reason: TerminationReason | None = None
    pages_attempted: int = 0
    pages_completed: int = 0
    pages_failed: int = 0
    pages_skipped: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(
        cls,
        seeds: list[CrawlUrl],
        budget: CrawlBudget,
        *,
        allowed_origins: set[str] | None = None,
        min_delay_seconds: float = 1.0,
        user_agent: str = "SwahiliLinguisticIntelligence",
    ) -> CrawlJob:
        if not seeds:
            raise ValueError("At least one seed URL is required")
        if min_delay_seconds < 0:
            raise ValueError("Minimum crawl delay cannot be negative")
        origins = allowed_origins or {seed.origin for seed in seeds}
        if any(seed.origin not in origins for seed in seeds):
            raise ValueError("Every seed origin must be allowed")
        return cls(
            id=str(uuid4()),
            seeds=tuple(seed.value for seed in seeds),
            allowed_origins=frozenset(origins),
            budget=budget,
            min_delay_seconds=min_delay_seconds,
            user_agent=user_agent,
        )

    def start(self, now: datetime | None = None) -> None:
        if self.status not in {CrawlStatus.CREATED, CrawlStatus.INTERRUPTED}:
            raise ValueError(f"Cannot start crawl from {self.status.value}")
        self.status = CrawlStatus.RUNNING
        self.termination_reason = None
        self.updated_at = now or datetime.now(timezone.utc)

    def record_completed(self) -> None:
        self.pages_attempted += 1
        self.pages_completed += 1

    def record_failed(self) -> None:
        self.pages_attempted += 1
        self.pages_failed += 1

    def record_skipped(self) -> None:
        self.pages_skipped += 1

    def page_budget_available(self) -> bool:
        return self.pages_attempted < self.budget.max_pages

    def failure_budget_available(self) -> bool:
        return self.pages_failed < self.budget.max_failures

    def finish(self, reason: TerminationReason) -> None:
        if self.status != CrawlStatus.RUNNING:
            raise ValueError("Only a running crawl can terminate")
        self.status = CrawlStatus.COMPLETED
        self.termination_reason = reason

    def interrupt(self) -> None:
        if self.status != CrawlStatus.RUNNING:
            raise ValueError("Only a running crawl can be interrupted")
        self.status = CrawlStatus.INTERRUPTED
        self.termination_reason = TerminationReason.INTERRUPTED

    def stop(self) -> None:
        if self.status not in {CrawlStatus.CREATED, CrawlStatus.RUNNING, CrawlStatus.INTERRUPTED}:
            raise ValueError("Completed crawl cannot be stopped")
        self.status = CrawlStatus.STOPPED
        self.termination_reason = TerminationReason.MANUALLY_STOPPED


@dataclass(frozen=True)
class RobotsDecision:
    allowed: bool
    reason: str
    crawl_delay: float | None = None


@dataclass(frozen=True)
class RobotsPolicy:
    origin: str
    status: str
    groups: tuple[tuple[tuple[str, ...], tuple[tuple[str, bool], ...]], ...] = ()
    crawl_delay: float | None = None

    def evaluate(self, url: CrawlUrl, user_agent: str) -> RobotsDecision:
        if self.status == "missing":
            return RobotsDecision(True, "robots_missing_allow", self.crawl_delay)
        if self.status in {"unreachable", "malformed"} or not self.groups:
            return RobotsDecision(False, f"robots_{self.status}_deny", self.crawl_delay)
        agent = user_agent.lower()
        matching = [
            group
            for group in self.groups
            if any(candidate == "*" or candidate in agent for candidate in group[0])
        ]
        specific = [group for group in matching if any(candidate != "*" for candidate in group[0])]
        rules = [rule for group in (specific or matching) for rule in group[1]]
        path = urlsplit(url.value).path or "/"
        matches = [(pattern, allow) for pattern, allow in rules if _robots_match(pattern, path)]
        if not matches:
            return RobotsDecision(True, "robots_allowed", self.crawl_delay)
        longest = max(len(pattern.rstrip("$")) for pattern, _ in matches)
        allowed = any(allow for pattern, allow in matches if len(pattern.rstrip("$")) == longest)
        return RobotsDecision(
            allowed,
            "robots_allowed" if allowed else "robots_disallowed",
            self.crawl_delay,
        )


def _robots_match(pattern: str, path: str) -> bool:
    """Match RFC 9309 path wildcards and optional end anchors."""
    import re

    anchored = pattern.endswith("$")
    value = pattern[:-1] if anchored else pattern
    expression = re.escape(value).replace(r"\*", ".*")
    return re.match(f"^{expression}{'$' if anchored else ''}", path) is not None


@dataclass(frozen=True)
class RatePolicy:
    minimum_delay: float

    def required_wait(
        self, *, last_request_at: float | None, now: float, robots_delay: float | None
    ) -> float:
        delay = max(self.minimum_delay, robots_delay or 0.0)
        return 0.0 if last_request_at is None else max(0.0, delay - (now - last_request_at))


class CrawlRepository(ABC):
    """Persistence boundary for a crawl job aggregate and its frontier."""

    @abstractmethod
    def save_job(self, job: CrawlJob) -> None: ...

    @abstractmethod
    def get_job(self, job_id: str) -> CrawlJob | None: ...

    @abstractmethod
    def add_entry(self, entry: FrontierEntry) -> bool: ...

    @abstractmethod
    def save_entry(self, entry: FrontierEntry) -> None: ...

    @abstractmethod
    def checkpoint(self, job: CrawlJob, entry: FrontierEntry) -> None: ...

    @abstractmethod
    def next_queued(self, job_id: str) -> FrontierEntry | None: ...

    @abstractmethod
    def list_entries(self, job_id: str) -> list[FrontierEntry]: ...

    @abstractmethod
    def recover_processing(self, job_id: str) -> int: ...

    @abstractmethod
    def count_attempted_for_origin(self, job_id: str, origin: str) -> int: ...
