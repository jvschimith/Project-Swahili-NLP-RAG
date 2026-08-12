#!/usr/bin/env python3
"""
Script: Ingest Masakhane NER Data

Refactored to use DDD architecture.

Usage:
    python scripts/02_ingest_ner.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import init_db, get_session
from src.infrastructure.repositories.term_repository import TermRepository
from src.infrastructure.database.models import DBEntity
from src.infrastructure.config import settings
from src.infrastructure.logging_config import setup_logging
from src.domain.entities import SwahiliTerm
from loguru import logger
from tqdm import tqdm


def ingest_ner_data(file_path: Path):
    """
    Ingest Masakhane NER data.

    Format: word	B-LOC/I-LOC/O/etc
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return

    logger.info(f"Starting NER ingestion from {file_path}")

    session = get_session()
    term_repo = TermRepository(session)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    stats = {"entities_mapped": 0, "skipped": 0, "errors": 0}

    try:
        for line in tqdm(lines, desc="Processing NER data"):
            line = line.strip()
            if not line:
                continue

            try:
                parts = line.split()
                if len(parts) < 2:
                    continue

                word = parts[0].strip().lower()
                tag = parts[1].strip()

                # Skip 'O' (Outside) tags
                if tag == "O":
                    stats["skipped"] += 1
                    continue

                # Extract entity group (B-PER → PER)
                entity_group = tag.split("-")[-1]

                # Get or create term
                if not term_repo.exists(word):
                    term = SwahiliTerm(term=word)
                    term_repo.save(term)

                # Get term ID
                term_entity = term_repo.find_by_term(word)
                if not term_entity:
                    continue

                # Check if entity mapping already exists
                existing = (
                    session.query(DBEntity)
                    .filter_by(
                        term_id=term_entity.id if hasattr(term_entity, "id") else None,
                        entity_group=entity_group,
                    )
                    .first()
                )

                if not existing and hasattr(term_entity, "id"):
                    # Create entity mapping
                    entity = DBEntity(
                        term_id=term_entity.id,
                        entity_group=entity_group,
                        confidence_score=1.0,
                    )
                    session.add(entity)
                    stats["entities_mapped"] += 1

            except Exception as e:
                logger.warning(f"Error processing line '{line}': {e}")
                stats["errors"] += 1
                continue

        session.commit()
        logger.success(f"NER ingestion complete: {stats}")

    except Exception as e:
        session.rollback()
        logger.error(f"NER ingestion failed: {e}")
        raise
    finally:
        session.close()


def main():
    """Main function."""
    setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)

    logger.info("=" * 60)
    logger.info("Masakhane NER Data Ingestion")
    logger.info("=" * 60)

    init_db()

    file_path = settings.MASAKHANE_NER_FILE
    ingest_ner_data(file_path)

    logger.info("=" * 60)
    logger.info("Process complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
