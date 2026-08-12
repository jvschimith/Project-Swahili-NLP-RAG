#!/usr/bin/env python3
"""
Script: Backup and Export News Articles

Monthly backup of analyzed articles.

Usage:
    python scripts/backup_articles.py
"""
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import get_session
from src.infrastructure.repositories.news_repository import NewsRepository
from loguru import logger

def backup_articles():
    """Backup all articles to CSV and Parquet."""
    
    # Create backup directory
    backup_dir = Path("data/backups")
    backup_dir.mkdir(exist_ok=True)
    
    # Get all articles
    session = get_session()
    news_repo = NewsRepository(session)
    
    articles = news_repo.find_all(limit=100000)  # Get all
    
    if not articles:
        logger.warning("No articles to backup")
        return
    
    # Convert to DataFrame
    data = []
    for article in articles:
        data.append({
            'content': article.content,
            'category': article.category,
            'date_published': article.date_published,
            'sentiment_label': article.sentiment_label,
            'sentiment_polarity': article.sentiment_score.polarity if article.sentiment_score else None,
            'source_url': article.source_url,
            'created_at': article.created_at
        })
    
    df = pd.DataFrame(data)
    
    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    # Save as CSV (human-readable)
    csv_file = backup_dir / f"articles_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    logger.info(f"Saved CSV: {csv_file} ({len(df)} articles)")
    
    # Save as Parquet (compressed, efficient)
    parquet_file = backup_dir / f"articles_{timestamp}.parquet"
    df.to_parquet(parquet_file, compression='gzip')
    logger.info(f"Saved Parquet: {parquet_file}")
    
    # Save metadata
    metadata = {
        'backup_date': timestamp,
        'article_count': len(df),
        'date_range': {
            'earliest': str(df['created_at'].min()),
            'latest': str(df['created_at'].max())
        },
        'categories': df['category'].value_counts().to_dict(),
        'sentiment_distribution': df['sentiment_label'].value_counts().to_dict()
    }
    
    import json
    meta_file = backup_dir / f"metadata_{timestamp}.json"
    with open(meta_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    logger.success(f"Backup complete: {len(df)} articles")
    
    # Database backup (copy SQLite file)
    import shutil
    db_file = Path("data/swahili_knowledge.db")
    if db_file.exists():
        db_backup = backup_dir / f"database_{timestamp}.db"
        shutil.copy2(db_file, db_backup)
        logger.info(f"Database backed up: {db_backup}")
    
    session.close()

if __name__ == "__main__":
    logger.info("Starting backup...")
    backup_articles()
    logger.info("Backup complete!")
