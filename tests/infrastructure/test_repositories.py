"""SQLite-backed repository and transaction regression tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities import NewsArticle, SwahiliTerm
from src.domain.value_objects import BantuClass, MorphologicalRoot, SentimentScore, WordType
from src.infrastructure.database.models import Base
from src.infrastructure.repositories.news_repository import NewsRepository
from src.infrastructure.repositories.term_repository import TermRepository


@pytest.fixture
def session_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'repositories.sqlite'}")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False)
    yield factory
    engine.dispose()


def test_term_round_trip_and_duplicate_rejection(session_factory):
    session = session_factory()
    repo = TermRepository(session)
    term = SwahiliTerm(
        term="Mtu",
        root=MorphologicalRoot(root="tu", prefix="m"),
        noun_class=BantuClass.M_WA,
        word_type=WordType.NOUN,
    )

    term_id = repo.save(term)
    session.commit()

    restored = repo.find_by_id(term_id)
    assert restored is not None
    assert restored.term == "mtu"
    assert restored.root.root == "tu"
    with pytest.raises(ValueError, match="already exists"):
        repo.save(term)
    session.close()


def test_rollback_does_not_persist_uncommitted_term(session_factory):
    session = session_factory()
    repo = TermRepository(session)
    repo.save(SwahiliTerm(term="kitabu", word_type=WordType.NOUN))
    session.rollback()
    session.close()

    verification = session_factory()
    assert TermRepository(verification).find_by_term("kitabu") is None
    verification.close()


def test_news_counts_are_grouped_per_category(session_factory):
    session = session_factory()
    repo = NewsRepository(session)
    for category in ["Education", "Education", "Health"]:
        repo.save(
            NewsArticle(
                content="Habari ya Kiswahili yenye maelezo ya kutosha.",
                category=category,
                sentiment_score=SentimentScore(polarity=0.0, confidence=0.5),
            )
        )
    session.commit()

    assert repo.count() == 3
    assert repo.count_by_category() == {"Education": 2, "Health": 1}
    assert len(repo.find_with_sentiment("neutral")) == 3
    session.close()
