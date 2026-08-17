from datetime import datetime, timezone

import pytest

from src.crawl.domain import (
    CandidateEvidence,
    CandidatePriority,
    CrawlBudget,
    CrawlJob,
    CrawlStatus,
    CrawlUrl,
    FrontierEntry,
    FrontierState,
    LinkEligibilityPolicy,
    RatePolicy,
    ResourceKind,
    TerminationReason,
)


@pytest.mark.parametrize(
    ("url", "eligible", "priority", "kind", "evidence"),
    [
        (
            "https://example.org/sw/news/2026/08/report",
            True,
            CandidatePriority.HIGH,
            ResourceKind.ARTICLE,
            CandidateEvidence.EXPECTED_LANGUAGE_PATH,
        ),
        ("https://example.org/report", True, CandidatePriority.NORMAL, ResourceKind.UNKNOWN, None),
        (
            "https://example.org/sw/topic",
            True,
            CandidatePriority.NORMAL,
            ResourceKind.UNKNOWN,
            CandidateEvidence.EXPECTED_LANGUAGE_PATH,
        ),
        (
            "https://example.org/ar/article",
            False,
            CandidatePriority.LOW,
            ResourceKind.UNKNOWN,
            CandidateEvidence.COMPETING_LANGUAGE_PATH,
        ),
        (
            "https://example.org/category/world",
            True,
            CandidatePriority.LOW,
            ResourceKind.SECTION,
            CandidateEvidence.CATEGORY_LIKE_PATH,
        ),
        (
            "https://example.org/video/report",
            True,
            CandidatePriority.LOW,
            ResourceKind.VIDEO,
            CandidateEvidence.VIDEO_LIKE_PATH,
        ),
        (
            "https://example.org/embed/player/Article/123?type=video",
            True,
            CandidatePriority.LOW,
            ResourceKind.VIDEO,
            CandidateEvidence.VIDEO_LIKE_PATH,
        ),
        (
            "https://example.org/sw/vidio-zetu/s-123",
            True,
            CandidatePriority.LOW,
            ResourceKind.VIDEO,
            CandidateEvidence.VIDEO_LIKE_PATH,
        ),
        (
            "https://example.org/sw/sauti-zetu/s-123",
            True,
            CandidatePriority.LOW,
            ResourceKind.AUDIO,
            CandidateEvidence.AUDIO_LIKE_PATH,
        ),
        (
            "https://example.org/sw/editorial-title/a-123456",
            True,
            CandidatePriority.HIGH,
            ResourceKind.ARTICLE,
            CandidateEvidence.ARTICLE_LIKE_PATH,
        ),
        (
            "https://example.org/assets/report.pdf",
            False,
            CandidatePriority.LOW,
            ResourceKind.UNSUPPORTED_FILE,
            CandidateEvidence.UNSUPPORTED_RESOURCE,
        ),
    ],
)
def test_link_eligibility_is_explainable_and_conservative(url, eligible, priority, kind, evidence):
    decision = LinkEligibilityPolicy.evaluate(CrawlUrl.parse(url))

    assert decision.eligible is eligible
    assert decision.priority == priority
    assert decision.resource_kind == kind
    if evidence is not None:
        assert evidence in decision.evidence


NOW = datetime(2026, 8, 15, tzinfo=timezone.utc)


def test_crawl_url_is_canonical_and_rejects_unsupported_identity():
    url = CrawlUrl.parse("HTTPS://Example.COM:443/a?utm_source=x&id=2#part")
    assert url.value == "https://example.com/a?id=2"
    assert url.origin == "https://example.com"
    with pytest.raises(ValueError):
        CrawlUrl.parse("file:///etc/passwd")
    with pytest.raises(ValueError):
        CrawlUrl.parse("https://user:secret@example.com/")


def test_budget_validates_real_bounds():
    assert CrawlBudget(5, 2, 1, 3).max_depth == 2
    with pytest.raises(ValueError):
        CrawlBudget(0, 1, 1, 1)
    with pytest.raises(ValueError):
        CrawlBudget(2, 1, 1, 3)


def test_frontier_state_machine_enforces_terminal_states_and_recovery():
    entry = FrontierEntry(None, "job", CrawlUrl.parse("https://example.com/a"), 0)
    entry.transition(FrontierState.QUEUED, now=NOW)
    entry.transition(FrontierState.PROCESSING, now=NOW)
    assert entry.attempts == 1
    entry.transition(FrontierState.QUEUED, now=NOW)
    entry.transition(FrontierState.PROCESSING, now=NOW)
    entry.transition(FrontierState.COMPLETED, now=NOW)
    assert entry.attempts == 2
    with pytest.raises(ValueError, match="Forbidden"):
        entry.transition(FrontierState.QUEUED)


def test_job_lifecycle_and_budgets_are_explicit():
    job = CrawlJob.create([CrawlUrl.parse("https://example.com")], CrawlBudget(2, 1, 1, 2))
    job.start(NOW)
    job.record_completed()
    assert job.page_budget_available()
    job.record_failed()
    assert not job.page_budget_available()
    assert not job.failure_budget_available()
    job.finish(TerminationReason.PAGE_BUDGET_EXHAUSTED)
    assert job.status == CrawlStatus.COMPLETED
    with pytest.raises(ValueError):
        job.start()


def test_rate_policy_uses_stricter_minimum_or_robots_delay():
    policy = RatePolicy(2.0)
    assert policy.required_wait(last_request_at=None, now=10, robots_delay=5) == 0
    assert policy.required_wait(last_request_at=10, now=11, robots_delay=None) == 1
    assert policy.required_wait(last_request_at=10, now=11, robots_delay=4) == 3
