"""
Domain Layer - Entities

Entities are objects with unique identity that persists over time, even
when their attributes change. They are the central objects of the
domain.

Characteristics:
- They have unique identity (ID)
- They are mutable (their state can change)
- They are compared by identity (ID), not by value
- They encapsulate business rules
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from .value_objects import (
    BantuClass, 
    Etymology, 
    WordType, 
    SentimentScore, 
    MorphologicalRoot,
    EntityType,
    VerbComponents,
)
from .linguistic_rules import normalize_linguistic_text, normalize_suffixes


class WordForm(BaseModel):
    """
    Entity: Concrete surface realization of a lexeme.

    A WordForm captures an attested or generable form that belongs to a
    lexeme, including lightweight structural metadata needed during the
    domain migration.
    """
    lexeme_lemma: str = Field(..., min_length=1, max_length=100)
    form: str = Field(..., min_length=1, max_length=100)
    root: Optional[MorphologicalRoot] = None
    word_type: WordType = WordType.UNKNOWN
    grammatical_features: List[str] = Field(default_factory=list)
    subject_marker: Optional[str] = None
    tense_marker: Optional[str] = None
    object_marker: Optional[str] = None
    suffixes_extensions: List[str] = Field(default_factory=list)
    final_vowel: Optional[str] = None
    polarity: Optional[str] = None
    verb_components: Optional[VerbComponents] = None
    is_canonical: bool = False
    register: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('lexeme_lemma', 'form')
    @classmethod
    def normalize_text(cls, v: str) -> str:
        """Normalize lemma/form strings for lexical matching."""
        return normalize_linguistic_text(v)

    @field_validator('subject_marker', 'tense_marker', 'object_marker')
    @classmethod
    def normalize_markers(cls, v: Optional[str]) -> Optional[str]:
        """Normalize optional verbal markers."""
        if v is None:
            return None
        normalized = normalize_linguistic_text(v)
        return normalized or None

    @field_validator('suffixes_extensions')
    @classmethod
    def normalize_suffixes(cls, values: List[str]) -> List[str]:
        """Normalize derivational/final suffix material."""
        return normalize_suffixes(values)

    @field_validator('final_vowel', 'polarity')
    @classmethod
    def normalize_optional_fields(cls, v: Optional[str]) -> Optional[str]:
        """Normalize optional morphology fields."""
        if v is None:
            return None
        normalized = normalize_linguistic_text(v)
        return normalized or None

    def model_post_init(self, __context) -> None:
        """
        Synchronize structured verbal morphology across additive fields.

        The current migration keeps legacy/general fields while exposing
        explicit Swahili verbal morphology on the entity itself.
        """
        if self.verb_components is not None:
            if self.subject_marker is None:
                self.subject_marker = self.verb_components.subject_marker
            if self.tense_marker is None:
                self.tense_marker = self.verb_components.tense_marker
            if self.object_marker is None:
                self.object_marker = self.verb_components.object_marker
            if not self.suffixes_extensions:
                suffixes = list(self.verb_components.suffixes_extensions)
                if (
                    self.verb_components.final_vowel
                    and self.verb_components.final_vowel not in suffixes
                ):
                    suffixes.append(self.verb_components.final_vowel)
                self.suffixes_extensions = suffixes
            if self.final_vowel is None:
                self.final_vowel = self.verb_components.final_vowel
            if self.polarity is None:
                self.polarity = self.verb_components.polarity
            if self.root is None and self.verb_components.root:
                self.root = MorphologicalRoot(root=self.verb_components.root)

    def add_feature(self, feature: str) -> None:
        """Add a normalized grammatical feature once."""
        normalized = feature.strip().lower()
        if normalized and normalized not in self.grammatical_features:
            self.grammatical_features.append(normalized)

    @property
    def surface_form(self) -> str:
        """Convenience alias used by future API/domain adapters."""
        return self.form

    @property
    def has_structured_morphology(self) -> bool:
        """Check whether explicit verbal morphology has been attached."""
        return any([
            self.subject_marker,
            self.tense_marker,
            self.object_marker,
            self.suffixes_extensions,
            self.final_vowel,
            self.polarity,
            self.verb_components is not None,
        ])


class Meaning(BaseModel):
    """
    Entity: Semantic interpretation belonging to a lexeme.

    Meanings are attached to abstract lexemes instead of individual
    surface forms so the model can represent multiple realizations of the
    same underlying concept.
    """
    lexeme_lemma: str = Field(..., min_length=1, max_length=100)
    gloss: str = Field(..., min_length=1)
    definition: Optional[str] = None
    english_translation: Optional[str] = None
    semantic_domain: Optional[str] = None
    usage_notes: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('lexeme_lemma')
    @classmethod
    def normalize_lemma(cls, v: str) -> str:
        """Normalize lexical lemma references."""
        return v.strip().lower()

    def add_synonym(self, synonym: str) -> None:
        """Add a normalized synonym once."""
        normalized = synonym.strip().lower()
        if normalized and normalized not in self.synonyms:
            self.synonyms.append(normalized)


class Context(BaseModel):
    """
    Entity: Real-world usage context for lexical data.

    Context stores attested example sentences and references back to the
    relevant lexeme and optionally a specific word form.
    """
    text: str = Field(..., min_length=1)
    english_translation: Optional[str] = None
    lexeme_lemma: str = Field(..., min_length=1, max_length=100)
    word_form: Optional[str] = Field(default=None, min_length=1, max_length=100)
    source: Optional[str] = None
    source_url: Optional[str] = None
    sentence_id: Optional[int] = Field(default=None, ge=0)
    token_start: Optional[int] = Field(default=None, ge=0)
    token_end: Optional[int] = Field(default=None, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('lexeme_lemma')
    @classmethod
    def normalize_lemma(cls, v: str) -> str:
        """Normalize lexical lemma references."""
        return v.strip().lower()

    @field_validator('word_form')
    @classmethod
    def normalize_word_form(cls, v: Optional[str]) -> Optional[str]:
        """Normalize optional surface form references."""
        if v is None:
            return None
        normalized = v.strip().lower()
        return normalized or None

    @property
    def references_specific_form(self) -> bool:
        """Check whether the usage example targets a concrete word form."""
        return self.word_form is not None


class Derivation(BaseModel):
    """
    Entity: Directed derivational relation between lexemes.

    This models lexical families such as base forms, applicatives,
    causatives, nominalizations, and other derivational processes.
    """
    source_lexeme: str = Field(..., min_length=1, max_length=100)
    target_lexeme: str = Field(..., min_length=1, max_length=100)
    process: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None
    is_productive: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('source_lexeme', 'target_lexeme', 'process')
    @classmethod
    def normalize_fields(cls, v: str) -> str:
        """Normalize lexical references and process labels."""
        return v.strip().lower()

    @property
    def is_self_derivation(self) -> bool:
        """Guard against accidental identity relations."""
        return self.source_lexeme == self.target_lexeme


class Lexeme(BaseModel):
    """
    Aggregate Root: Abstract lexical-semantic unit.

    A Lexeme is the primary domain entity for lexical knowledge. It
    separates abstract identity from the concrete word forms that realize
    it in text.
    """
    lemma: str = Field(..., min_length=1, max_length=100)
    word_type: WordType = WordType.UNKNOWN
    etymology: Etymology = Etymology.UNKNOWN
    noun_class: BantuClass = BantuClass.UNKNOWN
    root: Optional[MorphologicalRoot] = None
    word_forms: List[WordForm] = Field(default_factory=list)
    meanings: List[Meaning] = Field(default_factory=list)
    contexts: List[Context] = Field(default_factory=list)
    derivations: List[Derivation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration."""
        use_enum_values = False
        validate_assignment = True

    @field_validator('lemma')
    @classmethod
    def normalize_lemma(cls, v: str) -> str:
        """Normalize the canonical lemma."""
        return v.strip().lower()

    def add_word_form(self, word_form: WordForm) -> None:
        """
        Attach a WordForm to this lexeme.

        Business Rule: a word form must reference this lexeme's lemma.
        """
        if word_form.lexeme_lemma != self.lemma:
            raise ValueError(
                f"WordForm belongs to '{word_form.lexeme_lemma}', expected '{self.lemma}'"
            )

        if all(existing.form != word_form.form for existing in self.word_forms):
            self.word_forms.append(word_form)
            self.updated_at = datetime.utcnow()

    def add_meaning(self, meaning: Meaning) -> None:
        """
        Attach a Meaning to this lexeme.

        Business Rule: meanings are owned by the lexeme, not by individual
        forms.
        """
        if meaning.lexeme_lemma != self.lemma:
            raise ValueError(
                f"Meaning belongs to '{meaning.lexeme_lemma}', expected '{self.lemma}'"
            )

        if all(existing.gloss != meaning.gloss for existing in self.meanings):
            self.meanings.append(meaning)
            self.updated_at = datetime.utcnow()

    def add_context(self, context: Context) -> None:
        """Attach an attested usage context to this lexeme."""
        if context.lexeme_lemma != self.lemma:
            raise ValueError(
                f"Context belongs to '{context.lexeme_lemma}', expected '{self.lemma}'"
            )

        if context.word_form is not None:
            known_forms = {form.form for form in self.word_forms}
            if known_forms and context.word_form not in known_forms:
                raise ValueError(
                    f"Context references unknown word form '{context.word_form}' for '{self.lemma}'"
                )

        if context not in self.contexts:
            self.contexts.append(context)
            self.updated_at = datetime.utcnow()

    def add_derivation(self, derivation: Derivation) -> None:
        """Attach a derivational relation involving this lexeme."""
        if derivation.source_lexeme != self.lemma and derivation.target_lexeme != self.lemma:
            raise ValueError(
                f"Derivation does not involve lexeme '{self.lemma}'"
            )
        if derivation.is_self_derivation:
            raise ValueError("Derivation cannot point to the same lexeme")

        if derivation not in self.derivations:
            self.derivations.append(derivation)
            self.updated_at = datetime.utcnow()

    @property
    def canonical_form(self) -> Optional[WordForm]:
        """Return the marked canonical form when present."""
        for word_form in self.word_forms:
            if word_form.is_canonical:
                return word_form
        return None

    @property
    def primary_meaning(self) -> Optional[Meaning]:
        """Return the first available meaning as a temporary default."""
        return self.meanings[0] if self.meanings else None

    @property
    def has_word_forms(self) -> bool:
        """Check whether the lexeme has at least one concrete realization."""
        return len(self.word_forms) > 0

    @property
    def has_meanings(self) -> bool:
        """Check whether the lexeme already has semantic data."""
        return len(self.meanings) > 0


