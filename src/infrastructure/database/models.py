"""
Infrastructure Layer - ORM Models

SQLAlchemy ORM models for database persistence.
"""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DBTerm(Base):
    """ORM Model: Core Vocabulary table."""

    __tablename__ = "terms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    swahili_term = Column(String(100), unique=True, nullable=False, index=True)
    root_radical = Column(String(50), index=True)
    noun_class = Column(String(20), default="N/A")
    etymology = Column(String(20), default="unknown")
    word_type = Column(String(20), default="unknown")
    is_stopword = Column(Boolean, default=False, index=True)
    frequency_score = Column(Float, default=0.0, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    pos_records = relationship(
        "DBPOS", back_populates="term", cascade="all, delete-orphan"
    )
    sentiment_records = relationship(
        "DBSentiment", back_populates="term", cascade="all, delete-orphan"
    )
    entity_records = relationship(
        "DBEntity", back_populates="term", cascade="all, delete-orphan"
    )
    dictionary_entry = relationship(
        "DBDictionary",
        back_populates="term",
        uselist=False,
        cascade="all, delete-orphan",
    )
    conjugations = relationship(
        "DBConjugation", back_populates="verb", cascade="all, delete-orphan"
    )


class DBDictionary(Base):
    """ORM Model: Kamusi Dictionary entries."""

    __tablename__ = "dictionary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey("terms.id"), unique=True, nullable=False)
    meaning = Column(Text, nullable=False)
    english_translation = Column(Text)
    synonyms = Column(Text)
    antonyms = Column(Text)
    usage_examples = Column(Text)
    usage_context = Column(String(50))

    term = relationship("DBTerm", back_populates="dictionary_entry")


class DBConjugation(Base):
    """ORM Model: Verb conjugations."""

    __tablename__ = "conjugations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verb_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    tense = Column(String(20), nullable=False)
    person = Column(String(10), nullable=False)
    form = Column(String(50), nullable=False)
    prefix_chain = Column(String(20))
    is_affirmative = Column(Boolean, default=True)

    verb = relationship("DBTerm", back_populates="conjugations")


class DBPOS(Base):
    """ORM Model: Part-of-Speech annotations."""

    __tablename__ = "grammar_pos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    tag = Column(String(20), nullable=False, index=True)
    prefix_chain = Column(String(20))
    sentence_id = Column(Integer, index=True)
    word_order = Column(Integer)
    confidence = Column(Float, default=1.0)

    term = relationship("DBTerm", back_populates="pos_records")


class DBSentiment(Base):
    """ORM Model: Sentiment analysis results."""

    __tablename__ = "sentiment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey("terms.id"))
    polarity_score = Column(Float, nullable=False)
    confidence = Column(Float, default=1.0)
    label = Column(String(20), index=True)

    term = relationship("DBTerm", back_populates="sentiment_records")


class DBEntity(Base):
    """ORM Model: Named Entity Recognition."""

    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    term_id = Column(Integer, ForeignKey("terms.id"), nullable=False)
    entity_group = Column(String(20), nullable=False, index=True)
    confidence_score = Column(Float, default=1.0)

    term = relationship("DBTerm", back_populates="entity_records")


class DBNews(Base):
    """ORM Model: News articles."""

    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), index=True)
    source_url = Column(String(500))
    date_published = Column(DateTime, default=datetime.utcnow, index=True)
    sentiment_polarity = Column(Float)
    sentiment_confidence = Column(Float)
    sentiment_label = Column(String(20), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DBSchemaVersion(Base):
    """ORM Model: Database schema versioning."""

    __tablename__ = "schema_version"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String(20), nullable=False, unique=True)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    description = Column(Text)
