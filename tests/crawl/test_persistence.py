from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

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


def test_frontier_persists_deduplicates_orders_and_recovers(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'crawl.sqlite'}")
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    first = SqlAlchemyCrawlRepository(factory())
    job = CrawlJob.create([CrawlUrl.parse("https://example.com")], CrawlBudget(5, 2, 2, 5))
    first.save_job(job)
    deep = FrontierEntry(
        None,
        job.id,
        CrawlUrl.parse("https://example.com/deep"),
        2,
        priority=CandidatePriority.HIGH,
    )
    deep.transition(FrontierState.QUEUED)
    shallow = FrontierEntry(
        None,
        job.id,
        CrawlUrl.parse("https://example.com/shallow"),
        1,
        priority=CandidatePriority.LOW,
    )
    shallow.transition(FrontierState.QUEUED)
    assert first.add_entry(deep)
    assert first.add_entry(shallow)
    assert not first.add_entry(
        FrontierEntry(None, job.id, CrawlUrl.parse("https://example.com/shallow#duplicate"), 1)
    )
    processing = first.next_queued(job.id)
    assert processing is not None and processing.url.value.endswith("/shallow")
    processing.transition(FrontierState.PROCESSING)
    first.save_entry(processing)
    first.session.close()

    resumed = SqlAlchemyCrawlRepository(factory())
    loaded = resumed.get_job(job.id)
    assert loaded is not None and loaded.budget == job.budget
    assert resumed.recover_processing(job.id) == 1
    assert resumed.next_queued(job.id).url.value.endswith("/shallow")
    assert len(resumed.list_entries(job.id)) == 2
    resumed.session.close()
    engine.dispose()


def test_priority_and_evidence_survive_reload_with_stable_equal_priority_order(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'priority.sqlite'}")
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    repository = SqlAlchemyCrawlRepository(factory())
    job = CrawlJob.create([CrawlUrl.parse("https://example.com")], CrawlBudget(5, 2, 2, 5))
    repository.save_job(job)
    low = FrontierEntry(
        None,
        job.id,
        CrawlUrl.parse("https://example.com/category"),
        1,
        priority=CandidatePriority.LOW,
    )
    first_high = FrontierEntry(
        None,
        job.id,
        CrawlUrl.parse("https://example.com/sw/news/one"),
        1,
        priority=CandidatePriority.HIGH,
        resource_kind=ResourceKind.ARTICLE,
        candidate_evidence=("expected_language_path", "article_like_path"),
    )
    second_high = FrontierEntry(
        None,
        job.id,
        CrawlUrl.parse("https://example.com/sw/news/two"),
        1,
        priority=CandidatePriority.HIGH,
    )
    for entry in (low, first_high, second_high):
        entry.transition(FrontierState.QUEUED)
        assert repository.add_entry(entry)
    repository.session.close()

    resumed = SqlAlchemyCrawlRepository(factory())
    first = resumed.next_queued(job.id)

    assert first is not None and first.url.value.endswith("/one")
    assert first.priority == CandidatePriority.HIGH
    assert first.resource_kind == ResourceKind.ARTICLE
    assert first.candidate_evidence == ("expected_language_path", "article_like_path")
    first.transition(FrontierState.PROCESSING)
    resumed.save_entry(first)
    assert resumed.next_queued(job.id).url.value.endswith("/two")
    resumed.session.close()
    engine.dispose()