class SwahiliTerm(BaseModel):
    """
    Aggregate Root: Term in the Swahili vocabulary.

    Represents a unique word in the vocabulary with all of its
    linguistic and semantic metadata. It is the aggregate root of the
    domain.
    
    Attributes:
        term: The Swahili word (normalized, lowercase)
        root: Morphological root (if identified)
        noun_class: Bantu noun class (for nouns)
        etymology: Etymological origin of the word
        word_type: Grammatical type (noun, verb, etc.)
        is_stopword: Whether it is a stopword (function word)
        frequency_score: Usage frequency (computed from corpora)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    
    Business Rules:
        - The term must have at least 1 character
        - The term is always normalized to lowercase
        - Stopwords should have frequency_score ignored in analysis
        - Only nouns have a meaningful noun_class
    
    Examples:
        >>> term = SwahiliTerm(term="mtu", noun_class=BantuClass.M_WA)
        >>> term.is_noun
        True
        >>> term.update_frequency(5.0)
        >>> term.frequency_score
        5.0
    """
    term: str = Field(..., min_length=1, max_length=100)
    root: Optional[MorphologicalRoot] = None
    noun_class: BantuClass = BantuClass.UNKNOWN
    etymology: Etymology = Etymology.UNKNOWN
    word_type: WordType = WordType.UNKNOWN
    is_stopword: bool = False
    frequency_score: float = Field(default=0.0, ge=0.0)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = False  # Keep enums as objects
        validate_assignment = True  # Validate on assignment
    
    @field_validator('term')
    @classmethod
    def normalize_term(cls, v: str) -> str:
        """
        Normalize the term: lowercase and trim spaces.
        
        Args:
            v: Term to normalize
            
        Returns:
            Normalized term
        """
        return v.strip().lower()
    
    @property
    def is_noun(self) -> bool:
        """Check whether this is a noun."""
        return self.word_type == WordType.NOUN
    
    @property
    def is_verb(self) -> bool:
        """Check whether this is a verb."""
        return self.word_type == WordType.VERB
    
    @property
    def has_bantu_class(self) -> bool:
        """Check whether a Bantu class has been identified."""
        return self.noun_class.is_identified
    
    @property
    def is_native(self) -> bool:
        """Check whether this is a native Bantu word."""
        return self.etymology.is_native
    
    def update_frequency(self, increment: float = 1.0) -> None:
        """
        Increment the term's usage frequency.

        Business Rule: Stopwords should not have their frequency
        incremented in semantic analysis.
        
        Args:
            increment: Increment value (default: 1.0)
        """
        if not self.is_stopword:
            self.frequency_score += increment
        self.updated_at = datetime.utcnow()
    
    def mark_as_stopword(self) -> None:
        """
        Mark the term as a stopword.

        Business Rule: Marking a term as a stopword resets its frequency.
        """
        self.is_stopword = True
        self.frequency_score = 0.0
        self.updated_at = datetime.utcnow()
    
    def set_word_type(self, word_type: WordType) -> None:
        """
        Set the grammatical type.

        Business Rule: If the type is not noun, remove the Bantu class.
        
        Args:
            word_type: Grammatical type
        """
        self.word_type = word_type
        if word_type != WordType.NOUN:
            self.noun_class = BantuClass.UNKNOWN
        self.updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        """String representation."""
        return f"SwahiliTerm('{self.term}', {self.word_type.value})"
    
    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"SwahiliTerm(term='{self.term}', "
            f"word_type={self.word_type.value}, "
            f"noun_class={self.noun_class.value})"
        )

    def to_lexeme(self) -> Lexeme:
        """
        Convert the legacy compatibility model into the new Lexeme shape.

        This keeps existing code working while the rest of the application
        migrates away from term-centric modeling.
        """
        lexeme = Lexeme(
            lemma=self.term,
            root=self.root,
            noun_class=self.noun_class,
            etymology=self.etymology,
            word_type=self.word_type,
        )
        lexeme.add_word_form(
            WordForm(
                lexeme_lemma=self.term,
                form=self.term,
                root=self.root,
                word_type=self.word_type,
                is_canonical=True,
            )
        )
        return lexeme


