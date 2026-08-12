#!/usr/bin/env python3
"""
Seed a minimal deterministic local dataset for Release 1 alpha.

Usage:
    python scripts/seed_release1_alpha.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from src.domain.entities import DictionaryEntry, NewsArticle, SwahiliTerm
from src.domain.services.bantu_classifier import BantuClassifierService
from src.domain.services.root_extractor import RootExtractorService
from src.domain.value_objects import Etymology, SentimentScore, WordType
from src.infrastructure.config import settings
from src.infrastructure.database import get_session, init_db
from src.infrastructure.database.models import DBDictionary, DBNews, DBPOS, DBTerm
from src.infrastructure.logging_config import setup_logging
from src.infrastructure.repositories.dictionary_repository import DictionaryRepository
from src.infrastructure.repositories.news_repository import NewsRepository
from src.infrastructure.repositories.term_repository import TermRepository


SEED_DIR = Path(__file__).parent.parent / "data" / "seed"
DICTIONARY_FIXTURE = SEED_DIR / "release1_dictionary.json"
LINGUISTIC_FIXTURE = SEED_DIR / "release1_linguistic_sample.json"
NEWS_FIXTURE = SEED_DIR / "release1_news.json"


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _map_word_type(value: str) -> WordType:
    mapping = {
        "noun": WordType.NOUN,
        "verb": WordType.VERB,
        "adjective": WordType.ADJECTIVE,
        "adverb": WordType.ADVERB,
    }
    return mapping.get((value or "").strip().lower(), WordType.UNKNOWN)


def _map_etymology(value: str) -> Etymology:
    mapping = {
        "bantu": Etymology.BANTU,
        "arabic": Etymology.ARABIC,
        "english": Etymology.ENGLISH,
        "portuguese": Etymology.PORTUGUESE,
        "german": Etymology.GERMAN,
        "indian": Etymology.INDIAN,
        "persian": Etymology.PERSIAN,
    }
    return mapping.get((value or "").strip().lower(), Etymology.UNKNOWN)


def _ensure_term(session, term_repo, root_service, bantu_service, word: str, word_type: WordType, etymology: Etymology) -> int:
    normalized = word.strip().lower()
    existing_db_term = session.query(DBTerm).filter_by(swahili_term=normalized).first()
    if existing_db_term:
        return existing_db_term.id

    root = root_service.extract(normalized, word_type=word_type)
    noun_class = bantu_service.infer_class(normalized, word_type)

    term = SwahiliTerm(
        term=normalized,
        root=root,
        noun_class=noun_class,
        etymology=etymology,
        word_type=word_type,
    )
    return term_repo.save(term)


def seed_dictionary(session, term_repo, dict_repo, root_service, bantu_service):
    """Seed a few dictionary-backed lexical entries."""
    entries = _load_json(DICTIONARY_FIXTURE)
    stats = {"dictionary_terms": 0, "dictionary_entries": 0}

    for item in entries:
        word = item["word"].strip().lower()
        word_type = _map_word_type(item.get("word_type", "noun"))
        etymology = _map_etymology(item.get("etymology", "unknown"))

        term_id = _ensure_term(
            session,
            term_repo,
            root_service,
            bantu_service,
            word=word,
            word_type=word_type,
            etymology=etymology,
        )

        term_entity = term_repo.find_by_term(word)
        if term_entity is None:
            raise ValueError(f"Seed term '{word}' could not be reloaded after creation")

        entry = DictionaryEntry(
            term=term_entity,
            meaning=item["meaning"],
            english_translation=item.get("english_translation"),
            synonyms=item.get("synonyms", []),
            usage_examples=item.get("usage_examples", []),
        )

        existing_entry = session.query(DBDictionary).join(DBTerm).filter(DBTerm.swahili_term == word).first()
        dict_repo.save(entry, term_id)

        stats["dictionary_terms"] += 1
        if existing_entry is None:
            stats["dictionary_entries"] += 1

    return stats


def seed_linguistic_sample(session, term_repo, root_service, bantu_service):
    """Seed a tiny POS-style linguistic sample."""
    sample_rows = _load_json(LINGUISTIC_FIXTURE)
    stats = {"linguistic_rows": 0}

    for row in sample_rows:
        word = row["word"].strip().lower()
        word_type = _map_word_type("verb" if row["tag"].upper() == "VERB" else "noun")

        term_id = _ensure_term(
            session,
            term_repo,
            root_service,
            bantu_service,
            word=word,
            word_type=word_type,
            etymology=Etymology.UNKNOWN,
        )

        existing = session.query(DBPOS).filter_by(
            term_id=term_id,
            tag=row["tag"].upper(),
            sentence_id=row["sentence_id"],
            word_order=row["word_order"],
        ).first()

        if existing is None:
            session.add(
                DBPOS(
                    term_id=term_id,
                    tag=row["tag"].upper(),
                    prefix_chain=row.get("prefix_chain"),
                    sentence_id=row["sentence_id"],
                    word_order=row["word_order"],
                    confidence=1.0,
                )
            )
            stats["linguistic_rows"] += 1

    return stats


def seed_news(session, news_repo):
    """Seed a few deterministic local news/example records."""
    items = _load_json(NEWS_FIXTURE)
    stats = {"news_records": 0}

    for item in items:
        existing = session.query(DBNews).filter_by(source_url=item["source_url"]).first()
        if existing is not None:
            continue

        article = NewsArticle(
            content=item["content"],
            category=item["category"],
            source_url=item["source_url"],
        )

        polarity = item.get("sentiment_polarity")
        if polarity is not None:
            article.analyze_sentiment(
                SentimentScore(
                    polarity=float(polarity),
                    confidence=float(item.get("sentiment_confidence", 0.5)),
                )
            )

        news_repo.save(article)
        stats["news_records"] += 1

    return stats


def main():
    """Run the Release 1 alpha seed workflow."""
    setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)
    logger.info("Initializing database for Release 1 alpha seed...")
    init_db()

    session = get_session()
    term_repo = TermRepository(session)
    dict_repo = DictionaryRepository(session)
    news_repo = NewsRepository(session)
    root_service = RootExtractorService()
    bantu_service = BantuClassifierService()

    try:
        stats = {}
        stats.update(seed_dictionary(session, term_repo, dict_repo, root_service, bantu_service))
        stats.update(seed_linguistic_sample(session, term_repo, root_service, bantu_service))
        stats.update(seed_news(session, news_repo))

        session.commit()
        logger.success(f"Release 1 alpha seed complete: {stats}")
        print("Seed complete.")
        print(json.dumps(stats, indent=2))
    except Exception:
        session.rollback()
        logger.exception("Release 1 alpha seed failed")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
