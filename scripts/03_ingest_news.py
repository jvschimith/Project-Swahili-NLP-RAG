#!/usr/bin/env python3
"""
Script: Ingest Masakhane News Data

Refactored to use DDD architecture.

Usage:
    python scripts/03_ingest_news.py
"""
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import init_db, get_session
from src.infrastructure.repositories.news_repository import NewsRepository
from src.infrastructure.config import settings
from src.infrastructure.logging_config import setup_logging
from src.domain.entities import NewsArticle
from loguru import logger


def ingest_news_data(file_path: Path):
    """
    Ingest Masakhane News data.
    
    Format: TSV with columns: category, headline, text, url
    """
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return
    
    logger.info(f"Starting news ingestion from {file_path}")
    
    session = get_session()
    news_repo = NewsRepository(session)
    
    # Define column names
    column_names = ['category', 'headline', 'text', 'url']
    
    try:
        # Read TSV file
        df = pd.read_csv(
            file_path,
            sep='\t',
            names=column_names,
            skiprows=1,
            encoding='utf-8'
        )
        
        logger.info(f"Loaded {len(df)} articles")
        
        stats = {'ingested': 0, 'errors': 0}
        
        # Process each article
        for idx, row in df.iterrows():
            try:
                # Create NewsArticle entity
                article = NewsArticle(
                    content=str(row['text']),
                    category=row['category'],
                    source_url=row.get('url', None)
                )
                
                # Save
                news_repo.save(article)
                stats['ingested'] += 1
                
            except Exception as e:
                logger.warning(f"Error processing row {idx}: {e}")
                stats['errors'] += 1
                continue
        
        session.commit()
        logger.success(f"News ingestion complete: {stats}")
        
    except Exception as e:
        session.rollback()
        logger.error(f"News ingestion failed: {e}")
        raise
    finally:
        session.close()


def main():
    """Main function."""
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_file=settings.LOG_FILE
    )
    
    logger.info("=" * 60)
    logger.info("Masakhane News Data Ingestion")
    logger.info("=" * 60)
    
    init_db()
    
    file_path = settings.MASAKHANE_NEWS_FILE
    ingest_news_data(file_path)
    
    logger.info("=" * 60)
    logger.info("Process complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
