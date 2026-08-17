"""Observable, bounded three-site crawl demonstration.

Firefox (or a system-browser fallback) is presentation only. All network access and
corpus decisions continue through the existing crawl and acquisition components.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, TextIO

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from src.acquisition.inspector import PageInspectionResult, PageInspector
from src.acquisition.models import IngestionResult
from src.acquisition.pipeline import AcquisitionPipeline
from src.acquisition.storage import CorpusStore
from src.application.services.url_analyzer import FetchResult, URLNewsAnalyzer
from src.crawl.application import (
    AcquisitionOutcome,
    CrawlOrchestrator,
    OriginRateScheduler,
    RobotsPolicyService,
)
from src.crawl.domain import CrawlBudget, CrawlUrl, FrontierEntry
from src.crawl.infrastructure import (
    PublicUrlSafetyAdapter,
    SafeRobotsRetriever,
    SqlAlchemyCrawlRepository,
    SystemClock,
    observation_details,
)
from src.infrastructure.database.models import Base

DEMO_SITES = (
    ("VOA Swahili", "https://www.voaswahili.com/", "Public Swahili news and article pages."),
    ("DW Kiswahili", "https://www.dw.com/sw/", "Public Kiswahili news and features."),
    ("UN News Kiswahili", "https://news.un.org/sw/", "Public institutional news in Swahili."),
)
MAX_PAGES_PER_SITE = 3
MAX_DEPTH = 1


class BrowserViewer(Protocol):
    name: str
    limitation: str | None

    @property
    def available(self) -> bool: ...

    def show(self, url: str) -> bool: ...


@dataclass
class SystemBrowserViewer:
    """Open URLs for a human observer without reading or controlling the browser."""

    command: tuple[str, ...] | None
    name: str
    limitation: str | None = None

    @property
    def available(self) -> bool:
        return self.command is not None

    @classmethod
    def detect(cls) -> SystemBrowserViewer:
        candidates = (
            ("Firefox", ("firefox",)),
            ("Firefox (Windows via WSL)", ("firefox.exe",)),
            ("system browser (WSL)", ("wslview",)),
            ("system browser", ("xdg-open",)),
        )
        for name, command in candidates:
            if shutil.which(command[0]):
                return cls(command, name)
        return cls(
            None,
            "unavailable",
            "No firefox, firefox.exe, wslview, or xdg-open executable was found on PATH.",
        )

    def show(self, url: str) -> bool:
        if self.command is None:
            return False
        try:
            subprocess.Popen(
                (*self.command, url),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as error:
            self.limitation = f"{self.name} could not be invoked: {error}"
            return False
        return True


@dataclass
class AcquisitionTrace:
    requested_url: str
    fetched: FetchResult | None = None
    inspection: PageInspectionResult | None = None
    ingestion: IngestionResult | None = None


class TracedWebAcquisition:
    """Demo observability around, not instead of, deterministic acquisition."""

    def __init__(self, analyzer: URLNewsAnalyzer, pipeline: AcquisitionPipeline):
        self.analyzer = analyzer
        self.pipeline = pipeline
        self.traces: dict[str, AcquisitionTrace] = {}

    def acquire(self, url: str) -> AcquisitionOutcome:
        trace = AcquisitionTrace(url)
        self.traces[url] = trace
        fetched = self.analyzer.fetch_result(url)
        trace.fetched = fetched
        if fetched is None:
            return AcquisitionOutcome(False, url, reason="network_failure", stage="fetch")
        trace.inspection = PageInspector.inspect_html(fetched.final_url, fetched.html)
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
        trace.ingestion = result
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


@dataclass(frozen=True)
class SiteSummary:
    name: str
    origin: str
    job_id: str
    discovered: int
    attempted: int
    completed: int
    skipped: int
    failed: int
    robots_denied: int
    external_exclusions: int
    language_rejections: int
    duplicates: int
    artifacts: int
    termination: str | None
    eligible: int = 0
    skipped_before_acquisition: int = 0
    high_priority: int = 0
    low_priority: int = 0
    extraction_rejections: int = 0
    depth_exclusions: int = 0
    unsafe_exclusions: int = 0


@dataclass
class LiveCrawlDemo:
    orchestrator: CrawlOrchestrator
    repository: SqlAlchemyCrawlRepository
    acquisition: TracedWebAcquisition
    browser: BrowserViewer
    output: TextIO
    demo_delay: float = 2.0
    max_pages_per_site: int = MAX_PAGES_PER_SITE
    max_depth: int = MAX_DEPTH
    sleeper: Callable[[float], None] = time.sleep
    summaries: list[SiteSummary] = field(default_factory=list)
    candidate_example_limit: int = 3

    def say(self, message: str = "") -> None:
        print(message, file=self.output, flush=True)

    def run(self, sites: tuple[tuple[str, str, str], ...] = DEMO_SITES) -> list[SiteSummary]:
        if len(sites) != 3:
            raise ValueError("Live Crawl Demonstration v1 requires exactly three sites")
        self.say("=" * 60)
        self.say("Swahili Linguistic Intelligence\nLIVE CRAWL DEMONSTRATION")
        self.say("=" * 60)
        self.say(f"Browser visualization: {'ENABLED' if self.browser.available else 'UNAVAILABLE'}")
        self.say(f"Browser: {self.browser.name}")
        if self.browser.limitation:
            self.say(f"Environment limitation: {self.browser.limitation}")
        self.say("\nSelected sites (live compatibility and robots policy are rechecked per run):")
        for index, (name, url, reason) in enumerate(sites, 1):
            self.say(f"  {index}. {name} — {url} — {reason}")

        for index, site in enumerate(sites, 1):
            self._run_site(index, site)
        self._print_final()
        return self.summaries

    def _run_site(self, index: int, site: tuple[str, str, str]) -> None:
        name, seed, _ = site
        origin = CrawlUrl.parse(seed).origin
        job = self.orchestrator.start_crawl(
            [seed],
            CrawlBudget(
                self.max_pages_per_site,
                self.max_depth,
                self.max_pages_per_site,
                self.max_pages_per_site,
            ),
            allowed_origins={origin},
            min_delay_seconds=2.0,
        )
        self.say(f"\n{'=' * 60}\nSITE {index}/3: {name}\nOrigin: {origin}\nCrawl Job: {job.id}")
        page = 0
        while True:
            entry = self.repository.next_queued(job.id)
            if entry is None or page >= self.max_pages_per_site:
                snapshot = self.orchestrator.run(job.id, max_steps=0)
                if snapshot.status == "running":
                    snapshot = self.orchestrator.run(job.id)
                break
            page += 1
            before = self.orchestrator.inspect_crawl(job.id)
            self._print_before(entry, page, before)
            snapshot = self.orchestrator.run(job.id, max_steps=1)
            self._print_after(entry, snapshot)
            if self.demo_delay:
                self.sleeper(self.demo_delay)

        snapshot = self.orchestrator.inspect_crawl(job.id)
        entries = self.repository.list_entries(job.id)
        metrics = self._site_metrics(name, origin, job.id, snapshot, entries)
        self.summaries.append(metrics)
        self._print_site_summary(metrics)

    def _print_before(self, entry: FrontierEntry, page: int, snapshot) -> None:
        self.say(f"\nPAGE {page}/{self.max_pages_per_site}\n\nURL\n{entry.url.value}")
        self.say("\n[URL SAFETY]\n✓ supported HTTP(S)\n✓ no credentials\n✓ allowed origin")
        safe = self.orchestrator.safety.is_safe(entry.url.value)
        self.say(f"{'✓' if safe else '✗'} public destination")
        decision = self.orchestrator.robots.decision(
            entry.url, self.repository.get_job(entry.job_id).user_agent  # type: ignore[union-attr]
        )
        self.say(
            f"\n[ROBOTS]\n{'✓ allowed' if decision.allowed else '✗ denied'}"
            f"\nReason: {decision.reason}"
        )
        self.say(
            "\n[RATE POLICY]\nConfigured minimum: 2.0 seconds"
            f"\nrobots crawl delay: {decision.crawl_delay if decision.crawl_delay is not None else 'not specified'}"
            f"\nEffective pacing: {max(2.0, decision.crawl_delay or 0.0)} seconds"
        )
        self.say(
            f"\n[FRONTIER]\nDepth: {entry.depth} / {self.max_depth}\nQueued: {snapshot.queued}"
            f"\nCompleted: {snapshot.completed}\nSkipped: {snapshot.skipped}"
            f"\nFailed: {snapshot.failed}"
        )
        if self.browser.available:
            opened = self.browser.show(entry.url.value)
            self.say(
                f"\n[BROWSER]\n{'Opening page in ' + self.browser.name + '...' if opened else 'Browser invocation failed; crawl continues.'}"
            )
        else:
            self.say("\n[BROWSER]\nVisualization unavailable; deterministic crawl continues.")

    def _print_after(self, entry: FrontierEntry, snapshot) -> None:
        persisted = next(
            item for item in self.repository.list_entries(entry.job_id) if item.id == entry.id
        )
        trace = self.acquisition.traces.get(entry.url.value)
        if trace is None:
            self.say(
                f"\n[RESULT]\n{persisted.state.value.upper()}: {persisted.skip_reason or persisted.error}"
            )
        else:
            self._print_acquisition(trace)
        self._print_candidates(entry)
        self.say(
            f"\n[DISCOVERY / FRONTIER]\nURLs known: {snapshot.discovered}"
            f"\nQueued: {snapshot.queued}\nCompleted: {snapshot.completed}"
            f"\nSkipped: {snapshot.skipped}\nFailed: {snapshot.failed}"
            f"\n[NEXT]\n{'Process next queued URL.' if snapshot.queued else 'Finish bounded site crawl.'}"
        )

    def _print_acquisition(self, trace: AcquisitionTrace) -> None:
        fetched, inspection, result = trace.fetched, trace.inspection, trace.ingestion
        if fetched is None:
            self.say("\n[FETCH]\nNetwork acquisition failed under the safe fetch policy.")
            return
        self.say(
            f"\n[FETCH]\nStatus: {fetched.status_code}\nContent-Type: {fetched.content_type}"
            f"\nFinal URL: {fetched.final_url}"
        )
        if inspection:
            self.say(
                f"\n[PAGE INSPECTION]\nTitle: {inspection.title or 'not exposed'}"
                f"\nHTML language: {inspection.html_language or 'not exposed'}"
                f"\nArticle container: {'yes' if inspection.has_article else 'no'}"
                f"\nJSON-LD: {', '.join(inspection.json_ld_types) or 'none'}"
                f"\nParagraphs: {inspection.paragraph_count}\nLinks: {inspection.link_count}"
                f"\nDynamic evidence: {'yes' if inspection.likely_dynamic else 'no'}"
            )
        if result is None:
            return
        document = result.document
        strategy = document.extraction_method if document else "not currently exposed"
        self.say(f"\n[EXTRACTION]\nStrategy: {strategy}")
        if document:
            self.say(f"Characters extracted: {len(document.normalized_text)}")
            self.say(
                f"\n[LANGUAGE]\nDecision: {document.language or 'accepted'}"
                f"\nEvidence score (heuristic, not a probability): {document.language_confidence}"
                f"\nEvidence: {', '.join(document.language_evidence)}"
            )
            self.say(
                f"\n[CORPUS]\nArtifact: {result.storage_path or 'existing artifact'}"
                f"\nSHA-256: {document.content_hash}\nCanonical URL: {document.canonical_url}"
                f"\nDuplicate: {'yes — ' + result.duplicate_reason if result.duplicate_reason else 'no'}"
            )
        else:
            observation = result.observation
            self.say("\n[ACQUISITION RESULT]\nStatus: REJECTED")
            if observation:
                self.say(f"Stage: {observation.stage.value}\nReason: {observation.reason.value}")
                if observation.extraction_strategy:
                    self.say(f"Strategy: {observation.extraction_strategy}")
                if observation.html_language:
                    self.say(f"HTML language: {observation.html_language}")
                if observation.paragraph_count is not None:
                    self.say(f"Paragraphs: {observation.paragraph_count}")
                if observation.extracted_character_count is not None:
                    self.say(f"Characters extracted: {observation.extracted_character_count}")
                if observation.language_evidence_score is not None:
                    self.say(
                        "Language evidence score (heuristic, not a probability): "
                        f"{observation.language_evidence_score}"
                    )
                if observation.dynamic_signal is not None:
                    self.say(f"Dynamic evidence: {'yes' if observation.dynamic_signal else 'no'}")
            self.say("Artifact: none")

    def _print_candidates(self, parent: FrontierEntry) -> None:
        children = [
            item
            for item in self.repository.list_entries(parent.job_id)
            if item.parent_url == parent.url.value
        ]
        if not children:
            return
        eligible = sum(item.state.value != "skipped" for item in children)
        self.say(
            f"\n[CANDIDATES]\nDiscovered from page: {len(children)}"
            f"\nEligible/queued: {eligible}\nSkipped before acquisition: {len(children) - eligible}"
        )
        for item in children[: self.candidate_example_limit]:
            decision = "SKIPPED" if item.state.value == "skipped" else "ELIGIBLE"
            self.say(
                f"\n[CANDIDATE]\nURL: {item.url.value}\nResource kind: {item.resource_kind.value}"
                f"\nDecision: {decision}\nPriority: {item.priority.name}"
                f"\nEvidence: {', '.join(item.candidate_evidence) or 'neutral URL path'}"
            )
            if item.skip_reason:
                self.say(f"Reason: {item.skip_reason}\n→ crawl budget preserved")
            else:
                self.say("→ queued")
        if len(children) > self.candidate_example_limit:
            self.say(
                f"Candidate examples limited to {self.candidate_example_limit}; "
                f"{len(children) - self.candidate_example_limit} omitted."
            )

    def _site_metrics(self, name, origin, job_id, snapshot, entries) -> SiteSummary:
        traces = [self.acquisition.traces.get(entry.url.value) for entry in entries]
        results = [trace.ingestion for trace in traces if trace and trace.ingestion]
        return SiteSummary(
            name,
            origin,
            job_id,
            snapshot.discovered,
            snapshot.pages_attempted,
            snapshot.completed,
            snapshot.skipped,
            snapshot.failed,
            sum(
                count
                for reason, count in snapshot.skip_reasons.items()
                if reason.startswith("robots_")
            ),
            snapshot.skip_reasons.get("external_origin", 0),
            sum(result.status == "language_rejected" for result in results),
            snapshot.duplicates,
            sum(result.status == "stored" for result in results),
            snapshot.termination_reason,
            snapshot.eligible_candidates,
            snapshot.skipped_before_acquisition,
            snapshot.high_priority_candidates,
            snapshot.low_priority_candidates,
            snapshot.failure_reasons.get("insufficient_static_content", 0)
            + snapshot.failure_reasons.get("dynamic_browser_required", 0),
            snapshot.skip_reasons.get("depth_limit", 0),
            snapshot.skip_reasons.get("unsafe_url", 0),
        )

    def _print_site_summary(self, item: SiteSummary) -> None:
        self.say(
            f"\nSITE SUMMARY\nSite: {item.name}\nOrigin: {item.origin}"
            f"\nCrawl job ID: {item.job_id}\nDiscovered: {item.discovered}"
            f"\nAttempted: {item.attempted}\nCompleted: {item.completed}"
            f"\nSkipped: {item.skipped}\nFailed: {item.failed}"
            f"\nRobots denied: {item.robots_denied}\nDuplicates: {item.duplicates}"
            f"\nExternal-origin exclusions: {item.external_exclusions}"
            f"\nLanguage rejections: {item.language_rejections}"
            f"\nEligible candidates: {item.eligible}"
            f"\nSkipped before acquisition: {item.skipped_before_acquisition}"
            f"\nHigh-priority candidates: {item.high_priority}"
            f"\nLow-priority candidates: {item.low_priority}"
            f"\nStatic/extraction rejections: {item.extraction_rejections}"
            f"\nCorpus artifacts: {item.artifacts}\nTermination reason: {item.termination}"
        )

    def _print_final(self) -> None:
        self.say("\n" + "=" * 60 + "\nLIVE DEMO COMPLETE\nSites processed: 3")
        for item in self.summaries:
            self.say(
                f"\n{item.name}\nCompleted: {item.completed}\nArtifacts: {item.artifacts}"
                f"\nTermination: {item.termination}"
            )
        self.say(
            f"\nTOTAL\nURLs discovered: {sum(x.discovered for x in self.summaries)}"
            f"\nPages attempted: {sum(x.attempted for x in self.summaries)}"
            f"\nCompleted: {sum(x.completed for x in self.summaries)}"
            f"\nSkipped: {sum(x.skipped for x in self.summaries)}"
            f"\nFailed: {sum(x.failed for x in self.summaries)}"
            f"\nCorpus artifacts: {sum(x.artifacts for x in self.summaries)}"
            f"\nDuplicates: {sum(x.duplicates for x in self.summaries)}"
        )


def build_demo(
    output_dir: Path,
    state_db: Path,
    output: TextIO,
    demo_delay: float,
    max_pages_per_site: int = MAX_PAGES_PER_SITE,
    max_depth: int = MAX_DEPTH,
) -> LiveCrawlDemo:
    engine = create_engine(f"sqlite:///{state_db}")
    event.listen(
        engine, "connect", lambda connection, _: connection.execute("PRAGMA foreign_keys=ON")
    )
    Base.metadata.create_all(engine)
    session = Session(engine)
    analyzer = URLNewsAnalyzer()
    pipeline = AcquisitionPipeline(CorpusStore(output_dir))
    acquisition = TracedWebAcquisition(analyzer, pipeline)
    repository = SqlAlchemyCrawlRepository(session)
    orchestrator = CrawlOrchestrator(
        repository,
        PublicUrlSafetyAdapter(),
        RobotsPolicyService(SafeRobotsRetriever(analyzer)),
        OriginRateScheduler(SystemClock(), 2.0),
        acquisition,
    )
    return LiveCrawlDemo(
        orchestrator,
        repository,
        acquisition,
        SystemBrowserViewer.detect(),
        output,
        demo_delay,
        max_pages_per_site,
        max_depth,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded three-site live crawl demo")
    parser.add_argument("--max-pages-per-site", type=int, choices=(1, 2, 3), default=3)
    parser.add_argument("--max-depth", type=int, choices=(0, 1), default=1)
    parser.add_argument("--demo-delay", type=float, default=2.0)
    parser.add_argument("--output", type=Path, default=Path("data/live-crawl-demo/corpus"))
    parser.add_argument(
        "--state-db", type=Path, default=Path("data/live-crawl-demo/frontier.sqlite")
    )
    args = parser.parse_args()
    if args.demo_delay < 0 or args.demo_delay > 10:
        parser.error("--demo-delay must be between 0 and 10 seconds")
    args.output.mkdir(parents=True, exist_ok=True)
    args.state_db.parent.mkdir(parents=True, exist_ok=True)
    import sys

    demo = build_demo(
        args.output,
        args.state_db,
        sys.stdout,
        args.demo_delay,
        args.max_pages_per_site,
        args.max_depth,
    )
    demo.run()
    print(f"\nCorpus output directory: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
