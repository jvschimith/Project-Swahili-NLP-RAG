"""
Application Layer - Export Formats

ML-ready export formats for research use.
Supports CoNLL, BIO, TSV, JSON-LD, and standard splits.
"""
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
import random
from pathlib import Path


@dataclass
class AnnotatedToken:
    """Single token with all annotations."""
    text: str
    pos: Optional[str] = None
    ner: Optional[str] = None
    sentiment: Optional[str] = None
    morphology: Optional[Dict[str, str]] = None
    sentence_id: int = 0
    token_id: int = 0


@dataclass
class AnnotatedSentence:
    """Sentence with token-level annotations."""
    tokens: List[AnnotatedToken]
    sentence_id: int
    sentiment: Optional[str] = None
    
    def to_conll(self) -> str:
        """
        Convert to CoNLL format.
        
        Format:
        # sent_id = 1
        # text = Original sentence
        1    Token    Lemma    POS    NER
        2    Token2   Lemma2   POS2   NER2
        
        Returns:
            CoNLL formatted string
        """
        lines = [f"# sent_id = {self.sentence_id}"]
        text = " ".join([t.text for t in self.tokens])
        lines.append(f"# text = {text}")
        
        if self.sentiment:
            lines.append(f"# sentiment = {self.sentiment}")
        
        for token in self.tokens:
            # CoNLL-U format: ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC
            lemma = token.text.lower()
            pos = token.pos or "_"
            ner = token.ner or "O"
            
            # Add morphology as features
            feats = "_"
            if token.morphology:
                feats = "|".join([f"{k}={v}" for k, v in token.morphology.items()])
            
            line = f"{token.token_id}\t{token.text}\t{lemma}\t{pos}\t_\t{feats}\t_\t_\t_\tNER={ner}"
            lines.append(line)
        
        lines.append("")  # Empty line between sentences
        return "\n".join(lines)
    
    def to_bio(self) -> List[Tuple[str, str, str]]:
        """
        Convert to BIO tagging format.
        
        Returns:
            List of (token, pos, ner_tag) tuples
        """
        bio_tags = []
        for token in self.tokens:
            bio_tags.append((
                token.text,
                token.pos or "O",
                token.ner or "O"
            ))
        return bio_tags
    
    def to_tsv(self) -> str:
        """
        Convert to TSV format for SpaCy.
        
        Format:
        Token\tPOS\tNER\tSentiment
        """
        lines = []
        for token in self.tokens:
            lines.append(f"{token.text}\t{token.pos or 'O'}\t{token.ner or 'O'}\t{self.sentiment or 'O'}")
        return "\n".join(lines)


