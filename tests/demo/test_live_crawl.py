from __future__ import annotations

import io
from datetime import datetime, timezone

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from src.acquisition.pipeline import AcquisitionPipeline
from src.acquisition.storage import CorpusStore
from src.application.services.url_analyzer import FetchResult
from src.crawl.application import (
    CrawlOrchestrator,
    OriginRateScheduler,
    RobotsPolicyService,
    RobotsResource,
)
from src.crawl.infrastructure import SqlAlchemyCrawlRepository
from src.demo.live_crawl import LiveCrawlDemo, SystemBrowserViewer, TracedWebAcquisition
from src.infrastructure.database.models import Base

SITES = (
    ("One", "https://one.example/", "first"),
    ("Two", "https://two.example/", "second"),
    ("Three", "https://three.example/", "third"),
)
HTML = """
<html lang="sw"><head><title>Habari</title></head><body><article>
<p>Serikali ya Tanzania imesema kwamba wananchi watapata huduma na elimu bora.</p>
<p>Watu wengi wameendelea kufanya kazi katika jamii kwa maendeleo ya nchi.</p>
<p>Habari hizi zilitolewa leo katika mji mkuu baada ya mkutano wa viongozi.</p>
</article></body></html>
"""


class FakeAnalyzer:
    def __init__(self, fail: bool = False, html: str = HTML):
        self.fail = fail
        self.html = html

    def fetch_result(self, url, **_options):
        if self.fail:
            return None
        return FetchResult(url, url, 200, "text/html", self.html, datetime.now(timezone.utc))


class AllowSafety:
    def is_safe(self, _url):
        return True


class AllowRobots:
    def retrieve(self, _origin):
        return RobotsResource("available", "User-agent: *\nAllow: /")


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def monotonic(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


class FakeBrowser:
    name = "Firefox"
    available = True
    limitation = None

    def __init__(self):
        self.urls = []

    def show(self, url):
        self.urls.append(url)
        return True


def make_demo(tmp_path, *, fail=False, delay=0, html=HTML, max_depth=0):
    engine = create_engine("sqlite:///:memory:")
    event.listen(
        engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON")
    )
    Base.metadata.create_all(engine)
    repository = SqlAlchemyCrawlRepository(Session(engine))
    analyzer = FakeAnalyzer(fail, html)
    acquisition = TracedWebAcquisition(
        analyzer, AcquisitionPipeline(CorpusStore(tmp_path / "corpus"))
    )
    orchestrator = CrawlOrchestrator(
        repository,
        AllowSafety(),
        RobotsPolicyService(AllowRobots()),
        OriginRateScheduler(FakeClock(), 2),
        acquisition,
    )
    browser = FakeBrowser()
    pauses = []
    demo = LiveCrawlDemo(
        orchestrator,
        repository,
        acquisition,
        browser,
        io.StringIO(),
        delay,
        1,
        max_depth,
        pauses.append,
    )
    return demo, browser, pauses


def test_browser_invocation_abstraction(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "src.demo.live_crawl.subprocess.Popen", lambda args, **kwargs: calls.append((args, kwargs))
    )
    viewer = SystemBrowserViewer(("firefox",), "Firefox")

    assert viewer.show("https://example.org/")
    assert calls[0][0] == ("firefox", "https://example.org/")


def test_browser_unavailable_fallback(monkeypatch):
    monkeypatch.setattr("src.demo.live_crawl.shutil.which", lambda _name: None)

    viewer = SystemBrowserViewer.detect()

    assert not viewer.available
    assert "No firefox" in viewer.limitation


def test_three_sites_progress_sequentially_and_delay_can_be_disabled(tmp_path):
    demo, browser, pauses = make_demo(tmp_path)

    summaries = demo.run(SITES)

    assert [item.name for item in summaries] == ["One", "Two", "Three"]
    assert [item.completed for item in summaries] == [1, 1, 1]
    assert browser.urls == [site[1] for site in SITES]
    assert pauses == []
    terminal = demo.output.getvalue()
    assert "[ROBOTS]" in terminal
    assert "[PAGE INSPECTION]" in terminal
    assert "Sites processed: 3" in terminal


def test_crawl_failures_are_presented_without_crashing_later_sites(tmp_path):
    demo, browser, _ = make_demo(tmp_path, fail=True)

    summaries = demo.run(SITES)

    assert [item.failed for item in summaries] == [1, 1, 1]
    assert len(browser.urls) == 3
    assert "Network acquisition failed" in demo.output.getvalue()


def test_candidate_examples_are_bounded_and_render_decisions(tmp_path):
    html = HTML.replace(
        "</article>",
        "</article><a href='/ar/article'>Arabic</a>"
        "<a href='/sw/news/2026/08/report'>Report</a>"
        "<a href='/category/world'>World</a>"
        "<a href='/image.jpg'>Image</a>",
    )
    demo, _, _ = make_demo(tmp_path, html=html, max_depth=1)

    summaries = demo.run(SITES)

    terminal = demo.output.getvalue()
    assert "[CANDIDATES]" in terminal
    assert "Reason: competing_language_path" in terminal
    assert "Priority: HIGH" in terminal
    assert "Candidate examples limited to 3" in terminal
    assert all(item.skipped_before_acquisition == 2 for item in summaries)


def test_structured_static_rejection_is_educational(tmp_path):
    demo, _, _ = make_demo(tmp_path, html="<html><main><p>Short.</p></main></html>")

    summaries = demo.run(SITES)

    terminal = demo.output.getvalue()
    assert "Status: REJECTED" in terminal
    assert "Stage: static_extraction" in terminal
    assert "Reason: insufficient_static_content" in terminal
    assert all(item.extraction_rejections == 1 for item in summaries)
