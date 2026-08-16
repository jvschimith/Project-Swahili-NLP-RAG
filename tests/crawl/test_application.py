from __future__ import annotations

import pytest

from src.crawl.application import (
    AcquisitionOutcome,
    CrawlOrchestrator,
    OriginRateScheduler,
    RobotsPolicyService,
    RobotsResource,
)
from src.crawl.domain import (
    CrawlBudget,
    CrawlJob,
    CrawlRepository,
    CrawlUrl,
    FrontierEntry,
    FrontierState,
)


class MemoryRepository(CrawlRepository):
    def __init__(self):
        self.jobs: dict[str, CrawlJob] = {}
        self.entries: dict[str, list[FrontierEntry]] = {}
        self.next_id = 1

    def save_job(self, job):
        self.jobs[job.id] = job

    def get_job(self, job_id):
        return self.jobs.get(job_id)

    def add_entry(self, entry):
        bucket = self.entries.setdefault(entry.job_id, [])
        if any(item.url == entry.url for item in bucket):
            return False
        entry.id = self.next_id
        self.next_id += 1
        bucket.append(entry)
        return True

    def save_entry(self, entry):
        return None

    def checkpoint(self, job, entry):
        self.save_job(job)
        self.save_entry(entry)

    def next_queued(self, job_id):
        items = [
            item for item in self.entries.get(job_id, []) if item.state == FrontierState.QUEUED
        ]
        return min(items, key=lambda item: (item.depth, item.id or 0), default=None)

    def list_entries(self, job_id):
        return list(self.entries.get(job_id, []))

    def recover_processing(self, job_id):
        count = 0
        for entry in self.entries.get(job_id, []):
            if entry.state == FrontierState.PROCESSING:
                entry.transition(FrontierState.QUEUED)
                count += 1
        return count

    def count_attempted_for_origin(self, job_id, origin):
        return sum(
            entry.state in {FrontierState.COMPLETED, FrontierState.FAILED}
            and entry.url.origin == origin
            for entry in self.entries.get(job_id, [])
        )


class FakeSafety:
    def is_safe(self, url):
        return "unsafe" not in url and not url.startswith("http://127.")


class FakeRobotsRetriever:
    def __init__(self, resources=None):
        self.resources = resources or {}
        self.calls = []

    def retrieve(self, origin):
        self.calls.append(origin)
        return self.resources.get(origin, RobotsResource("missing"))


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class FakeAcquisition:
    def __init__(self, pages):
        self.pages = pages
        self.calls = []

    def acquire(self, url):
        self.calls.append(url)
        return self.pages.get(url, AcquisitionOutcome(False, url, reason="missing_fixture"))


def build(pages, robots=None, minimum_delay=1.0):
    repository = MemoryRepository()
    retriever = FakeRobotsRetriever(robots)
    clock = FakeClock()
    acquisition = FakeAcquisition(pages)
    orchestrator = CrawlOrchestrator(
        repository,
        FakeSafety(),
        RobotsPolicyService(retriever),
        OriginRateScheduler(clock, minimum_delay),
        acquisition,
    )
    return orchestrator, repository, retriever, clock, acquisition


def test_robots_allowed_disallowed_missing_unreachable_and_cached():
    retriever = FakeRobotsRetriever(
        {
            "https://example.com": RobotsResource(
                "available", "User-agent: *\nDisallow: /private\nAllow: /private/public\n"
            ),
            "https://down.example": RobotsResource("unreachable"),
            "https://bad.example": RobotsResource("malformed"),
        }
    )
    service = RobotsPolicyService(retriever)
    assert service.decision(CrawlUrl.parse("https://example.com/news"), "bot").allowed
    assert not service.decision(CrawlUrl.parse("https://example.com/private/x"), "bot").allowed
    assert service.decision(CrawlUrl.parse("https://example.com/private/public"), "bot").allowed
    assert service.decision(CrawlUrl.parse("https://missing.example/x"), "bot").allowed
    assert not service.decision(CrawlUrl.parse("https://down.example/x"), "bot").allowed
    assert not service.decision(CrawlUrl.parse("https://bad.example/x"), "bot").allowed
    assert retriever.calls.count("https://example.com") == 1


def test_scheduler_paces_same_origin_but_isolates_origins_without_real_sleep():
    clock = FakeClock()
    scheduler = OriginRateScheduler(clock, 2.0)
    assert scheduler.wait("https://one.example") == 0
    assert scheduler.wait("https://two.example") == 0
    assert scheduler.wait("https://one.example") == 2
    assert clock.sleeps == [2.0]


