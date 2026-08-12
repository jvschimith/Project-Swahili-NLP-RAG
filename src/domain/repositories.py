"""
Domain Layer - Repository Interfaces

Repositories are abstractions that encapsulate data-access logic.
They are interfaces (contracts) defined in the domain and implemented in
the infrastructure layer.

They follow the Repository Pattern:
- Interface in the Domain Layer (this file)
- Implementation in the Infrastructure Layer
- Allows implementations to change without affecting the domain

Benefits:
- Testability (easy mocking)
- Dependency inversion (DIP)
- Separation of concerns
- Implementation flexibility
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .entities import (
    SwahiliTerm,
    DictionaryEntry,
    VerbConjugation,
    POSRecord,
    NewsArticle
)
from .value_objects import BantuClass, WordType, Etymology


class ITermRepository(ABC):
    """
    Interface: Repository of Swahili terms.

    Responsibility: Manage persistence of vocabulary terms.
    
    Design Decisions:
        - Search by term string is the most common use case
        - Exists() avoids unnecessary queries
        - Frequency updates are common operations (optimize them)
    """
    
    @abstractmethod
    def save(self, term: SwahiliTerm) -> int:
        """
        Persist a term in the repository.
        
        Args:
            term: SwahiliTerm entity to persist
            
        Returns:
            Saved term ID
            
        Raises:
            ValueError: If the term already exists (uniqueness constraint)
        """
        pass
    
    @abstractmethod
    def find_by_id(self, term_id: int) -> Optional[SwahiliTerm]:
        """
        Search for a term by ID.
        
        Args:
            term_id: Unique term identifier
            
        Returns:
            SwahiliTerm if found, otherwise None
        """
        pass
    
    @abstractmethod
    def find_by_term(self, term: str) -> Optional[SwahiliTerm]:
        """
        Search for a term by its string value (case-insensitive).
        
        Args:
            term: Swahili word
            
        Returns:
            SwahiliTerm if found, otherwise None
        """
        pass
    
    @abstractmethod
    def exists(self, term: str) -> bool:
        """
        Check whether a term exists without loading the object.
        
        Args:
            term: Swahili word
            
        Returns:
            True if it exists, False otherwise
        """
        pass
    
    @abstractmethod
    def find_by_bantu_class(self, bantu_class: BantuClass, limit: int = 100) -> List[SwahiliTerm]:
        """
        Search for terms by Bantu class.
        
        Args:
            bantu_class: Bantu noun class
            limit: Maximum number of results
            
        Returns:
            List of terms in the specified class
        """
        pass
    
    @abstractmethod
    def find_by_etymology(self, etymology: Etymology, limit: int = 100) -> List[SwahiliTerm]:
        """
        Search for terms by etymological origin.
        
        Args:
            etymology: Word origin
            limit: Maximum number of results
            
        Returns:
            List of terms with the specified origin
        """
        pass
    
    @abstractmethod
    def find_stopwords(self) -> List[SwahiliTerm]:
        """
        Return all terms marked as stopwords.
        
        Returns:
            List of stopwords
        """
        pass
    
    @abstractmethod
    def update_frequency(self, term_id: int, increment: float) -> None:
        """
        Update a term's usage frequency.

        Optimization: This operation should be efficient because it is
        called frequently during corpus processing.
        
        Args:
            term_id: Term ID
            increment: Increment value
        """
        pass
    
    @abstractmethod
    def get_most_frequent(self, limit: int = 100, exclude_stopwords: bool = True) -> List[SwahiliTerm]:
        """
        Return the most frequent terms.
        
        Args:
            limit: Maximum number of terms
            exclude_stopwords: If True, exclude stopwords
            
        Returns:
            List ordered by descending frequency
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Return the total number of terms.
        
        Returns:
            Number of terms in the repository
        """
        pass


class IDictionaryRepository(ABC):
    """
    Interface: Repository of dictionary entries.

    Responsibility: Manage persistence of Kamusi definitions.
    """
    
    @abstractmethod
    def save(self, entry: DictionaryEntry, term_id: int) -> int:
        """
        Persist a dictionary entry.
        
        Args:
            entry: Complete dictionary entry
            term_id: Associated term ID
            
        Returns:
            Saved entry ID
        """
        pass
    
    @abstractmethod
    def find_by_term_id(self, term_id: int) -> Optional[DictionaryEntry]:
        """
        Search for a dictionary entry by term ID.
        
        Args:
            term_id: Term ID
            
        Returns:
            DictionaryEntry if found, otherwise None
        """
        pass
    
    @abstractmethod
    def find_by_term_string(self, term: str) -> Optional[DictionaryEntry]:
        """
        Search for an entry by word string (convenience method).
        
        Args:
            term: Swahili word
            
        Returns:
            DictionaryEntry if found, otherwise None
        """
        pass
    
    @abstractmethod
    def find_synonyms(self, term_id: int) -> List[str]:
        """
        Return synonyms for a term.
        
        Args:
            term_id: Term ID
            
        Returns:
            List of synonyms
        """
        pass
    
    @abstractmethod
    def search_by_meaning(self, query: str, limit: int = 50) -> List[DictionaryEntry]:
        """
        Search entries by similarity in meaning.
        
        Args:
            query: Text to search in the meaning
            limit: Maximum number of results
            
        Returns:
            List of entries that contain the query
        """
        pass


class IConjugationRepository(ABC):
    """
    Interface: Repository of verb conjugations.

    Responsibility: Manage Swahili verb conjugations.
    """
    
    @abstractmethod
    def save(self, conjugation: VerbConjugation, verb_id: int) -> int:
        """
        Persist a verb conjugation.
        
        Args:
            conjugation: Conjugated form
            verb_id: Verb ID (term)
            
        Returns:
            Saved conjugation ID
        """
        pass
    
    @abstractmethod
    def find_by_verb(self, verb_id: int) -> List[VerbConjugation]:
        """
        Return all conjugations of a verb.
        
        Args:
            verb_id: Verb ID
            
        Returns:
            List of conjugations
        """
        pass
    
    @abstractmethod
    def find_by_tense(self, verb_id: int, tense: str) -> List[VerbConjugation]:
        """
        Search conjugations by tense.
        
        Args:
            verb_id: Verb ID
            tense: Verb tense (present, past, etc.)
            
        Returns:
            List of conjugations in the specified tense
        """
        pass
    
    @abstractmethod
    def find_by_person(self, verb_id: int, person: str) -> List[VerbConjugation]:
        """
        Search conjugations by grammatical person.
        
        Args:
            verb_id: Verb ID
            person: Person (1sg, 2sg, etc.)
            
        Returns:
            List of conjugations for the specified person
        """
        pass


class IPOSRepository(ABC):
    """
    Interface: Repository of POS (Part-of-Speech) annotations.

    Responsibility: Manage Masakhane-POS data.
    """
    
    @abstractmethod
    def save(self, pos_record: POSRecord, term_id: int) -> int:
        """
        Persist a POS record.
        
        Args:
            pos_record: Grammatical annotation
            term_id: Annotated term ID
            
        Returns:
            Saved record ID
        """
        pass
    
    @abstractmethod
    def find_by_sentence(self, sentence_id: int) -> List[POSRecord]:
        """
        Return all records for a sentence.
        
        Args:
            sentence_id: Sentence ID
            
        Returns:
            List of records ordered by word_order
        """
        pass
    
    @abstractmethod
    def find_by_tag(self, tag: str, limit: int = 100) -> List[POSRecord]:
        """
        Search records by grammatical tag.
        
        Args:
            tag: Grammatical tag (NOUN, VERB, etc.)
            limit: Maximum number of results
            
        Returns:
            List of records with the specified tag
        """
        pass
    
    @abstractmethod
    def count_by_tag(self) -> dict:
        """
        Return record counts by tag.
        
        Returns:
            Dictionary {tag: count}
        """
        pass


class INewsRepository(ABC):
    """
    Interface: Repository of news articles.

    Responsibility: Manage the Masakhane-News corpus.
    """
    
    @abstractmethod
    def save(self, article: NewsArticle) -> int:
        """
        Persist a news article.
        
        Args:
            article: Full article
            
        Returns:
            Saved article ID
        """
        pass
    
    @abstractmethod
    def find_by_id(self, article_id: int) -> Optional[NewsArticle]:
        """
        Search for an article by ID.
        
        Args:
            article_id: Article ID
            
        Returns:
            NewsArticle if found, otherwise None
        """
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[NewsArticle]:
        """
        Return all articles (paginated).
        
        Args:
            limit: Maximum number of articles
            offset: Pagination offset
            
        Returns:
            List of articles
        """
        pass
    
    @abstractmethod
    def find_by_category(self, category: str, limit: int = 100) -> List[NewsArticle]:
        """
        Search articles by category.
        
        Args:
            category: Category (Kitaifa, Kimataifa, etc.)
            limit: Maximum number of results
            
        Returns:
            List of articles in the category
        """
        pass
    
    @abstractmethod
    def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 100
    ) -> List[NewsArticle]:
        """
        Search articles within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            limit: Maximum number of results
            
        Returns:
            List of articles in the period
        """
        pass
    
    @abstractmethod
    def find_with_sentiment(
        self,
        sentiment_label: str,
        limit: int = 100
    ) -> List[NewsArticle]:
        """
        Search articles by sentiment.
        
        Args:
            sentiment_label: Sentiment label (positive, negative, neutral)
            limit: Maximum number of results
            
        Returns:
            List of articles with the specified sentiment
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Return the total article count.
        
        Returns:
            Number of articles in the repository
        """
        pass
    
    @abstractmethod
    def count_by_category(self) -> dict:
        """
        Return article counts by category.
        
        Returns:
            Dictionary {category: count}
        """
        pass


# Type hints for convenience
TermRepo = ITermRepository
DictRepo = IDictionaryRepository
ConjugRepo = IConjugationRepository
POSRepo = IPOSRepository
NewsRepo = INewsRepository


# Usage example (for tests/documentation)
if __name__ == "__main__":
    print("Repository Interfaces - Domain Layer")
    print("\nAvailable interfaces:")
    print("- ITermRepository: Manages Swahili terms")
    print("- IDictionaryRepository: Manages dictionary entries")
    print("- IConjugationRepository: Manages verb conjugations")
    print("- IPOSRepository: Manages POS annotations")
    print("- INewsRepository: Manages the news corpus")
    print("\nThese interfaces are implemented in the Infrastructure Layer.")
