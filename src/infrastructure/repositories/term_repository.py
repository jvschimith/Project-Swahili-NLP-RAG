"""
Infrastructure Layer - Term Repository Implementation

Concrete implementation of ITermRepository interface.
Maps between domain entities and ORM models.
"""

from loguru import logger
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.domain.entities import SwahiliTerm
from src.domain.repositories import ITermRepository
from src.domain.value_objects import BantuClass, Etymology, MorphologicalRoot, WordType
from src.infrastructure.database.models import DBTerm


class TermRepository(ITermRepository):
    """
    Concrete implementation of Term Repository.

    Responsibilities:
    - Persist and retrieve SwahiliTerm entities
    - Map between domain entities and ORM models
    - Handle database transactions

    Examples:
        >>> session = get_session()
        >>> repo = TermRepository(session)
        >>> term = SwahiliTerm(term="mtu", noun_class=BantuClass.M_WA)
        >>> term_id = repo.save(term)
        >>> found = repo.find_by_term("mtu")
    """

    def __init__(self, session: Session):
        """
        Initialize repository with database session.

        Args:
            session: SQLAlchemy session
        """
        self.session = session

    def save(self, term: SwahiliTerm) -> int:
        """
        Save a term to the database.

        Args:
            term: SwahiliTerm entity

        Returns:
            ID of saved term

        Raises:
            ValueError: If term already exists
        """
        # Check if term already exists
        existing = self.session.query(DBTerm).filter_by(swahili_term=term.term).first()

        if existing:
            raise ValueError(f"Term '{term.term}' already exists with ID {existing.id}")

        # Create ORM model
        db_term = DBTerm(
            swahili_term=term.term,
            root_radical=term.root.root if term.root else None,
            noun_class=term.noun_class.value,
            etymology=term.etymology.value,
            word_type=term.word_type.value,
            is_stopword=term.is_stopword,
            frequency_score=term.frequency_score,
        )

        self.session.add(db_term)
        self.session.flush()  # Get ID without committing

        logger.debug(f"Saved term '{term.term}' with ID {db_term.id}")
        return db_term.id

    def find_by_id(self, term_id: int) -> SwahiliTerm | None:
        """
        Find term by ID.

        Args:
            term_id: Term ID

        Returns:
            SwahiliTerm if found, None otherwise
        """
        db_term = self.session.query(DBTerm).filter_by(id=term_id).first()

        if not db_term:
            return None

        return self._to_domain(db_term)

    def find_by_term(self, term: str) -> SwahiliTerm | None:
        """
        Find term by string (case-insensitive).

        Args:
            term: Term string

        Returns:
            SwahiliTerm if found, None otherwise
        """
        normalized = term.lower().strip()
        db_term = self.session.query(DBTerm).filter_by(swahili_term=normalized).first()

        if not db_term:
            return None

        return self._to_domain(db_term)

    def exists(self, term: str) -> bool:
        """
        Check if term exists without loading full object.

        Args:
            term: Term string

        Returns:
            True if exists, False otherwise
        """
        normalized = term.lower().strip()
        count = self.session.query(DBTerm).filter_by(swahili_term=normalized).count()
        return count > 0

    def find_by_bantu_class(
        self, bantu_class: BantuClass, limit: int = 100
    ) -> list[SwahiliTerm]:
        """
        Find terms by Bantu class.

        Args:
            bantu_class: Bantu noun class
            limit: Maximum number of results

        Returns:
            List of terms
        """
        db_terms = (
            self.session.query(DBTerm)
            .filter_by(noun_class=bantu_class.value)
            .limit(limit)
            .all()
        )

        return [self._to_domain(db_term) for db_term in db_terms]

    def find_by_etymology(
        self, etymology: Etymology, limit: int = 100
    ) -> list[SwahiliTerm]:
        """
        Find terms by etymology.

        Args:
            etymology: Word origin
            limit: Maximum number of results

        Returns:
            List of terms
        """
        db_terms = (
            self.session.query(DBTerm)
            .filter_by(etymology=etymology.value)
            .limit(limit)
            .all()
        )

        return [self._to_domain(db_term) for db_term in db_terms]

    def find_stopwords(self) -> list[SwahiliTerm]:
        """
        Get all stopwords.

        Returns:
            List of stopword terms
        """
        db_terms = self.session.query(DBTerm).filter_by(is_stopword=True).all()

        return [self._to_domain(db_term) for db_term in db_terms]

    def update_frequency(self, term_id: int, increment: float) -> None:
        """
        Update term frequency (optimized query).

        Args:
            term_id: Term ID
            increment: Amount to increment
        """
        db_term = self.session.query(DBTerm).filter_by(id=term_id).first()

        if db_term:
            db_term.frequency_score += increment
            self.session.flush()
            logger.debug(f"Updated frequency for term ID {term_id}: +{increment}")

    def get_most_frequent(
        self, limit: int = 100, exclude_stopwords: bool = True
    ) -> list[SwahiliTerm]:
        """
        Get most frequent terms.

        Args:
            limit: Maximum number of results
            exclude_stopwords: Exclude stopwords if True

        Returns:
            List of terms ordered by frequency (descending)
        """
        query = self.session.query(DBTerm)

        if exclude_stopwords:
            query = query.filter_by(is_stopword=False)

        db_terms = query.order_by(desc(DBTerm.frequency_score)).limit(limit).all()

        return [self._to_domain(db_term) for db_term in db_terms]

    def count(self) -> int:
        """
        Count total terms.

        Returns:
            Number of terms
        """
        return self.session.query(DBTerm).count()

    def _to_domain(self, db_term: DBTerm) -> SwahiliTerm:
        """
        Convert ORM model to domain entity.

        Args:
            db_term: ORM model

        Returns:
            Domain entity
        """
        # Reconstruct morphological root if available
        root = None
        if db_term.root_radical:
            root = MorphologicalRoot(root=db_term.root_radical)

        return SwahiliTerm(
            term=db_term.swahili_term,
            root=root,
            noun_class=BantuClass(db_term.noun_class),
            etymology=Etymology(db_term.etymology),
            word_type=WordType(db_term.word_type),
            is_stopword=db_term.is_stopword,
            frequency_score=db_term.frequency_score,
            created_at=db_term.created_at,
            updated_at=db_term.updated_at,
        )


# Usage example
if __name__ == "__main__":
    from src.infrastructure.database import get_session, init_db

    print("=== Term Repository Test ===\n")

    # Initialize database
    init_db()

    # Create session
    session = get_session()

    try:
        # Create repository
        repo = TermRepository(session)

        # Create and save a term
        term = SwahiliTerm(
            term="mtu",
            noun_class=BantuClass.M_WA,
            word_type=WordType.NOUN,
            etymology=Etymology.BANTU,
        )

        if not repo.exists("mtu"):
            term_id = repo.save(term)
            print(f"✓ Saved term 'mtu' with ID: {term_id}")
        else:
            print("✓ Term 'mtu' already exists")

        # Find by term
        found = repo.find_by_term("mtu")
        if found:
            print(f"✓ Found term: {found.term} ({found.word_type.value})")
            print(f"  Bantu Class: {found.noun_class.value}")
            print(f"  Etymology: {found.etymology.value}")

        # Count terms
        total = repo.count()
        print(f"\n✓ Total terms in database: {total}")

        # Commit
        session.commit()
        print("\n✓ Repository test complete!")

    except Exception as e:
        session.rollback()
        print(f"\n✗ Error: {e}")
    finally:
        session.close()