class DictionaryEntry(BaseModel):
    """
    Entity: Complete dictionary entry.

    Related to SwahiliTerm (aggregate root) and adds semantic
    information from the Kamusi dictionary.
    
    Attributes:
        term: Swahili term (aggregate root)
        meaning: Definition in Swahili
        english_translation: English translation
        synonyms: List of synonyms
        antonyms: List of antonyms
        usage_examples: Usage examples in sentences
        usage_context: Usage context (formal, informal, etc.)
    
    Business Rules:
        - It must have at least one meaning
        - Synonyms must be different words from the main term
        - Examples should contain the term
    
    Examples:
        >>> term = SwahiliTerm(term="mtu")
        >>> entry = DictionaryEntry(
        ...     term=term,
        ...     meaning="binadamu",
        ...     english_translation="person"
        ... )
        >>> entry.add_synonym("binadamu")
        >>> len(entry.synonyms)
        1
    """
    term: SwahiliTerm
    meaning: str = Field(..., min_length=1)
    english_translation: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)
    antonyms: List[str] = Field(default_factory=list)
    usage_examples: List[str] = Field(default_factory=list)
    usage_context: Optional[str] = None  # formal, informal, slang, technical
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    def add_synonym(self, synonym: str) -> None:
        """
        Add a synonym if it is not already present.

        Business Rule: Do not add the term itself as a synonym.
        
        Args:
            synonym: Synonym word
        """
        synonym = synonym.strip().lower()
        if synonym != self.term.term and synonym not in self.synonyms:
            self.synonyms.append(synonym)
    
    def add_antonym(self, antonym: str) -> None:
        """
        Add an antonym if it is not already present.
        
        Args:
            antonym: Antonym word
        """
        antonym = antonym.strip().lower()
        if antonym not in self.antonyms:
            self.antonyms.append(antonym)
    
    def add_usage_example(self, example: str) -> None:
        """
        Add a usage example.

        Business Rule: The example should contain the term (relaxed validation).
        
        Args:
            example: Example sentence
        """
        example = example.strip()
        if example and example not in self.usage_examples:
            self.usage_examples.append(example)
    
    @property
    def has_translation(self) -> bool:
        """Check whether an English translation is present."""
        return self.english_translation is not None
    
    @property
    def has_synonyms(self) -> bool:
        """Check whether synonyms are present."""
        return len(self.synonyms) > 0
    
    @property
    def has_examples(self) -> bool:
        """Check whether usage examples are present."""
        return len(self.usage_examples) > 0
    
    def __str__(self) -> str:
        """String representation."""
        return f"DictionaryEntry('{self.term.term}': {self.meaning})"


