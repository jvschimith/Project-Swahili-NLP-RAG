from datetime import datetime, timezone
from pathlib import Path

from src.acquisition.pipeline import AcquisitionPipeline
from src.acquisition.storage import CorpusStore
from src.application.services.url_analyzer import FetchResult
from src.crawl.infrastructure import SafeRobotsRetriever, WebAcquisitionAdapter

FIXTURES = Path(__file__).parents[1] / "fixtures" / "acquisition"


class FakeAnalyzer:
    def __init__(self, result: FetchResult):
        self.result = result
        self.calls: list[tuple[str, dict[str, object]]] = []

    def fetch_result(self, url: str, **kwargs):
        self.calls.append((url, kwargs))
        return self.result


def fetched(url: str, html: str, status: int = 200) -> FetchResult:
    return FetchResult(
        url,
        url,
        status,
        "text/html",
        html,
        datetime(2026, 8, 15, tzinfo=timezone.utc),
    )


def test_robots_retrieval_uses_safe_fetch_boundary_and_distinguishes_missing():
    analyzer = FakeAnalyzer(fetched("https://example.com/robots.txt", "", 404))
    resource = SafeRobotsRetriever(analyzer).retrieve("https://example.com")

    assert resource.status == "missing"
    url, options = analyzer.calls[0]
    assert url == "https://example.com/robots.txt"
    assert options["accepted_status_codes"] == frozenset({404, 410})


def test_acquisition_adapter_delegates_storage_deduplication(tmp_path):
    html = (FIXTURES / "semantic_sw.html").read_text(encoding="utf-8")
    url = "https://habari.example/elimu"
    analyzer = FakeAnalyzer(fetched(url, html))
    store = CorpusStore(tmp_path / "corpus")
    adapter = WebAcquisitionAdapter(analyzer, AcquisitionPipeline(store))

    first = adapter.acquire(url)
    second = adapter.acquire(url)

    assert first.acquired and second.acquired
    assert first.artifact_created and not second.artifact_created
    assert first.reason == "accepted"
    assert second.reason == "duplicate_canonical_url"
    assert second.duplicate_reason == "canonical_url"
    assert dict(second.details)["language_evidence_score"] > 0
    assert first.artifact_id == second.artifact_id
    assert len(store.list_manifest()) == 1
    assert analyzer.calls == [(url, {}), (url, {})]


def test_acquisition_adapter_preserves_rejection_stage_and_evidence(tmp_path):
    html = (FIXTURES / "english_fake_sw.html").read_text(encoding="utf-8")
    url = "https://example.org/english-article"
    adapter = WebAcquisitionAdapter(
        FakeAnalyzer(fetched(url, html)), AcquisitionPipeline(CorpusStore(tmp_path))
    )

    outcome = adapter.acquire(url)

    assert not outcome.acquired
    assert outcome.stage == "language_validation"
    assert outcome.reason == "likely_non_swahili"
    details = dict(outcome.details)
    assert details["html_language"] == "sw"
    assert details["paragraph_count"] >= 2
    assert details["language_evidence_score"] >= 0


def test_acquisition_adapter_reports_network_failure_without_generic_exception(tmp_path):
    class FailedAnalyzer:
        def fetch_result(self, _url):
            return None

    outcome = WebAcquisitionAdapter(
        FailedAnalyzer(), AcquisitionPipeline(CorpusStore(tmp_path))
    ).acquire("https://example.org/sw/news/article")

    assert not outcome.acquired
    assert outcome.stage == "fetch"
    assert outcome.reason == "network_failure"
