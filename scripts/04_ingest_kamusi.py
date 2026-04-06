#!/usr/bin/env python3
"""
Script: Ingest Kamusi Dictionary Data

Ingests 16,600+ Swahili words from Kamusi dictionary.

Usage:
    python scripts/04_ingest_kamusi.py [--csv | --json]
"""
import sys
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import init_db, get_session
from src.infrastructure.repositories.term_repository import TermRepository
from src.infrastructure.repositories.dictionary_repository import DictionaryRepository
from src.infrastructure.config import settings
from src.infrastructure.logging_config import setup_logging
from src.application.use_cases.ingest_kamusi import IngestKamusiUseCase
from loguru import logger


def ingest_kamusi_csv():
    """Ingest Kamusi from CSV file."""
    session = get_session()
    
    try:
        # Create repositories
        term_repo = TermRepository(session)
        dict_repo = DictionaryRepository(session)
        
        # Create use case
        use_case = IngestKamusiUseCase(term_repo, dict_repo)
        
        # Execute
        file_path = settings.KAMUSI_CSV_FILE
        logger.info(f"Ingesting from CSV: {file_path}")
        
        stats = use_case.execute_csv(str(file_path))
        
        # Commit
        session.commit()
        
        logger.success("CSV ingestion complete!")
        logger.info(f"Statistics: {stats}")
        
    except Exception as e:
        session.rollback()
        logger.error(f"CSV ingestion failed: {e}")
        raise
    finally:
        session.close()


def ingest_kamusi_json():
    """Ingest Kamusi from JSON file."""
    session = get_session()
    
    try:
        # Create repositories
        term_repo = TermRepository(session)
        dict_repo = DictionaryRepository(session)
        
        # Create use case
        use_case = IngestKamusiUseCase(term_repo, dict_repo)
        
        # Execute
        file_path = settings.KAMUSI_JSON_FILE
        logger.info(f"Ingesting from JSON: {file_path}")
        
        stats = use_case.execute_json(str(file_path))
        
        # Commit
        session.commit()
        
        logger.success("JSON ingestion complete!")
        logger.info(f"Statistics: {stats}")
        
    except Exception as e:
        session.rollback()
        logger.error(f"JSON ingestion failed: {e}")
        raise
    finally:
        session.close()


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Ingest Kamusi Dictionary Data"
    )
    parser.add_argument(
        '--csv',
        action='store_true',
        help='Ingest from CSV file'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Ingest from JSON file'
    )
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE
    )
    
    logger.info("=" * 60)
    logger.info("Kamusi Dictionary Ingestion")
    logger.info("=" * 60)
    
    # Initialize database
    logger.info("Initializing database...")
    init_db()
    
    # Determine which format to ingest
    if args.csv:
        ingest_kamusi_csv()
    elif args.json:
        ingest_kamusi_json()
    else:
        # Default: try CSV first, then JSON
        logger.info("No format specified, trying CSV first...")
        try:
            ingest_kamusi_csv()
        except FileNotFoundError:
            logger.warning("CSV file not found, trying JSON...")
            ingest_kamusi_json()
    
    logger.info("=" * 60)
    logger.info("Process complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