def test_bounded_orchestration_handles_cycles_duplicates_scope_robots_and_depth():
    pages = {
        "https://example.com/": AcquisitionOutcome(
            True,
            "https://example.com/",
            discovered_links=(
                "/a#part",
                "/a?utm_source=x",
                "/private",
                "https://outside.example/x",
                "mailto:test@example.com",
            ),
            artifact_id="one",
        ),
        "https://example.com/a": AcquisitionOutcome(
            True,
            "https://example.com/a",
            discovered_links=("/", "/deep"),
            artifact_id="two",
        ),
    }
    robots = {
        "https://example.com": RobotsResource(
            "available", "User-agent: *\nDisallow: /private\nCrawl-delay: 3\n"
        )
    }
    orchestrator, repository, _, clock, acquisition = build(pages, robots)
    job = orchestrator.start_crawl(
        ["https://example.com"], CrawlBudget(10, 1, 3, 10), min_delay_seconds=1
    )
    snapshot = orchestrator.run(job.id)
    assert snapshot.status == "completed"
    assert snapshot.termination_reason == "frontier_exhausted"
    assert snapshot.completed == 2
    assert snapshot.skipped == 3  # external origin, robots exclusion, depth
    assert acquisition.calls == ["https://example.com/", "https://example.com/a"]
    assert clock.sleeps == [3.0]
    urls = [entry.url.value for entry in repository.list_entries(job.id)]
    assert urls.count("https://example.com/a") == 1


def test_robots_denied_never_reaches_acquisition():
    robots = {"https://example.com": RobotsResource("available", "User-agent: *\nDisallow: /")}
    orchestrator, _, _, _, acquisition = build({}, robots)
    job = orchestrator.start_crawl(["https://example.com"], CrawlBudget(2, 1, 1, 2))
    snapshot = orchestrator.run(job.id)
    assert snapshot.skipped == 1
    assert acquisition.calls == []


def test_page_and_failure_budgets_terminate_explicitly():
    pages = {
        "https://example.com/": AcquisitionOutcome(
            True, "https://example.com/", discovered_links=("/a",)
        ),
        "https://example.com/a": AcquisitionOutcome(False, "https://example.com/a", reason="boom"),
    }
    orchestrator, _, _, _, _ = build(pages)
    page_job = orchestrator.start_crawl(["https://example.com"], CrawlBudget(1, 2, 2, 1))
    assert orchestrator.run(page_job.id).termination_reason == "page_budget_exhausted"

    orchestrator, _, _, _, _ = build(pages)
    failure_job = orchestrator.start_crawl(["https://example.com/a"], CrawlBudget(3, 2, 1, 3))
    assert orchestrator.run(failure_job.id).termination_reason == "failure_budget_exhausted"


def test_per_origin_attempt_cap_skips_remaining_candidates():
    pages = {
        "https://example.com/": AcquisitionOutcome(
            True, "https://example.com/", discovered_links=("/a", "/b")
        )
    }
    orchestrator, _, _, _, acquisition = build(pages)
    job = orchestrator.start_crawl(["https://example.com"], CrawlBudget(4, 2, 2, 1))

    result = orchestrator.run(job.id)

    assert result.skip_reasons == {"per_origin_limit": 2}
    assert acquisition.calls == ["https://example.com/"]


def test_interrupt_resume_recovers_processing_and_never_reacquires_completed():
    pages = {
        "https://example.com/": AcquisitionOutcome(
            True, "https://example.com/", discovered_links=("/a",)
        ),
        "https://example.com/a": AcquisitionOutcome(True, "https://example.com/a"),
    }
    orchestrator, repository, _, _, acquisition = build(pages)
    job = orchestrator.start_crawl(["https://example.com"], CrawlBudget(4, 2, 2, 4))
    orchestrator.run(job.id, max_steps=1)
    queued = repository.next_queued(job.id)
    assert queued is not None
    queued.transition(FrontierState.PROCESSING)
    orchestrator.interrupt_crawl(job.id)
    orchestrator.resume_crawl(job.id)
    result = orchestrator.run(job.id)
    assert result.completed == 2
    assert acquisition.calls.count("https://example.com/") == 1
    assert acquisition.calls.count("https://example.com/a") == 1


def test_invalid_resume_and_completed_to_queued_are_forbidden():
    orchestrator, repository, _, _, _ = build({})
    job = orchestrator.start_crawl(["https://example.com"], CrawlBudget(1, 0, 1, 1))
    with pytest.raises(ValueError):
        orchestrator.resume_crawl(job.id)
    entry = repository.next_queued(job.id)
    assert entry is not None
    entry.transition(FrontierState.PROCESSING)
    entry.transition(FrontierState.COMPLETED)
    with pytest.raises(ValueError):
        entry.transition(FrontierState.QUEUED)