@dataclass
class AnnotatedDocument:
    """Complete document with all annotations."""
    url: str
    title: str
    content: str
    sentences: List[AnnotatedSentence]
    sentiment: Dict[str, Any]
    entities: List[Dict[str, Any]]
    keywords: List[Dict[str, Any]]
    topics: List[Dict[str, str]]
    translation: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    analyzed_at: str = None
    
    def __post_init__(self):
        if self.analyzed_at is None:
            self.analyzed_at = datetime.utcnow().isoformat()
    
    def to_conll(self) -> str:
        """Export as CoNLL format."""
        conll_output = []
        conll_output.append(f"# document_id = {self.metadata.get('id', 'unknown')}")
        conll_output.append(f"# url = {self.url}")
        conll_output.append(f"# title = {self.title}")
        conll_output.append(f"# sentiment = {self.sentiment.get('label', 'unknown')}")
        conll_output.append("")
        
        for sentence in self.sentences:
            conll_output.append(sentence.to_conll())
        
        return "\n".join(conll_output)
    
    def to_bio(self) -> str:
        """Export as BIO format."""
        bio_lines = ["Token\tPOS\tNER"]
        
        for sentence in self.sentences:
            for token, pos, ner in sentence.to_bio():
                bio_lines.append(f"{token}\t{pos}\t{ner}")
            bio_lines.append("")  # Empty line between sentences
        
        return "\n".join(bio_lines)
    
    def to_tsv(self) -> str:
        """Export as TSV format."""
        tsv_lines = ["Token\tPOS\tNER\tSentiment"]
        
        for sentence in self.sentences:
            tsv_lines.append(sentence.to_tsv())
            tsv_lines.append("")
        
        return "\n".join(tsv_lines)
    
    def to_json_ld(self) -> Dict[str, Any]:
        """
        Export as JSON-LD (Linked Data).
        
        Uses schema.org vocabulary.
        """
        return {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "url": self.url,
            "headline": self.title,
            "articleBody": self.content,
            "datePublished": self.analyzed_at,
            "inLanguage": "sw",
            "about": [{"@type": "Thing", "name": topic['category']} for topic in self.topics],
            "keywords": [kw['word'] for kw in self.keywords[:10]],
            "sentiment": {
                "@type": "Rating",
                "ratingValue": self.sentiment.get('polarity', 0),
                "bestRating": 1,
                "worstRating": -1,
                "description": self.sentiment.get('label', 'unknown')
            },
            "mentions": [
                {
                    "@type": "Person" if entity.get('type') == 'PERSON' else "Place" if entity.get('type') == 'LOCATION' else "Organization",
                    "name": entity.get('text', '')
                }
                for entity in self.entities
            ],
            "translation": self.translation if self.translation else None
        }
    
    def to_research_json(self, include_confidence: bool = True) -> Dict[str, Any]:
        """
        Export as research-ready JSON with all features.
        
        Args:
            include_confidence: Include confidence scores
            
        Returns:
            Complete analysis dictionary
        """
        output = {
            "document_id": self.metadata.get('id', 'unknown'),
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "analyzed_at": self.analyzed_at,
            "language": "sw",
            "word_count": len(self.content.split()),
            "sentence_count": len(self.sentences),
            
            "sentiment": {
                "label": self.sentiment.get('label'),
                "polarity": self.sentiment.get('polarity'),
                "confidence": self.sentiment.get('confidence') if include_confidence else None,
                "positive_words": self.sentiment.get('positive_words_found', 0),
                "negative_words": self.sentiment.get('negative_words_found', 0)
            },
            
            "entities": [
                {
                    "text": e.get('text'),
                    "type": e.get('type'),
                    "confidence": e.get('confidence') if include_confidence else None
                }
                for e in self.entities
            ],
            
            "keywords": [
                {
                    "word": kw.get('word'),
                    "translation": kw.get('translation'),
                    "count": kw.get('count'),
                    "tfidf": kw.get('tfidf') if include_confidence else None
                }
                for kw in self.keywords
            ],
            
            "topics": [
                {
                    "category": t.get('category'),
                    "confidence": t.get('confidence') if include_confidence else None
                }
                for t in self.topics
            ],
            
            "translation": self.translation,
            
            "linguistic_features": {
                "lexical_diversity": self.metadata.get('lexical_diversity'),
                "readability": self.metadata.get('readability'),
                "avg_word_length": self.metadata.get('avg_word_length'),
                "complex_words_ratio": self.metadata.get('complex_words_ratio')
            },
            
            "sentences": [
                {
                    "id": sent.sentence_id,
                    "tokens": [
                        {
                            "text": tok.text,
                            "pos": tok.pos,
                            "ner": tok.ner,
                            "morphology": tok.morphology
                        }
                        for tok in sent.tokens
                    ],
                    "sentiment": sent.sentiment
                }
                for sent in self.sentences
            ]
        }
        
        # Remove None values
        if not include_confidence:
            output = self._remove_none_values(output)
        
        return output
    
    def _remove_none_values(self, d: Any) -> Any:
        """Recursively remove None values from dict."""
        if isinstance(d, dict):
            return {k: self._remove_none_values(v) for k, v in d.items() if v is not None}
        elif isinstance(d, list):
            return [self._remove_none_values(item) for item in d]
        else:
            return d


