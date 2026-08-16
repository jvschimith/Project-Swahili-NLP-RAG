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
    def __init__(self, fail: bool = False):
        self.fail = fail

    def fetch_result(self, url, **_options):
        if self.fail:
            return None
        return FetchResult(url, url, 200, "text/html", HTML, datetime.now(timezone.utc))


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


def make_demo(tmp_path, *, fail=False, delay=0):
    engine = create_engine("sqlite:///:memory:")
    event.listen(
        engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON")
    )
    Base.metadata.create_all(engine)
    repository = SqlAlchemyCrawlRepository(Session(engine))
    analyzer = FakeAnalyzer(fail)
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
        0,
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
