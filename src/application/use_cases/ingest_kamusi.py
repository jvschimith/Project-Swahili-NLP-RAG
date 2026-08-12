"""
Application Layer - Ingest Kamusi Dictionary

Use case for ingesting Kamusi dictionary data.
Integrates 16,600+ Swahili words with definitions.
"""
from pathlib import Path
from typing import Dict
import csv
import json
from loguru import logger
from tqdm import tqdm

from src.domain.repositories import ITermRepository, IDictionaryRepository
from src.domain.entities import SwahiliTerm, DictionaryEntry
from src.domain.services.bantu_classifier import BantuClassifierService
from src.domain.services.root_extractor import RootExtractorService
from src.domain.value_objects import WordType, Etymology


class IngestKamusiUseCase:
    """
    Use Case: Ingest Kamusi Dictionary.
    
    Processes Kamusi CSV/JSON data and stores:
    - Terms with metadata
    - Dictionary entries with meanings
    - Synonyms and usage examples
    
    Examples:
        >>> use_case = IngestKamusiUseCase(term_repo, dict_repo)
        >>> stats = use_case.execute("data/raw/kamusi/words.csv")
    """
    
    def __init__(
        self,
        term_repo: ITermRepository,
        dict_repo: IDictionaryRepository,
        bantu_service: BantuClassifierService = None,
        root_service: RootExtractorService = None
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            term_repo: Term repository
            dict_repo: Dictionary repository
            bantu_service: Bantu classification service
            root_service: Root extraction service
        """
        self.term_repo = term_repo
        self.dict_repo = dict_repo
        self.bantu_service = bantu_service or BantuClassifierService()
        self.root_service = root_service or RootExtractorService()
    
    def execute_csv(self, file_path: str, batch_size: int = 1000) -> Dict[str, int]:
        """
        Execute Kamusi ingestion from CSV file.
        
        Args:
            file_path: Path to Kamusi CSV file
            batch_size: Batch size for commits
            
        Returns:
            Statistics dictionary
            
        CSV Format:
            word,meaning,synonyms,english,examples
        """
        logger.info(f"Starting Kamusi CSV ingestion from {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stats = {
            'total_rows': 0,
            'new_terms': 0,
            'existing_terms': 0,
            'dictionary_entries': 0,
            'errors': 0
        }
        
        # Read CSV
        with open(path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            
            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(sample)
                delimiter = dialect.delimiter
            except:
                delimiter = ','
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in tqdm(reader, desc="Processing Kamusi data"):
                stats['total_rows'] += 1
                
                try:
                    # Extract fields (handle different CSV formats)
                    word = row.get('word', row.get('Word', '')).strip().lower()
                    meaning = row.get('meaning', row.get('Meaning', '')).strip()
                    english = row.get('english', row.get('English', '')).strip()
                    synonyms_str = row.get('synonyms', row.get('Synonyms', '')).strip()
                    examples_str = row.get('examples', row.get('Examples', '')).strip()
                    
                    if not word or not meaning:
                        continue
                    
                    # Get or create term
                    term_id = self._get_or_create_term(word)
                    
                    if term_id is None:
                        stats['errors'] += 1
                        continue
                    
                    # Parse synonyms
                    synonyms = []
                    if synonyms_str:
                        synonyms = [s.strip() for s in synonyms_str.split(',')]
                    
                    # Parse examples
                    examples = []
                    if examples_str:
                        examples = [e.strip() for e in examples_str.split(';')]
                    
                    # Create dictionary entry
                    term_entity = self.term_repo.find_by_term(word)
                    if not term_entity:
                        continue
                    
                    entry = DictionaryEntry(
                        term=term_entity,
                        meaning=meaning,
                        english_translation=english if english else None,
                        synonyms=synonyms,
                        usage_examples=examples
                    )
                    
                    self.dict_repo.save(entry, term_id)
                    stats['dictionary_entries'] += 1
                    
                except Exception as e:
                    logger.warning(f"Error processing row: {e}")
                    stats['errors'] += 1
                    continue
        
        logger.success(f"Kamusi CSV ingestion complete: {stats}")
        return stats
    
    def execute_json(self, file_path: str) -> Dict[str, int]:
        """
        Execute Kamusi ingestion from JSON file.
        
        Args:
            file_path: Path to Kamusi JSON file
            
        Returns:
            Statistics dictionary
            
        JSON Format:
            [
                {
                    "word": "mtu",
                    "meaning": "binadamu",
                    "english": "person",
                    "synonyms": ["binadamu", "mwanadamu"],
                    "examples": ["Mtu huyu ni rafiki"]
                },
                ...
            ]
        """
        logger.info(f"Starting Kamusi JSON ingestion from {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        stats = {
            'total_entries': 0,
            'new_terms': 0,
            'existing_terms': 0,
            'dictionary_entries': 0,
            'errors': 0
        }
        
        # Read JSON
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("JSON must be a list of dictionary entries")
        
        stats['total_entries'] = len(data)
        
        for item in tqdm(data, desc="Processing Kamusi JSON"):
            try:
                word = item.get('word', '').strip().lower()
                meaning = item.get('meaning', '').strip()
                english = item.get('english', '').strip()
                synonyms = item.get('synonyms', [])
                examples = item.get('examples', [])
                
                if not word or not meaning:
                    continue
                
                # Get or create term
                term_id = self._get_or_create_term(word)
                
                if term_id is None:
                    stats['errors'] += 1
                    continue
                
                # Create dictionary entry
                term_entity = self.term_repo.find_by_term(word)
                if not term_entity:
                    continue
                
                entry = DictionaryEntry(
                    term=term_entity,
                    meaning=meaning,
                    english_translation=english if english else None,
                    synonyms=synonyms if isinstance(synonyms, list) else [],
                    usage_examples=examples if isinstance(examples, list) else []
                )
                
                self.dict_repo.save(entry, term_id)
                stats['dictionary_entries'] += 1
                
            except Exception as e:
                logger.warning(f"Error processing entry: {e}")
                stats['errors'] += 1
                continue
        
        logger.success(f"Kamusi JSON ingestion complete: {stats}")
        return stats
    
    def _get_or_create_term(self, word: str) -> int:
        """
        Get existing term ID or create new term.
        
        Args:
            word: Word string
            
        Returns:
            Term ID
        """
        # Check if term exists
        if self.term_repo.exists(word):
            existing = self.term_repo.find_by_term(word)
            # Store that it exists
            return existing.id if hasattr(existing, 'id') else None
        
        # Infer word type (assume noun for dictionary words)
        word_type = WordType.NOUN
        
        # Apply domain services
        root = self.root_service.extract(word, word_type)
        bantu_class = self.bantu_service.infer_class(word, word_type)
        
        # Create entity
        term = SwahiliTerm(
            term=word,
            root=root,
            noun_class=bantu_class,
            word_type=word_type,
            etymology=Etymology.UNKNOWN  # Can be enhanced
        )
        
        # Save
        term_id = self.term_repo.save(term)
        return term_id


# Usage example
if __name__ == "__main__":
    from src.infrastructure.database import init_db, get_session
    from src.infrastructure.repositories.term_repository import TermRepository
    from src.infrastructure.repositories.dictionary_repository import DictionaryRepository
    
    print("=== Ingest Kamusi Use Case Test ===\n")
    
    # Initialize database
    init_db()
    
    # Create session
    session = get_session()
    
    try:
        # Create repositories
        term_repo = TermRepository(session)
        dict_repo = DictionaryRepository(session)
        
        # Create use case
        use_case = IngestKamusiUseCase(term_repo, dict_repo)
        
        print("✓ Use case initialized successfully")
        print("  (Execute with actual Kamusi data file to ingest)")
        
        # Example execution:
        # stats = use_case.execute_csv("data/raw/kamusi/words.csv")
        # stats = use_case.execute_json("data/raw/kamusi/words.json")
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error: {e}")
    finally:
        session.close()
