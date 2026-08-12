#!/usr/bin/env python3
"""
Script: Ingest Masakhane POS Data

Refactored to use DDD architecture.
Uses repositories and domain services.

Usage:
    python scripts/01_ingest_masakhane.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import init_db, get_session
from src.infrastructure.repositories.term_repository import TermRepository
from src.infrastructure.config import settings
from src.infrastructure.logging_config import setup_logging
from src.domain.services.bantu_classifier import BantuClassifierService
from src.domain.services.root_extractor import RootExtractorService
from src.domain.entities import SwahiliTerm, POSRecord
from src.domain.value_objects import WordType
from loguru import logger
from tqdm import tqdm


def map_pos_to_word_type(pos_tag: str) -> WordType:
    """Map POS tag to WordType."""
    mapping = {
        "NOUN": WordType.NOUN,
        "PROPN": WordType.NOUN,
        "VERB": WordType.VERB,
        "ADJ": WordType.ADJECTIVE,
        "ADV": WordType.ADVERB,
        "PRON": WordType.PRONOUN,
        "DET": WordType.DETERMINER,
        "ADP": WordType.PREPOSITION,
        "CONJ": WordType.CONJUNCTION,
    }
    return mapping.get(pos_tag.upper(), WordType.UNKNOWN)


def ingest_pos_data(file_path: Path):
    """
    Ingest Masakhane POS data.

    Args:
        file_path: Path to POS data file
    """
    # Check file exists
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return

    logger.info(f"Starting ingestion from {file_path}")

    # Initialize services
    bantu_service = BantuClassifierService()
    root_service = RootExtractorService()

    # Create session and repository
    session = get_session()
    term_repo = TermRepository(session)

    # Read file
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Statistics
    stats = {
        "sentences": 0,
        "new_terms": 0,
        "existing_terms": 0,
        "pos_records": 0,
        "errors": 0,
    }

    sentence_id = 0
    word_order = 0

    try:
        for line in tqdm(lines, desc="Processing POS data"):
            line = line.strip()

            # Empty line = sentence boundary
            if not line:
                sentence_id += 1
                word_order = 0
                stats["sentences"] += 1
                continue

            try:
                # Parse line (word	TAG)
                parts = line.split()
                if len(parts) < 2:
                    continue

                word = parts[0].strip()
                tag = parts[1].strip().upper()

                # Check if term exists
                if term_repo.exists(word):
                    stats["existing_terms"] += 1
                else:
                    # Create new term with domain services
                    word_type = map_pos_to_word_type(tag)
                    root = root_service.extract(word, word_type)
                    bantu_class = bantu_service.infer_class(word, word_type)

                    term = SwahiliTerm(
                        term=word,
                        root=root,
                        noun_class=bantu_class,
                        word_type=word_type,
                    )

                    term_repo.save(term)
                    stats["new_terms"] += 1

                word_order += 1

            except Exception as e:
                logger.warning(f"Error processing line '{line}': {e}")
                stats["errors"] += 1
                continue

        # Commit transaction
        session.commit()
        logger.success(f"Ingestion complete: {stats}")

    except Exception as e:
        session.rollback()
        logger.error(f"Ingestion failed: {e}")
        raise
    finally:
        session.close()


def main():
    """Main function."""
    # Setup logging
    setup_logging(log_level=settings.LOG_LEVEL, log_file=settings.LOG_FILE)

    logger.info("=" * 60)
    logger.info("Masakhane POS Data Ingestion")
    logger.info("=" * 60)

    # Initialize database
    logger.info("Initializing database...")
    init_db()

    # Ingest data
    file_path = settings.MASAKHANE_POS_FILE
    ingest_pos_data(file_path)

    logger.info("=" * 60)
    logger.info("Process complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
