"""
Smoke-test fixtures for alpha API validation.
"""

import pytest

from src.domain.entities import DictionaryEntry, NewsArticle, SwahiliTerm
from src.domain.value_objects import BantuClass, Etymology, MorphologicalRoot, WordType
from src.web.api import (
    app,
    get_dictionary_repository,
    get_news_repository,
    get_term_repository,
)
from tests.asgi_client import ASGITestClient


class FakeTermRepository:
    """Minimal term repository for stable smoke tests."""

    def __init__(self) -> None:
        self._term = SwahiliTerm(
            term="mtu",
            root=MorphologicalRoot(root="tu", prefix="m"),
            noun_class=BantuClass.M_WA,
            etymology=Etymology.BANTU,
            word_type=WordType.NOUN,
            frequency_score=15.5,
        )

    def find_by_term(self, term: str) -> SwahiliTerm | None:
        normalized = term.strip().lower()
        if normalized == self._term.term:
            return self._term
        return None

    def count(self) -> int:
        return 1


class FakeDictionaryRepository:
    """Minimal dictionary repository for stable smoke tests."""

    def __init__(self) -> None:
        term = SwahiliTerm(
            term="mtu",
            root=MorphologicalRoot(root="tu", prefix="m"),
            noun_class=BantuClass.M_WA,
            etymology=Etymology.BANTU,
            word_type=WordType.NOUN,
        )
        self._entry = DictionaryEntry(
            term=term,
            meaning="binadamu, mwanadamu",
            english_translation="person, human being",
            synonyms=["binadamu", "mwanadamu"],
            usage_examples=["Mtu huyu ni rafiki yangu"],
            usage_context="formal",
        )

    def find_by_term_string(self, term: str) -> DictionaryEntry | None:
        if term.strip().lower() == self._entry.term.term:
            return self._entry
        return None


class FakeNewsRepository:
    """Minimal in-memory news repository for stable smoke tests."""

    def __init__(self) -> None:
        self._saved_articles: list[NewsArticle] = []

    def save(self, article: NewsArticle) -> int:
        self._saved_articles.append(article)
        return len(self._saved_articles)

    def count(self) -> int:
        return len(self._saved_articles)


@pytest.fixture
def fake_term_repo() -> FakeTermRepository:
    """Provide a deterministic term repository."""
    return FakeTermRepository()


@pytest.fixture
def fake_dictionary_repo() -> FakeDictionaryRepository:
    """Provide a deterministic dictionary repository."""
    return FakeDictionaryRepository()


@pytest.fixture
def fake_news_repo() -> FakeNewsRepository:
    """Provide a deterministic news repository."""
    return FakeNewsRepository()


@pytest.fixture
def client(fake_term_repo, fake_dictionary_repo, fake_news_repo) -> ASGITestClient:
    """Create a TestClient with repository overrides for smoke tests."""

    async def term_override():
        return fake_term_repo

    async def dictionary_override():
        return fake_dictionary_repo

    async def news_override():
        return fake_news_repo

    app.dependency_overrides[get_term_repository] = term_override
    app.dependency_overrides[get_dictionary_repository] = dictionary_override
    app.dependency_overrides[get_news_repository] = news_override

    with ASGITestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