class VerbConjugation(BaseModel):
    """
    Entity: Verb conjugation.

    Represents a specific conjugated form of a Swahili verb.
    
    Attributes:
        verb_root: Verb root (e.g. "-soma" for "to read")
        tense: Verb tense (present, past, future, etc.)
        person: Grammatical person (1sg, 2sg, 3sg, 1pl, 2pl, 3pl)
        form: Full conjugated form (e.g. "ninasoma")
        prefix_chain: Prefix chain (e.g. "ni-na-")
        is_affirmative: Whether the form is affirmative (vs. negative)
    
    Business Rules:
        - Verb roots must start with a hyphen (convention)
        - The form should be consistent with prefix and root
    
    Examples:
        >>> conj = VerbConjugation(
        ...     verb_root="-soma",
        ...     tense="present",
        ...     person="1sg",
        ...     form="ninasoma",
        ...     prefix_chain="ni-na-"
        ... )
        >>> conj.is_first_person
        True
    """
    verb_root: str
    tense: str  # present, past, future, perfect, etc.
    person: str  # 1sg, 2sg, 3sg, 1pl, 2pl, 3pl
    form: str
    prefix_chain: Optional[str] = None
    is_affirmative: bool = True
    
    @field_validator('verb_root')
    @classmethod
    def validate_root(cls, v: str) -> str:
        """
        Ensure verb roots start with a hyphen.
        
        Args:
            v: Verb root
            
        Returns:
            Root normalized with hyphen
        """
        v = v.strip().lower()
        if not v.startswith('-'):
            return f'-{v}'
        return v
    
    @property
    def is_first_person(self) -> bool:
        """Check whether this is first person."""
        return self.person.startswith('1')
    
    @property
    def is_singular(self) -> bool:
        """Check whether this is singular."""
        return self.person.endswith('sg')
    
    @property
    def is_plural(self) -> bool:
        """Check whether this is plural."""
        return self.person.endswith('pl')
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.form} ({self.tense}, {self.person})"


