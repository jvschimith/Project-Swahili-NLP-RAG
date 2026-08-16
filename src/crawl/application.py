"""Application services and ports for responsible crawl orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from urllib.parse import urljoin

from .domain import (
    CrawlBudget,
    CrawlJob,
    CrawlRepository,
    CrawlStatus,
    CrawlUrl,
    FrontierEntry,
    FrontierState,
    RatePolicy,
    RobotsDecision,
    RobotsPolicy,
    SkipReason,
    TerminationReason,
)


@dataclass(frozen=True)
class RobotsResource:
    status: str
    text: str | None = None


@dataclass(frozen=True)
class AcquisitionOutcome:
    acquired: bool
    final_url: str
    html: str | None = None
    discovered_links: tuple[str, ...] = ()
    artifact_id: str | None = None
    reason: str | None = None


class UrlSafetyPort(Protocol):
    def is_safe(self, url: str) -> bool: ...


class RobotsRetrieverPort(Protocol):
    def retrieve(self, origin: str) -> RobotsResource: ...


class PageAcquisitionPort(Protocol):
    def acquire(self, url: str) -> AcquisitionOutcome: ...


class ClockPort(Protocol):
    def monotonic(self) -> float: ...

    def sleep(self, seconds: float) -> None: ...


class RobotsPolicyService:
    """Load and cache one deterministic robots policy per origin and crawl lifecycle."""

    def __init__(self, retriever: RobotsRetrieverPort):
        self.retriever = retriever
        self._cache: dict[str, RobotsPolicy] = {}

    def decision(self, url: CrawlUrl, user_agent: str) -> RobotsDecision:
        policy = self._cache.get(url.origin)
        if policy is None:
            resource = self.retriever.retrieve(url.origin)
            groups: tuple[tuple[tuple[str, ...], tuple[tuple[str, bool], ...]], ...] = ()
            delay = None
            status = resource.status
            if status == "available" and resource.text is not None:
                try:
                    groups, delays = _parse_robots(resource.text)
                    applicable = [
                        value
                        for agents, value in delays
                        if any(agent == "*" or agent in user_agent.lower() for agent in agents)
                    ]
                    delay = applicable[0] if applicable else None
                except ValueError:
                    status = "malformed"
                    groups = ()
            policy = RobotsPolicy(url.origin, status, groups, delay)
            self._cache[url.origin] = policy
        return policy.evaluate(url, user_agent)

    @property
    def cache_size(self) -> int:
        return len(self._cache)


def _parse_robots(
    text: str,
) -> tuple[
    tuple[tuple[tuple[str, ...], tuple[tuple[str, bool], ...]], ...],
    tuple[tuple[tuple[str, ...], float], ...],
]:
    groups: list[tuple[tuple[str, ...], tuple[tuple[str, bool], ...]]] = []
    delays: list[tuple[tuple[str, ...], float]] = []
    agents: list[str] = []
    rules: list[tuple[str, bool]] = []
    delay: float | None = None

    def finish() -> None:
        nonlocal agents, rules, delay
        if agents:
            groups.append((tuple(agents), tuple(rules)))
            if delay is not None:
                delays.append((tuple(agents), delay))
        agents, rules, delay = [], [], None

    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if ":" not in line:
            raise ValueError("Malformed robots directive")
        name, value = (part.strip() for part in line.split(":", 1))
        directive = name.lower()
        if directive == "user-agent":
            if rules or delay is not None:
                finish()
            if not value:
                raise ValueError("Empty robots user-agent")
            agents.append(value.lower())
        elif directive in {"allow", "disallow"}:
            if not agents:
                raise ValueError("Robots rule has no user-agent")
            if value:
                rules.append((value, directive == "allow"))
        elif directive == "crawl-delay" and agents:
            try:
                delay = max(0.0, float(value))
            except ValueError as error:
                raise ValueError("Invalid robots crawl-delay") from error
    finish()
    if not groups:
        raise ValueError("Robots policy has no user-agent groups")
    return tuple(groups), tuple(delays)


class OriginRateScheduler:
    """Enforce independent origin pacing through an injectable clock."""

    def __init__(self, clock: ClockPort, minimum_delay: float):
        self.clock = clock
        self.policy = RatePolicy(minimum_delay)
        self._last_request: dict[str, float] = {}

    def wait(
        self,
        origin: str,
        robots_delay: float | None = None,
        minimum_delay: float | None = None,
    ) -> float:
        now = self.clock.monotonic()
        policy = self.policy if minimum_delay is None else RatePolicy(minimum_delay)
        required = policy.required_wait(
            last_request_at=self._last_request.get(origin),
            now=now,
            robots_delay=robots_delay,
        )
        if required:
            self.clock.sleep(required)
        self._last_request[origin] = self.clock.monotonic()
        return required


@dataclass(frozen=True)
class CrawlSnapshot:
    job_id: str
    status: str
    termination_reason: str | None
    discovered: int
    queued: int
    processing: int
    completed: int
    skipped: int
    failed: int
    pages_attempted: int
    pages_completed: int
    pages_failed: int
    page_limit: int
    failure_limit: int
    max_depth: int
    skip_reasons: dict[str, int] = field(default_factory=dict)


class CrawlOrchestrator:
    """Coordinate policy-controlled crawling and delegate resource acquisition."""

    def __init__(
        self,
        repository: CrawlRepository,
        safety: UrlSafetyPort,
        robots: RobotsPolicyService,
        scheduler: OriginRateScheduler,
        acquisition: PageAcquisitionPort,
    ):
        self.repository = repository
        self.safety = safety
        self.robots = robots
        self.scheduler = scheduler
        self.acquisition = acquisition

    def start_crawl(
        self,
        seed_urls: list[str],
        budget: CrawlBudget,
        *,
        allowed_origins: set[str] | None = None,
        min_delay_seconds: float = 1.0,
    ) -> CrawlJob:
        seeds = [CrawlUrl.parse(url) for url in seed_urls]
        if any(not self.safety.is_safe(seed.value) for seed in seeds):
            raise ValueError("Seed URL failed the public network safety policy")
        job = CrawlJob.create(
            seeds,
            budget,
            allowed_origins=allowed_origins,
            min_delay_seconds=min_delay_seconds,
        )
        self.repository.save_job(job)
        for seed in seeds:
            entry = FrontierEntry(None, job.id, seed, 0)
            entry.transition(FrontierState.QUEUED)
            self.repository.add_entry(entry)
        job.start()
        self.repository.save_job(job)
        return job

    def resume_crawl(self, job_id: str) -> CrawlJob:
        job = self._require_job(job_id)
        if job.status != CrawlStatus.INTERRUPTED:
            raise ValueError("Only an interrupted crawl can resume")
        self.repository.recover_processing(job_id)
        job.start()
        self.repository.save_job(job)
        return job

    def interrupt_crawl(self, job_id: str) -> CrawlJob:
        job = self._require_job(job_id)
        job.interrupt()
        self.repository.save_job(job)
        return job

    def stop_crawl(self, job_id: str) -> CrawlJob:
        job = self._require_job(job_id)
        job.stop()
        self.repository.save_job(job)
        return job

    def run(self, job_id: str, *, max_steps: int | None = None) -> CrawlSnapshot:
        steps = 0
        while max_steps is None or steps < max_steps:
            job = self._require_job(job_id)
            if job.status != CrawlStatus.RUNNING:
                break
            if not job.page_budget_available():
                job.finish(TerminationReason.PAGE_BUDGET_EXHAUSTED)
                self.repository.save_job(job)
                break
            if not job.failure_budget_available():
                job.finish(TerminationReason.FAILURE_BUDGET_EXHAUSTED)
                self.repository.save_job(job)
                break
            entry = self.repository.next_queued(job_id)
            if entry is None:
                job.finish(TerminationReason.FRONTIER_EXHAUSTED)
                self.repository.save_job(job)
                break
            self._process(job, entry)
            steps += 1
        return self.inspect_crawl(job_id)

    def _process(self, job: CrawlJob, entry: FrontierEntry) -> None:
        entry.transition(FrontierState.PROCESSING)
        self.repository.save_entry(entry)
        if entry.url.origin not in job.allowed_origins:
            self._skip(job, entry, SkipReason.EXTERNAL_ORIGIN)
            return
        if entry.depth > job.budget.max_depth:
            self._skip(job, entry, SkipReason.DEPTH_LIMIT)
            return
        if not self.safety.is_safe(entry.url.value):
            self._skip(job, entry, SkipReason.UNSAFE_URL)
            return
        if (
            self.repository.count_attempted_for_origin(job.id, entry.url.origin)
            >= job.budget.per_origin_pages
        ):
            self._skip(job, entry, SkipReason.PER_ORIGIN_LIMIT)
            return
        robots = self.robots.decision(entry.url, job.user_agent)
        if not robots.allowed:
            self._skip(job, entry, SkipReason.ROBOTS_DENIED, robots.reason)
            return
        self.scheduler.wait(entry.url.origin, robots.crawl_delay, job.min_delay_seconds)
        outcome = self.acquisition.acquire(entry.url.value)
        if not outcome.acquired:
            entry.transition(FrontierState.FAILED, reason=outcome.reason or "acquisition_failed")
            job.record_failed()
            self.repository.checkpoint(job, entry)
            return
        entry.transition(FrontierState.COMPLETED)
        job.record_completed()
        self.repository.checkpoint(job, entry)
        self._discover(job, entry, outcome.discovered_links)
        self.repository.save_job(job)

    def _discover(self, job: CrawlJob, parent: FrontierEntry, links: tuple[str, ...]) -> None:
        for raw_link in links:
            try:
                candidate = CrawlUrl.parse(urljoin(parent.url.value, raw_link))
            except ValueError:
                continue
            child = FrontierEntry(
                None, job.id, candidate, parent.depth + 1, parent_url=parent.url.value
            )
            if candidate.origin not in job.allowed_origins:
                child.transition(FrontierState.SKIPPED, reason=SkipReason.EXTERNAL_ORIGIN.value)
                if self.repository.add_entry(child):
                    job.record_skipped()
                continue
            if child.depth > job.budget.max_depth:
                child.transition(FrontierState.SKIPPED, reason=SkipReason.DEPTH_LIMIT.value)
                if self.repository.add_entry(child):
                    job.record_skipped()
                continue
            if not self.safety.is_safe(candidate.value):
                child.transition(FrontierState.SKIPPED, reason=SkipReason.UNSAFE_URL.value)
                if self.repository.add_entry(child):
                    job.record_skipped()
                continue
            child.transition(FrontierState.QUEUED)
            self.repository.add_entry(child)

    def _skip(
        self,
        job: CrawlJob,
        entry: FrontierEntry,
        reason: SkipReason,
        detail: str | None = None,
    ) -> None:
        entry.transition(FrontierState.SKIPPED, reason=detail or reason.value)
        job.record_skipped()
        self.repository.checkpoint(job, entry)

    def inspect_crawl(self, job_id: str) -> CrawlSnapshot:
        job = self._require_job(job_id)
        entries = self.repository.list_entries(job_id)
        counts = {state: 0 for state in FrontierState}
        reasons: dict[str, int] = {}
        for entry in entries:
            counts[entry.state] += 1
            if entry.skip_reason:
                reasons[entry.skip_reason] = reasons.get(entry.skip_reason, 0) + 1
        return CrawlSnapshot(
            job.id,
            job.status.value,
            job.termination_reason.value if job.termination_reason else None,
            len(entries),
            counts[FrontierState.QUEUED],
            counts[FrontierState.PROCESSING],
            counts[FrontierState.COMPLETED],
            counts[FrontierState.SKIPPED],
            counts[FrontierState.FAILED],
            job.pages_attempted,
            job.pages_completed,
            job.pages_failed,
            job.budget.max_pages,
            job.budget.max_failures,
            job.budget.max_depth,
            reasons,
        )

    def _require_job(self, job_id: str) -> CrawlJob:
        job = self.repository.get_job(job_id)
        if job is None:
            raise ValueError(f"Crawl job not found: {job_id}")
        return job
