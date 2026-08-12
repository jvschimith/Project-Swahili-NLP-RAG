"""
Application Layer - Ingest Masakhane Use Case

Use case for ingesting Masakhane POS/NER data.
Orchestrates domain services and repositories.
"""
from pathlib import Path
from typing import Dict
from loguru import logger
from tqdm import tqdm

from src.domain.repositories import ITermRepository, IPOSRepository
from src.domain.entities import SwahiliTerm, POSRecord
from src.domain.services.bantu_classifier import BantuClassifierService
from src.domain.services.root_extractor import RootExtractorService
from src.domain.value_objects import WordType


class IngestMasakhaneUseCase:
    """
    Use Case: Ingest Masakhane POS data.
    
    Orchestrates:
    - File reading
    - Entity creation
    - Domain service application
    - Repository persistence
    
    Examples:
        >>> use_case = IngestMasakhaneUseCase(term_repo, pos_repo)
        >>> stats = use_case.execute("data/raw/pos_swa_test.txt")
    """
    
    def __init__(
        self,
        term_repo: ITermRepository,
        pos_repo: IPOSRepository,
        bantu_service: BantuClassifierService = None,
        root_service: RootExtractorService = None
    ):
        """
        Initialize use case with dependencies.
        
        Args:
            term_repo: Term repository
            pos_repo: POS repository
            bantu_service: Bantu classification service
            root_service: Root extraction service
        """
        self.term_repo = term_repo
        self.pos_repo = pos_repo
        self.bantu_service = bantu_service or BantuClassifierService()
        self.root_service = root_service or RootExtractorService()
    
    def execute(self, file_path: str, batch_size: int = 1000) -> Dict[str, int]:
        """
        Execute Masakhane POS ingestion.
        
        Args:
            file_path: Path to POS data file (CoNLL format)
            batch_size: Batch size for commits
            
        Returns:
            Statistics dictionary
            
        Format:
            word	TAG
            Zanzibar	PROPN
            ni	AUX
            ...
        """
        logger.info(f"Starting Masakhane POS ingestion from {file_path}")
        
        # Check file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Statistics
        stats = {
            'total_lines': 0,
            'new_terms': 0,
            'existing_terms': 0,
            'pos_records': 0,
            'sentences': 0,
            'errors': 0
        }
        
        # Read file
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        stats['total_lines'] = len(lines)
        
        # Process lines
        sentence_id = 0
        word_order = 0
        
        for line in tqdm(lines, desc="Processing POS data"):
            line = line.strip()
            
            # Empty line = sentence boundary
            if not line:
                sentence_id += 1
                word_order = 0
                stats['sentences'] += 1
                continue
            
            try:
                # Parse line (word	TAG)
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                word = parts[0].strip()
                tag = parts[1].strip().upper()
                
                # Create or get term
                term_id = self._get_or_create_term(word, tag)
                
                if term_id is None:
                    stats['errors'] += 1
                    continue
                
                # Create POS record
                pos_record = POSRecord(
                    term=word,
                    tag=tag,
                    sentence_id=sentence_id,
                    word_order=word_order,
                    confidence=1.0
                )
                
                self.pos_repo.save(pos_record, term_id)
                stats['pos_records'] += 1
                
                word_order += 1
                
            except Exception as e:
                logger.warning(f"Error processing line '{line}': {e}")
                stats['errors'] += 1
                continue
        
        logger.success(f"Masakhane ingestion complete: {stats}")
        return stats
    
    def _get_or_create_term(self, word: str, tag: str) -> int:
        """
        Get existing term ID or create new term.
        
        Args:
            word: Word string
            tag: POS tag
            
        Returns:
            Term ID
        """
        # Check if term exists
        if self.term_repo.exists(word):
            existing = self.term_repo.find_by_term(word)
            return existing.id if hasattr(existing, 'id') else None
        
        # Map POS tag to WordType
        word_type = self._map_pos_to_word_type(tag)
        
        # Apply domain services
        root = self.root_service.extract(word, word_type)
        bantu_class = self.bantu_service.infer_class(word, word_type)
        
        # Create entity
        term = SwahiliTerm(
            term=word,
            root=root,
            noun_class=bantu_class,
            word_type=word_type
        )
        
        # Save
        term_id = self.term_repo.save(term)
        return term_id
    
    @staticmethod
    def _map_pos_to_word_type(pos_tag: str) -> WordType:
        """
        Map POS tag to WordType.
        
        Args:
            pos_tag: Universal POS tag
            
        Returns:
            WordType enum
        """
        mapping = {
            'NOUN': WordType.NOUN,
            'PROPN': WordType.NOUN,
            'VERB': WordType.VERB,
            'ADJ': WordType.ADJECTIVE,
            'ADV': WordType.ADVERB,
            'PRON': WordType.PRONOUN,
            'DET': WordType.DETERMINER,
            'ADP': WordType.PREPOSITION,
            'CONJ': WordType.CONJUNCTION,
            'CCONJ': WordType.CONJUNCTION,
            'SCONJ': WordType.CONJUNCTION,
            'INTJ': WordType.INTERJECTION,
            'NUM': WordType.NUMERAL,
        }
        
        return mapping.get(pos_tag.upper(), WordType.UNKNOWN)


# Usage example
if __name__ == "__main__":
    from src.infrastructure.database import init_db, get_session
    from src.infrastructure.repositories.term_repository import TermRepository
    from src.infrastructure.repositories.pos_repository import POSRepository
    
    print("=== Ingest Masakhane Use Case Test ===\n")
    
    # Initialize database
    init_db()
    
    # Create session
    session = get_session()
    
    try:
        # Create repositories
        term_repo = TermRepository(session)
        pos_repo = POSRepository(session)  # You'll need to create this
        
        # Create use case
        use_case = IngestMasakhaneUseCase(term_repo, pos_repo)
        
        # Execute (with test data)
        # stats = use_case.execute("data/raw/pos_swa_test.txt")
        
        print("✓ Use case initialized successfully")
        print("  (Execute with actual data file to ingest)")
        
        session.commit()
        
    except Exception as e:
        session.rollback()
        print(f"✗ Error: {e}")
    finally:
        session.close()