class POSRecord(BaseModel):
    """
    Entity: Record of Part-of-Speech.
    
    Represents a grammatical annotation of a word in a specific sentence
    context (Masakhane-POS data).
    
    Attributes:
        term: Annotated word
        tag: Grammatical tag (NOUN, VERB, ADJ, etc.)
        prefix_chain: Chain of morphological prefixes
        sentence_id: Sentence ID in the corpus
        word_order: Word position in the sentence
        confidence: Annotation confidence [0.0, 1.0]
    
    Business Rules:
        - sentence_id and word_order identify a unique position
        - default confidence is 1.0 (manual annotation)
    """
    term: str
    tag: str  # NOUN, VERB, ADJ, ADP, DET, etc.
    prefix_chain: Optional[str] = None
    sentence_id: int = Field(..., ge=0)
    word_order: int = Field(..., ge=0)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    
    @field_validator('term')
    @classmethod
    def normalize_term(cls, v: str) -> str:
        """Normalize the term."""
        return v.strip().lower()
    
    @field_validator('tag')
    @classmethod
    def normalize_tag(cls, v: str) -> str:
        """Normalize the tag to uppercase."""
        return v.strip().upper()
    
    @property
    def is_confident(self, threshold: float = 0.8) -> bool:
        """Check whether the annotation has high confidence."""
        return self.confidence >= threshold
    
    def __str__(self) -> str:
        """String representation."""
        return f"{self.term}/{self.tag}"


