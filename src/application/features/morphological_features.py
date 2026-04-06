"""
Features - Morphological Feature Extractor (Phase 2)

Extract linguistic features for machine learning models.
Particularly useful for low-resource scenarios where features help models generalize.
"""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict

from ..services.root_extractor_enhanced import EnhancedRootExtractor
from ...application.tokenizers.syllable_tokenizer import SwahiliSyllableTokenizer


@dataclass
class MorphologicalFeatures:
    """
    Complete morphological feature set for a Swahili word.
    
    These features help ML models learn patterns in low-resource settings:
    - Explicit linguistic structure
    - Language-specific features
    - Syllable-level information
    - Morpheme decomposition
    """
    
    # Basic features
    word: str
    length: int
    starts_with_vowel: bool
    ends_with_vowel: bool
    
    # Morphological structure
    has_prefix: bool
    has_suffix: bool
    prefix: Optional[str]
    root: Optional[str]
    suffix: Optional[str]
    
    # Syllable features
    syllable_count: int
    syllables: List[str]
    first_syllable: str
    last_syllable: str
    syllable_complexity: float
    
    # Verb features
    is_verb_like: bool
    subject_marker: Optional[str]
    tense_marker: Optional[str]
    object_marker: Optional[str]
    verb_root: Optional[str]
    
    # Noun features
    is_noun_like: bool
    noun_class_prefix: Optional[str]
    
    # Character patterns
    has_hyphen: bool
    has_apostrophe: bool
    has_mixed_case: bool
    
    # Phonological features
    vowel_ratio: float
    consonant_clusters: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for ML."""
        return asdict(self)
    
    def to_feature_vector(self) -> Dict[str, float]:
        """
        Convert to numerical feature vector.
        
        Returns dict of feature_name -> numerical_value
        Useful for sklearn, xgboost, etc.
        """
        return {
            "length": float(self.length),
            "starts_with_vowel": 1.0 if self.starts_with_vowel else 0.0,
            "ends_with_vowel": 1.0 if self.ends_with_vowel else 0.0,
            "has_prefix": 1.0 if self.has_prefix else 0.0,
            "has_suffix": 1.0 if self.has_suffix else 0.0,
            "syllable_count": float(self.syllable_count),
            "syllable_complexity": self.syllable_complexity,
            "is_verb_like": 1.0 if self.is_verb_like else 0.0,
            "is_noun_like": 1.0 if self.is_noun_like else 0.0,
            "vowel_ratio": self.vowel_ratio,
            "consonant_clusters": float(self.consonant_clusters),
        }


class MorphologicalFeatureExtractor:
    """
    Extract morphological features for ML models.
    
    Use cases:
    - Feature engineering for classification
    - Active learning (identify uncertain examples)
    - Model interpretability
    - Cross-lingual transfer
    """
    
    VOWELS = set('aeiou')
    CONSONANTS = set('bcdfghjklmnpqrstvwxyz')
    
    # Common prefixes for nouns
    NOUN_PREFIXES = ['m', 'wa', 'mi', 'ji', 'ma', 'ki', 'vi', 'n', 'ny', 'u', 'ku', 'pa']
    
    # Common prefixes for verbs (subject markers)
    VERB_PREFIXES = ['ni', 'u', 'a', 'tu', 'm', 'wa']
    
    @classmethod
    def extract_features(
        cls,
        word: str,
        context: Optional[str] = None
    ) -> MorphologicalFeatures:
        """
        Extract all morphological features for a word.
        
        Args:
            word: Swahili word to analyze
            context: Optional sentence context (not used yet, for future)
            
        Returns:
            MorphologicalFeatures object
            
        Example:
            >>> extractor = MorphologicalFeatureExtractor()
            >>> features = extractor.extract_features("ninasoma")
            >>> features.is_verb_like
            True
            >>> features.syllable_count
            4
        """
        word_lower = word.lower()
        
        # Basic features
        length = len(word_lower)
        starts_vowel = word_lower[0] in cls.VOWELS if word_lower else False
        ends_vowel = word_lower[-1] in cls.VOWELS if word_lower else False
        
        # Syllable analysis
        syllables = SwahiliSyllableTokenizer.tokenize(word_lower)
        syl_analysis = SwahiliSyllableTokenizer.analyze_syllable_structure(word_lower)
        
        # Verb analysis
        verb_components = EnhancedRootExtractor.extract_verb_components(word_lower)
        is_verb = EnhancedRootExtractor.is_valid_verb(word_lower)
        
        # Noun analysis
        is_noun = cls._looks_like_noun(word_lower)
        noun_prefix = cls._extract_noun_prefix(word_lower)
        
        # Character patterns
        has_hyphen = '-' in word
        has_apostrophe = "'" in word
        has_mixed = any(c.isupper() for c in word) and any(c.islower() for c in word)
        
        # Phonological features
        vowel_count = sum(1 for c in word_lower if c in cls.VOWELS)
        vowel_ratio = vowel_count / length if length > 0 else 0.0
        consonant_clusters = cls._count_consonant_clusters(word_lower)
        
        return MorphologicalFeatures(
            word=word,
            length=length,
            starts_with_vowel=starts_vowel,
            ends_with_vowel=ends_vowel,
            has_prefix=verb_components.subject is not None or noun_prefix is not None,
            has_suffix=verb_components.final is not None,
            prefix=verb_components.subject or noun_prefix,
            root=verb_components.root,
            suffix=verb_components.final,
            syllable_count=len(syllables),
            syllables=syllables,
            first_syllable=syllables[0] if syllables else "",
            last_syllable=syllables[-1] if syllables else "",
            syllable_complexity=syl_analysis.get('complexity', 0.0),
            is_verb_like=is_verb,
            subject_marker=verb_components.subject,
            tense_marker=verb_components.tense,
            object_marker=verb_components.object,
            verb_root=verb_components.root if is_verb else None,
            is_noun_like=is_noun,
            noun_class_prefix=noun_prefix,
            has_hyphen=has_hyphen,
            has_apostrophe=has_apostrophe,
            has_mixed_case=has_mixed,
            vowel_ratio=vowel_ratio,
            consonant_clusters=consonant_clusters
        )
    
    @classmethod
    def extract_for_corpus(
        cls,
        corpus: List[str],
        include_context: bool = False
    ) -> List[MorphologicalFeatures]:
        """
        Extract features for entire corpus.
        
        Args:
            corpus: List of words
            include_context: Whether to use sentence context (future)
            
        Returns:
            List of MorphologicalFeatures
        """
        return [cls.extract_features(word) for word in corpus]
    
    @classmethod
    def extract_to_dataframe(cls, corpus: List[str]) -> 'pd.DataFrame':
        """
        Extract features and return as pandas DataFrame.
        
        Useful for ML pipelines.
        """
        import pandas as pd
        
        features_list = cls.extract_for_corpus(corpus)
        data = [f.to_dict() for f in features_list]
        
        return pd.DataFrame(data)
    
    @classmethod
    def extract_feature_vectors(
        cls,
        corpus: List[str]
    ) -> List[Dict[str, float]]:
        """
        Extract numerical feature vectors for ML.
        
        Returns list of feature dictionaries ready for sklearn.
        """
        features_list = cls.extract_for_corpus(corpus)
        return [f.to_feature_vector() for f in features_list]
    
    @classmethod
    def _looks_like_noun(cls, word: str) -> bool:
        """Heuristic to check if word looks like a noun."""
        # Starts with noun class prefix
        for prefix in cls.NOUN_PREFIXES:
            if word.startswith(prefix):
                return True
        
        # Doesn't look like verb
        if not any(word.startswith(v) for v in cls.VERB_PREFIXES):
            return True
        
        return False
    
    @classmethod
    def _extract_noun_prefix(cls, word: str) -> Optional[str]:
        """Try to extract noun class prefix."""
        for prefix in sorted(cls.NOUN_PREFIXES, key=len, reverse=True):
            if word.startswith(prefix) and len(word) > len(prefix):
                return prefix
        return None
    
    @classmethod
    def _count_consonant_clusters(cls, word: str) -> int:
        """Count consonant clusters (CC, CCC, etc.)."""
        count = 0
        in_cluster = False
        
        for char in word:
            if char in cls.CONSONANTS:
                if in_cluster:
                    count += 1
                in_cluster = True
            else:
                in_cluster = False
        
        return count


# ==================== FEATURE-BASED MODELS ====================

class FeatureBasedClassifier:
    """
    Simple feature-based classifier for low-resource scenarios.
    
    Uses hand-crafted morphological features instead of embeddings.
    Often works better than neural models with <1000 examples.
    """
    
    @staticmethod
    def prepare_training_data(
        words: List[str],
        labels: List[str]
    ) -> Tuple[List[Dict[str, float]], List[str]]:
        """
        Prepare feature vectors and labels for training.
        
        Args:
            words: List of Swahili words
            labels: Corresponding labels
            
        Returns:
            (feature_vectors, labels) ready for sklearn
        """
        features = MorphologicalFeatureExtractor.extract_feature_vectors(words)
        return features, labels
    
    @staticmethod
    def train_baseline_classifier(
        X_train: List[Dict[str, float]],
        y_train: List[str],
        model_type: str = "random_forest"
    ):
        """
        Train baseline classifier using morphological features.
        
        Args:
            X_train: Feature dictionaries
            y_train: Labels
            model_type: "random_forest", "logistic", or "svm"
            
        Returns:
            Trained sklearn model
        """
        from sklearn.feature_extraction import DictVectorizer
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.svm import SVC
        from sklearn.pipeline import Pipeline
        
        # Vectorize features
        vectorizer = DictVectorizer(sparse=False)
        
        # Choose model
        if model_type == "random_forest":
            classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        elif model_type == "logistic":
            classifier = LogisticRegression(max_iter=1000, random_state=42)
        elif model_type == "svm":
            classifier = SVC(kernel='rbf', random_state=42)
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Create pipeline
        pipeline = Pipeline([
            ('vectorizer', vectorizer),
            ('classifier', classifier)
        ])
        
        # Train
        pipeline.fit(X_train, y_train)
        
        return pipeline
