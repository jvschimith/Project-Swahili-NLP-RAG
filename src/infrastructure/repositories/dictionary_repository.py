"""
Infrastructure Layer - Dictionary Repository Implementation

Concrete implementation of IDictionaryRepository.
"""

import json

from loguru import logger
from sqlalchemy.orm import Session

from src.domain.entities import DictionaryEntry, SwahiliTerm
from src.domain.repositories import IDictionaryRepository
from src.infrastructure.database.models import DBDictionary, DBTerm


class DictionaryRepository(IDictionaryRepository):
    """
    Concrete implementation of Dictionary Repository.

    Manages Kamusi dictionary entries.
    """

    def __init__(self, session: Session):
        """Initialize with database session."""
        self.session = session

    def save(self, entry: DictionaryEntry, term_id: int) -> int:
        """
        Save dictionary entry.

        Args:
            entry: DictionaryEntry entity
            term_id: ID of associated term

        Returns:
            ID of saved entry
        """
        # Check if entry already exists
        existing = self.session.query(DBDictionary).filter_by(term_id=term_id).first()

        if existing:
            # Update existing
            existing.meaning = entry.meaning
            existing.english_translation = entry.english_translation
            existing.synonyms = json.dumps(entry.synonyms)
            existing.antonyms = json.dumps(entry.antonyms)
            existing.usage_examples = json.dumps(entry.usage_examples)
            existing.usage_context = entry.usage_context
            self.session.flush()
            logger.debug(f"Updated dictionary entry for term_id {term_id}")
            return existing.id

        # Create new entry
        db_dict = DBDictionary(
            term_id=term_id,
            meaning=entry.meaning,
            english_translation=entry.english_translation,
            synonyms=json.dumps(entry.synonyms),
            antonyms=json.dumps(entry.antonyms),
            usage_examples=json.dumps(entry.usage_examples),
            usage_context=entry.usage_context,
        )

        self.session.add(db_dict)
        self.session.flush()

        logger.debug(f"Saved dictionary entry for term_id {term_id}")
        return db_dict.id

    def find_by_term_id(self, term_id: int) -> DictionaryEntry | None:
        """
        Find dictionary entry by term ID.

        Args:
            term_id: Term ID

        Returns:
            DictionaryEntry if found, None otherwise
        """
        db_dict = self.session.query(DBDictionary).filter_by(term_id=term_id).first()

        if not db_dict:
            return None

        return self._to_domain(db_dict)

    def find_by_term_string(self, term: str) -> DictionaryEntry | None:
        """
        Find dictionary entry by term string.

        Args:
            term: Term string

        Returns:
            DictionaryEntry if found, None otherwise
        """
        # Join with terms table
        result = (
            self.session.query(DBDictionary)
            .join(DBTerm, DBDictionary.term_id == DBTerm.id)
            .filter(DBTerm.swahili_term == term.lower())
            .first()
        )

        if not result:
            return None

        return self._to_domain(result)

    def find_synonyms(self, term_id: int) -> list[str]:
        """
        Get synonyms for a term.

        Args:
            term_id: Term ID

        Returns:
            List of synonym strings
        """
        db_dict = self.session.query(DBDictionary).filter_by(term_id=term_id).first()

        if not db_dict or not db_dict.synonyms:
            return []

        try:
            return json.loads(db_dict.synonyms)
        except json.JSONDecodeError:
            return []

    def search_by_meaning(self, query: str, limit: int = 50) -> list[DictionaryEntry]:
        """
        Search entries by meaning.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching entries
        """
        db_dicts = (
            self.session.query(DBDictionary)
            .filter(DBDictionary.meaning.contains(query))
            .limit(limit)
            .all()
        )

        return [self._to_domain(db_dict) for db_dict in db_dicts]

    def _to_domain(self, db_dict: DBDictionary) -> DictionaryEntry:
        """
        Convert ORM model to domain entity.

        Args:
            db_dict: ORM model

        Returns:
            Domain entity
        """
        # Get associated term
        db_term = self.session.query(DBTerm).filter_by(id=db_dict.term_id).first()

        if not db_term:
            raise ValueError(f"Term not found for dictionary entry {db_dict.id}")

        # Create SwahiliTerm (simplified)
        from src.domain.value_objects import (
            BantuClass,
            Etymology,
            MorphologicalRoot,
            WordType,
        )

        root = None
        if db_term.root_radical:
            root = MorphologicalRoot(root=db_term.root_radical)

        term = SwahiliTerm(
            term=db_term.swahili_term,
            root=root,
            noun_class=BantuClass(db_term.noun_class),
            etymology=Etymology(db_term.etymology),
            word_type=WordType(db_term.word_type),
            is_stopword=db_term.is_stopword,
            frequency_score=db_term.frequency_score,
        )

        # Parse JSON fields
        synonyms = []
        antonyms = []
        usage_examples = []

        if db_dict.synonyms:
            try:
                synonyms = json.loads(db_dict.synonyms)
            except json.JSONDecodeError:
                pass

        if db_dict.antonyms:
            try:
                antonyms = json.loads(db_dict.antonyms)
            except json.JSONDecodeError:
                pass

        if db_dict.usage_examples:
            try:
                usage_examples = json.loads(db_dict.usage_examples)
            except json.JSONDecodeError:
                pass

        return DictionaryEntry(
            term=term,
            meaning=db_dict.meaning,
            english_translation=db_dict.english_translation,
            synonyms=synonyms,
            antonyms=antonyms,
            usage_examples=usage_examples,
            usage_context=db_dict.usage_context,
        )
