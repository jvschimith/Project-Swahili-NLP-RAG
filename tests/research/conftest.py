from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from src.acquisition.models import WebDocument
from src.acquisition.storage import CorpusStore
from src.crawl.domain import (
    CandidatePriority,
    CrawlBudget,
    CrawlJob,
    CrawlUrl,
    FrontierEntry,
    FrontierState,
    ResourceKind,
)
from src.crawl.infrastructure import SqlAlchemyCrawlRepository
from src.infrastructure.database.connection import _enable_sqlite_foreign_keys
from src.infrastructure.database.models import Base
from src.infrastructure.research_repository import SqlAlchemyResearchRepository
from src.research.models import CorpusPilotRun, PilotConfiguration, PilotSource


@pytest.fixture
def research_state(tmp_path):
    database = tmp_path / "pilot.sqlite"
    corpus = tmp_path / "corpus"
    engine = create_engine(f"sqlite:///{database}")
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    Base.metadata.create_all(engine)
    session = Session(engine)
    sources = (
        PilotSource("One", "https://one.example/sw/", "news", "first source"),
        PilotSource("Two", "https://two.example/sw/", "knowledge", "second source"),
    )
    pilot = CorpusPilotRun.create(PilotConfiguration(sources, 3, 1, 1))
    research = SqlAlchemyResearchRepository(session)
    research.create_pilot(
        pilot,
        software_version="test-v1",
        git_branch="test",
        git_commit="a" * 40,
        git_dirty=False,
        python_version="3.12",
        corpus_path=str(corpus),
        database_path=str(database),
    )
    pilot.start()
    research.save_pilot(pilot)
    crawl = SqlAlchemyCrawlRepository(session)
    jobs = []
    for source in sources:
        seed = CrawlUrl.parse(source.seed_url)
        job = CrawlJob.create([seed], CrawlBudget(3, 1, 3, 3))
        job.start()
        crawl.save_job(job)
        research.associate_source_job(pilot.id, seed.origin, job.id)
        pilot.associate_job(job.id)
        jobs.append(job)

    document = _document("artifact-one", "one.example", "Habari safi ya Kiswahili.")
    CorpusStore(corpus).save(document)
    accepted = FrontierEntry(
        None,
        jobs[0].id,
        CrawlUrl.parse("https://one.example/sw/story/2026/08/one"),
        1,
        state=FrontierState.PROCESSING,
        priority=CandidatePriority.HIGH,
        resource_kind=ResourceKind.ARTICLE,
        candidate_evidence=("expected_language_path", "article_like_path"),
    )
    crawl.add_entry(accepted)
    accepted.attempts = 1
    accepted.artifact_id = document.document_id
    accepted.artifact_created = True
    accepted.final_url = accepted.url.value
    accepted.acquisition_stage = "storage"
    accepted.acquisition_reason = "accepted"
    accepted.acquisition_details = (("title", document.title), ("paragraph_count", 3))
    accepted.state = FrontierState.COMPLETED
    crawl.save_entry(accepted)
    jobs[0].record_completed()
    crawl.save_job(jobs[0])

    rejected = FrontierEntry(
        None,
        jobs[0].id,
        CrawlUrl.parse("https://one.example/sw/story/2026/08/two"),
        1,
        state=FrontierState.PROCESSING,
        priority=CandidatePriority.HIGH,
        resource_kind=ResourceKind.ARTICLE,
    )
    crawl.add_entry(rejected)
    rejected.attempts = 1
    rejected.acquisition_stage = "static_extraction"
    rejected.acquisition_reason = "insufficient_static_content"
    rejected.state = FrontierState.FAILED
    crawl.save_entry(rejected)
    jobs[0].record_failed()
    crawl.save_job(jobs[0])

    skipped = FrontierEntry(
        None,
        jobs[1].id,
        CrawlUrl.parse("https://two.example/ar/story"),
        1,
        state=FrontierState.SKIPPED,
        priority=CandidatePriority.LOW,
        skip_reason="competing_language_path",
    )
    crawl.add_entry(skipped)
    jobs[1].record_skipped()
    crawl.save_job(jobs[1])
    yield session, pilot, corpus, database, research
    session.close()
    engine.dispose()


def _document(document_id: str, domain: str, text: str) -> WebDocument:
    return WebDocument(
        document_id=document_id,
        original_url=f"https://{domain}/sw/story",
        final_url=f"https://{domain}/sw/story",
        canonical_url=f"https://{domain}/sw/story",
        source_domain=domain,
        title="Habari ya majaribio",
        author=None,
        published_at=None,
        retrieved_at=datetime(2026, 8, 17, tzinfo=timezone.utc).isoformat(),
        language="sw",
        language_confidence=1.0,
        language_evidence=("swahili_function_words=10",),
        raw_text=text,
        normalized_text=text,
        content_hash="b" * 64,
        extraction_method="semantic_article",
        extraction_metadata={},
        provenance={"acquisition_version": "web-corpus-v1"},
    )
