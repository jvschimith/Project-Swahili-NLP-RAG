"""
Infrastructure Layer - Database Connection

Database connection management using SQLAlchemy.
"""

from collections.abc import Generator
from contextlib import contextmanager

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings
from .models import Base

# Create engine
# Add timeout for SQLite to prevent "database is locked" errors
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    connect_args=(
        {"timeout": 30, "check_same_thread": False}
        if "sqlite" in settings.DATABASE_URL
        else {}
    ),
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Initialize database schema."""
    Base.metadata.create_all(bind=engine)
    logger.info("Database schema initialized")


def get_session() -> Session:
    """Get a database session."""
    return SessionLocal()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_db_context() as db:
            db.query(DBTerm).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