class DatasetSplitter:
    """Split datasets into train/dev/test with stratification."""
    
    @staticmethod
    def split_dataset(
        documents: List[AnnotatedDocument],
        train_ratio: float = 0.7,
        dev_ratio: float = 0.15,
        test_ratio: float = 0.15,
        stratify_by: str = 'sentiment',
        random_seed: int = 42
    ) -> Tuple[List[AnnotatedDocument], List[AnnotatedDocument], List[AnnotatedDocument]]:
        """
        Split dataset with stratification.
        
        Args:
            documents: List of annotated documents
            train_ratio: Training set ratio (default 0.7)
            dev_ratio: Development set ratio (default 0.15)
            test_ratio: Test set ratio (default 0.15)
            stratify_by: Field to stratify by ('sentiment', 'topic', None)
            random_seed: Random seed for reproducibility
            
        Returns:
            (train, dev, test) tuple of document lists
        """
        random.seed(random_seed)
        
        # Validate ratios
        assert abs(train_ratio + dev_ratio + test_ratio - 1.0) < 0.001, "Ratios must sum to 1.0"
        
        if stratify_by:
            # Group by stratification field
            groups = {}
            for doc in documents:
                if stratify_by == 'sentiment':
                    key = doc.sentiment.get('label', 'unknown')
                elif stratify_by == 'topic':
                    key = doc.topics[0].get('category') if doc.topics else 'unknown'
                else:
                    key = 'all'
                
                if key not in groups:
                    groups[key] = []
                groups[key].append(doc)
            
            # Split each group
            train, dev, test = [], [], []
            
            for key, group_docs in groups.items():
                random.shuffle(group_docs)
                n = len(group_docs)
                
                train_end = int(n * train_ratio)
                dev_end = train_end + int(n * dev_ratio)
                
                train.extend(group_docs[:train_end])
                dev.extend(group_docs[train_end:dev_end])
                test.extend(group_docs[dev_end:])
            
        else:
            # Simple random split
            docs = documents.copy()
            random.shuffle(docs)
            n = len(docs)
            
            train_end = int(n * train_ratio)
            dev_end = train_end + int(n * dev_ratio)
            
            train = docs[:train_end]
            dev = docs[train_end:dev_end]
            test = docs[dev_end:]
        
        return train, dev, test
    
    @staticmethod
    def export_splits(
        documents: List[AnnotatedDocument],
        output_dir: Path,
        format: str = 'json',
        **split_kwargs
    ) -> Dict[str, Path]:
        """
        Split and export dataset.
        
        Args:
            documents: List of documents
            output_dir: Output directory
            format: Export format ('json', 'conll', 'bio', 'tsv')
            **split_kwargs: Arguments for split_dataset
            
        Returns:
            Dictionary mapping split names to file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Split dataset
        train, dev, test = DatasetSplitter.split_dataset(documents, **split_kwargs)
        
        # Export each split
        splits = {
            'train': train,
            'dev': dev,
            'test': test
        }
        
        file_paths = {}
        
        for split_name, split_docs in splits.items():
            if format == 'json':
                file_path = output_dir / f"{split_name}.json"
                data = [doc.to_research_json() for doc in split_docs]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            elif format == 'conll':
                file_path = output_dir / f"{split_name}.conll"
                with open(file_path, 'w', encoding='utf-8') as f:
                    for doc in split_docs:
                        f.write(doc.to_conll())
                        f.write("\n\n")
            
            elif format == 'bio':
                file_path = output_dir / f"{split_name}.bio"
                with open(file_path, 'w', encoding='utf-8') as f:
                    for doc in split_docs:
                        f.write(doc.to_bio())
                        f.write("\n\n")
            
            elif format == 'tsv':
                file_path = output_dir / f"{split_name}.tsv"
                with open(file_path, 'w', encoding='utf-8') as f:
                    for doc in split_docs:
                        f.write(doc.to_tsv())
                        f.write("\n\n")
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            file_paths[split_name] = file_path
        
        # Export metadata
        metadata = {
            'total_documents': len(documents),
            'train_size': len(train),
            'dev_size': len(dev),
            'test_size': len(test),
            'format': format,
            'split_config': split_kwargs,
            'created_at': datetime.utcnow().isoformat()
        }
        
        metadata_path = output_dir / 'metadata.json'
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        file_paths['metadata'] = metadata_path
        
        return file_paths


class ConfidenceScorer:
    """Add confidence scores to predictions."""
    
    @staticmethod
    def calculate_sentiment_confidence(
        polarity: float,
        positive_words: int,
        negative_words: int,
        total_words: int
    ) -> float:
        """
        Calculate confidence score for sentiment prediction.
        
        Args:
            polarity: Sentiment polarity (-1 to 1)
            positive_words: Number of positive words
            negative_words: Number of negative words
            total_words: Total word count
            
        Returns:
            Confidence score (0 to 1)
        """
        # Base confidence from polarity magnitude
        base_confidence = abs(polarity)
        
        # Boost if we have evidence
        evidence_ratio = (positive_words + negative_words) / max(total_words, 1)
        evidence_boost = min(evidence_ratio * 2, 0.3)  # Max 0.3 boost
        
        # Balance (if one-sided, higher confidence)
        total_sentiment_words = positive_words + negative_words
        if total_sentiment_words > 0:
            balance = abs(positive_words - negative_words) / total_sentiment_words
            balance_boost = balance * 0.2  # Max 0.2 boost
        else:
            balance_boost = 0
        
        confidence = min(base_confidence + evidence_boost + balance_boost, 1.0)
        
        return round(confidence, 2)
    
    @staticmethod
    def calculate_ner_confidence(
        entity_text: str,
        context: str,
        known_entities: set = None
    ) -> float:
        """
        Calculate confidence for NER prediction.
        
        Args:
            entity_text: Extracted entity
            context: Surrounding text
            known_entities: Set of known entities from gazeteer
            
        Returns:
            Confidence score (0 to 1)
        """
        confidence = 0.5  # Base confidence
        
        # Capitalized → likely proper noun
        if entity_text[0].isupper():
            confidence += 0.2
        
        # Multiple words → likely entity
        if len(entity_text.split()) > 1:
            confidence += 0.1
        
        # In known gazeteer
        if known_entities and entity_text in known_entities:
            confidence += 0.3
        
        # Has title words (Rais, Waziri, Dr., etc.)
        titles = {'rais', 'waziri', 'dkt', 'profesa', 'mheshimiwa'}
        if any(title in entity_text.lower() for title in titles):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    @staticmethod
    def calculate_topic_confidence(
        keywords: List[str],
        topic_keywords: Dict[str, List[str]]
    ) -> Dict[str, float]:
        """
        Calculate confidence for topic classification.
        
        Args:
            keywords: Extracted keywords from document
            topic_keywords: Dictionary of topic → keyword lists
            
        Returns:
            Dictionary of topic → confidence scores
        """
        topic_scores = {}
        
        for topic, topic_kws in topic_keywords.items():
            # Count matches
            matches = sum(1 for kw in keywords if kw in topic_kws)
            
            # Calculate confidence
            if len(keywords) > 0:
                confidence = matches / len(keywords)
            else:
                confidence = 0.0
            
            topic_scores[topic] = round(confidence, 2)
        
        return topic_scores
