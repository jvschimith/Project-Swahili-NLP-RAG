"""
Infrastructure Layer - News Repository Implementation

Concrete implementation of INewsRepository interface.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from loguru import logger

from src.domain.repositories import INewsRepository
from src.domain.entities import NewsArticle
from src.domain.value_objects import SentimentScore
from src.infrastructure.database.models import DBNews


class NewsRepository(INewsRepository):
    """
    Concrete implementation of News Repository.
    
    Manages persistence of news articles.
    """
    
    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session
    
    def save(self, article: NewsArticle) -> int:
        """
        Save news article.
        
        Args:
            article: NewsArticle entity
            
        Returns:
            ID of saved article
        """
        db_news = DBNews(
            content=article.content,
            category=article.category,
            source_url=article.source_url,
            date_published=article.date_published or datetime.utcnow()
        )
        
        # Add sentiment if available
        if article.sentiment_score:
            db_news.sentiment_polarity = article.sentiment_score.polarity
            db_news.sentiment_confidence = article.sentiment_score.confidence
            db_news.sentiment_label = article.sentiment_score.label
        
        self.session.add(db_news)
        self.session.flush()
        
        logger.debug(f"Saved news article with ID {db_news.id}")
        return db_news.id
    
    def find_by_id(self, article_id: int) -> Optional[NewsArticle]:
        """Find article by ID."""
        db_news = self.session.query(DBNews).filter_by(id=article_id).first()
        
        if not db_news:
            return None
        
        return self._to_domain(db_news)
    
    def find_all(self, limit: int = 100, offset: int = 0) -> List[NewsArticle]:
        """Get all articles (paginated)."""
        db_news_list = self.session.query(DBNews).order_by(
            desc(DBNews.date_published)
        ).limit(limit).offset(offset).all()
        
        return [self._to_domain(db_news) for db_news in db_news_list]
    
    def find_by_category(self, category: str, limit: int = 100) -> List[NewsArticle]:
        """Find articles by category."""
        db_news_list = self.session.query(DBNews).filter_by(
            category=category
        ).order_by(desc(DBNews.date_published)).limit(limit).all()
        
        return [self._to_domain(db_news) for db_news in db_news_list]
    
    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100
    ) -> List[NewsArticle]:
        """Find articles in date range."""
        db_news_list = self.session.query(DBNews).filter(
            DBNews.date_published >= start_date,
            DBNews.date_published <= end_date
        ).order_by(desc(DBNews.date_published)).limit(limit).all()
        
        return [self._to_domain(db_news) for db_news in db_news_list]
    
    def find_with_sentiment(
        self,
        sentiment_label: str,
        limit: int = 100
    ) -> List[NewsArticle]:
        """Find articles by sentiment."""
        db_news_list = self.session.query(DBNews).filter_by(
            sentiment_label=sentiment_label
        ).limit(limit).all()
        
        return [self._to_domain(db_news) for db_news in db_news_list]
    
    def count(self) -> int:
        """Count total articles."""
        return self.session.query(DBNews).count()
    
    def count_by_category(self) -> dict:
        """Count articles by category."""
        results = self.session.query(
            DBNews.category,
            self.session.query(DBNews).filter(
                DBNews.category == DBNews.category
            ).count()
        ).group_by(DBNews.category).all()
        
        return {category: count for category, count in results}
    
    def _to_domain(self, db_news: DBNews) -> NewsArticle:
        """Convert ORM model to domain entity."""
        sentiment_score = None
        if db_news.sentiment_polarity is not None:
            sentiment_score = SentimentScore(
                polarity=db_news.sentiment_polarity,
                confidence=db_news.sentiment_confidence or 1.0
            )
        
        return NewsArticle(
            content=db_news.content,
            category=db_news.category,
            date_published=db_news.date_published,
            sentiment_score=sentiment_score,
            source_url=db_news.source_url,
            created_at=db_news.created_at
        )
