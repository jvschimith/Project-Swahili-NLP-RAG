"""Headless bounded Public Swahili Corpus Pilot runner."""

from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from src.acquisition.inspector import PageInspector
from src.acquisition.pipeline import AcquisitionPipeline
from src.acquisition.storage import CorpusStore
from src.application.services.url_analyzer import URLNewsAnalyzer
from src.crawl.application import (
    CrawlOrchestrator,
    OriginRateScheduler,
    RobotsPolicyService,
)
from src.crawl.domain import CrawlBudget, CrawlUrl
from src.crawl.infrastructure import (
    PublicUrlSafetyAdapter,
    SafeRobotsRetriever,
    SqlAlchemyCrawlRepository,
    SystemClock,
    WebAcquisitionAdapter,
)
from src.infrastructure.database.connection import _enable_sqlite_foreign_keys
from src.infrastructure.database.models import Base
from src.infrastructure.research_repository import SqlAlchemyResearchRepository
from src.research.models import CorpusPilotRun, PilotConfiguration, PilotSource
from src.research.queries import CorpusResearchQueryService

PILOT_VERSION = "public-swahili-corpus-pilot-v1"

PREFLIGHT_CANDIDATES = (
    PilotSource(
        "VOA Swahili",
        "https://www.voaswahili.com/",
        "international_news",
        "Public Swahili reporting with stable static editorial routes.",
        "/",
    ),
    PilotSource(
        "DW Kiswahili",
        "https://www.dw.com/sw/",
        "international_news",
        "Long-form Swahili reporting with semantic article containers.",
        "/sw/",
    ),
    PilotSource(
        "UN News Kiswahili",
        "https://news.un.org/sw/",
        "institutional_public_information",
        "Public humanitarian and development reporting in Swahili.",
        "/sw/",
    ),
    PilotSource(
        "Global Voices Kiswahili",
        "https://sw.globalvoices.org/",
        "public_cultural_media",
        "Swahili civic and cultural reporting from a distinct publisher model.",
        "sw subdomain",
    ),
    PilotSource(
        "Wikipedia Kiswahili",
        "https://sw.wikipedia.org/wiki/Mwanzo",
        "public_knowledge",
        "Public encyclopedic Swahili provides non-news genre diversity.",
        "sw subdomain",
    ),
    PilotSource(
        "Vatican News Kiswahili",
        "https://www.vaticannews.va/sw.html",
        "public_cultural_institution",
        "Public institutional and cultural reporting in Swahili.",
        "/sw",
    ),
    PilotSource(
        "BBC News Swahili",
        "https://www.bbc.com/swahili",
        "international_news",
        "Independent international publisher useful for cross-source extraction comparison.",
        "/swahili",
    ),
    PilotSource(
        "HabariLEO",
        "https://habarileo.co.tz/",
        "national_news",
        "Tanzanian public news source adds regional publisher diversity.",
        "/",
    ),
)

PILOT_SOURCES = tuple(
    PilotSource(
        source.name,
        source.seed_url,
        source.category,
        source.rationale,
        source.expected_language_route,
        "robots_allowed",
        {
            "UN News Kiswahili": "insufficient_static_evidence",
        }.get(source.name, "generic_static"),
        {
            "VOA Swahili": "170 seed links",
            "DW Kiswahili": "144 seed links",
            "UN News Kiswahili": "190 seed links",
            "Global Voices Kiswahili": "446 seed links",
            "Vatican News Kiswahili": "211 seed links",
            "BBC News Swahili": "85 seed links",
            "HabariLEO": "125 seed links",
        }.get(source.name),
        "no obvious dynamic dependence",
    )
    for source in PREFLIGHT_CANDIDATES
    if source.name != "Wikipedia Kiswahili"
)


def preflight_sources(
    sources: tuple[PilotSource, ...] = PREFLIGHT_CANDIDATES,
) -> list[dict[str, object]]:
    analyzer = URLNewsAnalyzer()
    safety = PublicUrlSafetyAdapter()
    robots = RobotsPolicyService(SafeRobotsRetriever(analyzer))
    results: list[dict[str, object]] = []
    for source in sources:
        url = CrawlUrl.parse(source.seed_url)
        safe = safety.is_safe(url.value)
        decision = robots.decision(url, "SwahiliLinguisticIntelligence") if safe else None
        fetched = (
            analyzer.fetch_result(url.value) if safe and decision and decision.allowed else None
        )
        inspection = (
            PageInspector.inspect_html(fetched.final_url, fetched.html) if fetched else None
        )
        results.append(
            {
                "name": source.name,
                "origin": url.origin,
                "seed_url": source.seed_url,
                "category": source.category,
                "rationale": source.rationale,
                "expected_language_route": source.expected_language_route,
                "safe": safe,
                "robots_allowed": decision.allowed if decision else False,
                "robots_reason": decision.reason if decision else "not_checked",
                "static_suitability": (
                    inspection.recommended_strategy if inspection else "unavailable"
                ),
                "candidate_availability": inspection.link_count if inspection else 0,
                "dynamic_dependence": inspection.likely_dynamic if inspection else None,
                "html_language": inspection.html_language if inspection else None,
            }
        )
    return results


