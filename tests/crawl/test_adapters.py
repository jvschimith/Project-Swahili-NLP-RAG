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
    assert first.artifact_id == second.artifact_id
    assert len(store.list_manifest()) == 1
    assert analyzer.calls == [(url, {}), (url, {})]