class NewsArticle(BaseModel):
    """
    Aggregate: News article.

    Represents a complete article with associated analyses.
    
    Attributes:
        content: Full text content
        category: News category (Kitaifa, Kimataifa, etc.)
        date_published: Publication date
        sentiment_score: Sentiment analysis
        entities_mentioned: Mentioned entities (NER)
        source_url: Original source URL
    
    Business Rules:
        - Content cannot be empty
        - Sentiment is computed, not manually provided
        - Entities are extracted through NER
    
    Examples:
        >>> article = NewsArticle(
        ...     content="Rais ametembelea Zanzibar...",
        ...     category="Kitaifa"
        ... )
        >>> sentiment = SentimentScore(polarity=0.5, confidence=0.8)
        >>> article.analyze_sentiment(sentiment)
        >>> article.has_sentiment
        True
    """
    content: str = Field(..., min_length=10)
    category: str
    date_published: Optional[datetime] = None
    sentiment_score: Optional[SentimentScore] = None
    entities_mentioned: List[str] = Field(default_factory=list)
    source_url: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
    
    def analyze_sentiment(self, score: SentimentScore) -> None:
        """
        Attach sentiment analysis to the article.

        Business Rule: Sentiment must be computed, not manually provided.
        
        Args:
            score: Computed sentiment score
        """
        self.sentiment_score = score
    
    def add_entity(self, entity: str, entity_type: Optional[EntityType] = None) -> None:
        """
        Add an entity mentioned in the article.
        
        Args:
            entity: Entity name
            entity_type: Entity type (optional)
        """
        entity = entity.strip()
        if entity and entity not in self.entities_mentioned:
            self.entities_mentioned.append(entity)
    
    @property
    def has_sentiment(self) -> bool:
        """Check whether sentiment analysis is present."""
        return self.sentiment_score is not None
    
    @property
    def has_entities(self) -> bool:
        """Check whether identified entities are present."""
        return len(self.entities_mentioned) > 0
    
    @property
    def sentiment_label(self) -> Optional[str]:
        """Return the sentiment label if available."""
        if self.sentiment_score:
            return self.sentiment_score.label
        return None
    
    @property
    def word_count(self) -> int:
        """Count the words in the article."""
        return len(self.content.split())
    
    def __str__(self) -> str:
        """String representation."""
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"NewsArticle({self.category}: {preview})"


# Usage example (for tests/documentation)
if __name__ == "__main__":
    # Create term
    term = SwahiliTerm(
        term="mtu",
        noun_class=BantuClass.M_WA,
        word_type=WordType.NOUN,
        etymology=Etymology.BANTU
    )
    print(f"Term: {term}")
    print(f"Is noun: {term.is_noun}")
    print(f"Has Bantu class: {term.has_bantu_class}")
    
    # Create dictionary entry
    entry = DictionaryEntry(
        term=term,
        meaning="binadamu",
        english_translation="person"
    )
    entry.add_synonym("binadamu")
    entry.add_usage_example("Mtu huyu ni rafiki yangu")
    print(f"\nEntry: {entry}")
    print(f"Synonyms: {entry.synonyms}")
    
    # Create article
    article = NewsArticle(
        content="Rais wa Tanzania ametembelea mkoa wa Zanzibar.",
        category="Kitaifa"
    )
    sentiment = SentimentScore(polarity=0.3, confidence=0.85)
    article.analyze_sentiment(sentiment)
    article.add_entity("Tanzania")
    article.add_entity("Zanzibar")
    print(f"\nArticle: {article}")
    print(f"Sentiment: {article.sentiment_label}")
    print(f"Entities: {article.entities_mentioned}")