def run_pilot(
    configuration: PilotConfiguration,
    *,
    state_db: Path,
    corpus_root: Path,
    manifest_path: Path,
) -> str:
    state_db.parent.mkdir(parents=True, exist_ok=True)
    corpus_root.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{state_db}")
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    Base.metadata.create_all(engine)
    session = Session(engine)
    research = SqlAlchemyResearchRepository(session)
    pilot = CorpusPilotRun.create(configuration)
    branch, commit, dirty = _git_metadata()
    research.create_pilot(
        pilot,
        software_version=PILOT_VERSION,
        git_branch=branch,
        git_commit=commit,
        git_dirty=dirty,
        python_version=platform.python_version(),
        corpus_path=str(corpus_root.resolve()),
        database_path=str(state_db.resolve()),
    )
    analyzer = URLNewsAnalyzer()
    repository = SqlAlchemyCrawlRepository(session)
    orchestrator = CrawlOrchestrator(
        repository,
        PublicUrlSafetyAdapter(),
        RobotsPolicyService(SafeRobotsRetriever(analyzer)),
        OriginRateScheduler(SystemClock(), configuration.min_delay_seconds),
        WebAcquisitionAdapter(analyzer, AcquisitionPipeline(CorpusStore(corpus_root))),
    )
    pilot.start()
    research.save_pilot(pilot)
    try:
        for source in configuration.sources:
            origin = CrawlUrl.parse(source.seed_url).origin
            job = orchestrator.start_crawl(
                [source.seed_url],
                CrawlBudget(
                    configuration.max_pages_per_source,
                    configuration.max_depth,
                    configuration.max_pages_per_source,
                    configuration.max_pages_per_source,
                ),
                allowed_origins={origin},
                min_delay_seconds=configuration.min_delay_seconds,
            )
            pilot.associate_job(job.id)
            research.associate_source_job(pilot.id, origin, job.id)
            print(
                json.dumps(
                    {
                        "event": "source_started",
                        "pilot_id": pilot.id,
                        "source": source.name,
                        "job_id": job.id,
                    }
                )
            )
            snapshot = orchestrator.run(job.id)
            research.finish_source(pilot.id, origin)
            print(
                json.dumps(
                    {
                        "event": "source_finished",
                        "source": source.name,
                        "snapshot": snapshot.__dict__,
                    },
                    default=str,
                )
            )
        pilot.complete()
    except KeyboardInterrupt:
        pilot.interrupt()
        raise
    except Exception as error:
        pilot.fail(f"{type(error).__name__}: {error}")
        raise
    finally:
        research.save_pilot(pilot)
        query = CorpusResearchQueryService(session, corpus_root)
        write_pilot_manifest(query, pilot.id, manifest_path)
        session.close()
        engine.dispose()
    return pilot.id


def write_pilot_manifest(
    query: CorpusResearchQueryService, pilot_id: str, manifest_path: Path
) -> None:
    """Write the reproducible report without copying corpus text into it."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(query.manifest(pilot_id), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _git_metadata() -> tuple[str | None, str | None, bool | None]:
    try:
        branch = subprocess.run(
            ("git", "branch", "--show-current"), capture_output=True, text=True, check=True
        ).stdout.strip()
        commit = subprocess.run(
            ("git", "rev-parse", "HEAD"), capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ("git", "status", "--porcelain"), capture_output=True, text=True, check=True
            ).stdout.strip()
        )
        return branch or None, commit or None, dirty
    except (OSError, subprocess.SubprocessError):
        return None, None, None


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Public Swahili Corpus Pilot")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--max-pages-per-source", type=int, default=10)
    parser.add_argument("--max-depth", type=int, choices=(0, 1, 2), default=1)
    parser.add_argument("--min-delay", type=float, default=2.0)
    parser.add_argument("--state-db", type=Path, default=Path("data/corpus-pilot/pilot.sqlite"))
    parser.add_argument("--corpus", type=Path, default=Path("data/corpus-pilot/corpus"))
    parser.add_argument(
        "--manifest", type=Path, default=Path("data/corpus-pilot/pilot-manifest.json")
    )
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight_sources(), ensure_ascii=False, indent=2))
        return 0
    configuration = PilotConfiguration(
        PILOT_SOURCES,
        args.max_pages_per_source,
        args.max_depth,
        args.min_delay,
    )
    pilot_id = run_pilot(
        configuration, state_db=args.state_db, corpus_root=args.corpus, manifest_path=args.manifest
    )
    print(json.dumps({"pilot_id": pilot_id, "status": "finished"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
