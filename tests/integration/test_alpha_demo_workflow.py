"""
Integration test for the main Release 1 internal alpha workflow.
"""
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.entities import DictionaryEntry, SwahiliTerm
from src.domain.services.bantu_classifier import BantuClassifierService
from src.domain.services.root_extractor import RootExtractorService
from src.domain.value_objects import Etymology, WordType
from src.infrastructure.database.models import Base
from src.infrastructure.repositories.dictionary_repository import DictionaryRepository
from src.infrastructure.repositories.term_repository import TermRepository
from src.web.api import app, get_api_db
from tests.asgi_client import ASGITestClient


@pytest.fixture
def alpha_demo_client(tmp_path):
    """Create a request-scoped API client backed by a temporary SQLite database."""
    db_path = tmp_path / "alpha_demo.sqlite"
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    async def override_db():
        db = TestingSessionLocal()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_api_db] = override_db

    # Seed one dictionary-backed lexical entry for query validation.
    session = TestingSessionLocal()
    try:
        term_repo = TermRepository(session)
        dict_repo = DictionaryRepository(session)
        root_service = RootExtractorService()
        bantu_service = BantuClassifierService()

        term = SwahiliTerm(
            term="mtu",
            root=root_service.extract("mtu", WordType.NOUN),
            noun_class=bantu_service.infer_class("mtu", WordType.NOUN),
            etymology=Etymology.BANTU,
            word_type=WordType.NOUN,
        )
        term_id = term_repo.save(term)
        saved_term = term_repo.find_by_term("mtu")
        assert saved_term is not None

        dict_repo.save(
            DictionaryEntry(
                term=saved_term,
                meaning="binadamu, mwanadamu",
                english_translation="person, human being",
                synonyms=["binadamu", "mwanadamu"],
                usage_examples=["Mtu huyu ni mwalimu."],
                usage_context="formal",
            ),
            term_id,
        )
        session.commit()
    finally:
        session.close()

    with ASGITestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    engine.dispose()


@pytest.mark.integration
def test_release_one_alpha_demo_workflow(alpha_demo_client):
    """
    Validate the stable local alpha demo path:
    health -> save article -> query stats/articles/dictionary -> trends.
    """
    health = alpha_demo_client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    save_response = alpha_demo_client.post(
        "/news/save",
        json={
            "content": "Mtu mmoja anasoma habari za elimu mjini Dodoma kila asubuhi.",
            "category": "Education",
            "source_url": "seed://alpha-demo/manual-save-001",
            "sentiment_polarity": 0.3,
            "sentiment_confidence": 0.8,
            "sentiment_label": "positive",
        },
    )
    assert save_response.status_code == 200
    saved_payload = save_response.json()
    assert saved_payload["success"] is True
    assert saved_payload["article_id"] == 1

    stats = alpha_demo_client.get("/stats")
    assert stats.status_code == 200
    stats_payload = stats.json()
    assert stats_payload["terms"] >= 1
    assert stats_payload["news_articles"] >= 1

    articles = alpha_demo_client.get("/news/articles", params={"limit": 20})
    assert articles.status_code == 200
    articles_payload = articles.json()
    assert len(articles_payload) >= 1
    assert articles_payload[0]["category"] == "Education"
    assert "content" in articles_payload[0]

    dictionary = alpha_demo_client.get("/dictionary/mtu")
    assert dictionary.status_code == 200
    dictionary_payload = dictionary.json()
    assert dictionary_payload["term"] == "mtu"
    assert dictionary_payload["english_translation"] == "person, human being"

    trends = alpha_demo_client.get("/news/trends")
    assert trends.status_code == 200
    trends_payload = trends.json()
    assert isinstance(trends_payload, list)
    assert len(trends_payload) >= 1
