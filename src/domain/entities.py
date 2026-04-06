"""
Domain Layer - Entities

Entities são objetos com identidade única que persiste ao longo do tempo,
mesmo quando seus atributos mudam. São os objetos centrais do domínio.

Characteristics:
- Possuem identidade única (ID)
- Mutáveis (podem mudar de estado)
- Comparação por identidade (ID), não por valor
- Encapsulam regras de negócio
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
    EntityType
)


class SwahiliTerm(BaseModel):
    """
    Agregado Raiz: Termo no vocabulário Swahili.
    
    Representa uma palavra única no vocabulário com todos os seus
    metadados linguísticos e semânticos. É o agregado raiz do domínio.
    
    Attributes:
        term: A palavra em Swahili (normalizada, lowercase)
        root: Raiz morfológica (se identificada)
        noun_class: Classe nominal Bantu (para substantivos)
        etymology: Origem etimológica da palavra
        word_type: Tipo gramatical (noun, verb, etc)
        is_stopword: Se é uma stopword (palavra funcional)
        frequency_score: Frequência de uso (calculada dos corpora)
        created_at: Timestamp de criação
        updated_at: Timestamp de última atualização
    
    Business Rules:
        - O termo deve ter pelo menos 1 caractere
        - O termo é sempre normalizado para lowercase
        - Stopwords devem ter frequency_score ignorado em análises
        - Apenas substantivos têm noun_class significativa
    
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
        use_enum_values = False  # Mantém enums como objetos
        validate_assignment = True  # Valida ao atribuir valores
    
    @field_validator('term')
    @classmethod
    def normalize_term(cls, v: str) -> str:
        """
        Normaliza o termo: lowercase e remove espaços.
        
        Args:
            v: Termo a normalizar
            
        Returns:
            Termo normalizado
        """
        return v.strip().lower()
    
    @property
    def is_noun(self) -> bool:
        """Verifica se é um substantivo."""
        return self.word_type == WordType.NOUN
    
    @property
    def is_verb(self) -> bool:
        """Verifica se é um verbo."""
        return self.word_type == WordType.VERB
    
    @property
    def has_bantu_class(self) -> bool:
        """Verifica se tem classe Bantu identificada."""
        return self.noun_class.is_identified
    
    @property
    def is_native(self) -> bool:
        """Verifica se é palavra nativa (Bantu)."""
        return self.etymology.is_native
    
    def update_frequency(self, increment: float = 1.0) -> None:
        """
        Incrementa a frequência de uso do termo.
        
        Business Rule: Stopwords não devem ter frequência incrementada
        em análises semânticas.
        
        Args:
            increment: Valor a incrementar (padrão: 1.0)
        """
        if not self.is_stopword:
            self.frequency_score += increment
        self.updated_at = datetime.utcnow()
    
    def mark_as_stopword(self) -> None:
        """
        Marca o termo como stopword.
        
        Business Rule: Ao marcar como stopword, a frequência é resetada.
        """
        self.is_stopword = True
        self.frequency_score = 0.0
        self.updated_at = datetime.utcnow()
    
    def set_word_type(self, word_type: WordType) -> None:
        """
        Define o tipo gramatical.
        
        Business Rule: Se não for substantivo, remove classe Bantu.
        
        Args:
            word_type: Tipo gramatical
        """
        self.word_type = word_type
        if word_type != WordType.NOUN:
            self.noun_class = BantuClass.UNKNOWN
        self.updated_at = datetime.utcnow()
    
    def __str__(self) -> str:
        """Representação em string."""
        return f"SwahiliTerm('{self.term}', {self.word_type.value})"
    
    def __repr__(self) -> str:
        """Representação para debug."""
        return (
            f"SwahiliTerm(term='{self.term}', "
            f"word_type={self.word_type.value}, "
            f"noun_class={self.noun_class.value})"
        )


class DictionaryEntry(BaseModel):
    """
    Entidade: Entrada de dicionário completa.
    
    Relaciona-se com SwahiliTerm (agregado raiz) e adiciona
    informações semânticas do dicionário Kamusi.
    
    Attributes:
        term: Termo Swahili (agregado raiz)
        meaning: Definição em Swahili
        english_translation: Tradução para inglês
        synonyms: Lista de sinônimos
        antonyms: Lista de antônimos
        usage_examples: Exemplos de uso em frases
        usage_context: Contexto de uso (formal, informal, etc)
    
    Business Rules:
        - Deve ter pelo menos um significado
        - Sinônimos devem ser palavras diferentes do termo principal
        - Exemplos devem conter o termo
    
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
        Adiciona um sinônimo se ainda não existir.
        
        Business Rule: Não adiciona o próprio termo como sinônimo.
        
        Args:
            synonym: Palavra sinônima
        """
        synonym = synonym.strip().lower()
        if synonym != self.term.term and synonym not in self.synonyms:
            self.synonyms.append(synonym)
    
    def add_antonym(self, antonym: str) -> None:
        """
        Adiciona um antônimo se ainda não existir.
        
        Args:
            antonym: Palavra antônima
        """
        antonym = antonym.strip().lower()
        if antonym not in self.antonyms:
            self.antonyms.append(antonym)
    
    def add_usage_example(self, example: str) -> None:
        """
        Adiciona um exemplo de uso.
        
        Business Rule: O exemplo deve conter o termo (validação relaxada).
        
        Args:
            example: Frase de exemplo
        """
        example = example.strip()
        if example and example not in self.usage_examples:
            self.usage_examples.append(example)
    
    @property
    def has_translation(self) -> bool:
        """Verifica se tem tradução para inglês."""
        return self.english_translation is not None
    
    @property
    def has_synonyms(self) -> bool:
        """Verifica se tem sinônimos."""
        return len(self.synonyms) > 0
    
    @property
    def has_examples(self) -> bool:
        """Verifica se tem exemplos de uso."""
        return len(self.usage_examples) > 0
    
    def __str__(self) -> str:
        """Representação em string."""
        return f"DictionaryEntry('{self.term.term}': {self.meaning})"


class VerbConjugation(BaseModel):
    """
    Entidade: Conjugação verbal.
    
    Representa uma forma conjugada específica de um verbo Swahili.
    
    Attributes:
        verb_root: Raiz do verbo (e.g., "-soma" para ler)
        tense: Tempo verbal (present, past, future, etc)
        person: Pessoa gramatical (1sg, 2sg, 3sg, 1pl, 2pl, 3pl)
        form: Forma conjugada completa (e.g., "ninasoma")
        prefix_chain: Cadeia de prefixos (e.g., "ni-na-")
        is_affirmative: Se é forma afirmativa (vs. negativa)
    
    Business Rules:
        - Raízes verbais devem começar com hífen (convenção)
        - Forma deve ser consistente com prefixo e raiz
    
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
        Garante que raízes verbais começam com hífen.
        
        Args:
            v: Raiz verbal
            
        Returns:
            Raiz normalizada com hífen
        """
        v = v.strip().lower()
        if not v.startswith('-'):
            return f'-{v}'
        return v
    
    @property
    def is_first_person(self) -> bool:
        """Verifica se é primeira pessoa."""
        return self.person.startswith('1')
    
    @property
    def is_singular(self) -> bool:
        """Verifica se é singular."""
        return self.person.endswith('sg')
    
    @property
    def is_plural(self) -> bool:
        """Verifica se é plural."""
        return self.person.endswith('pl')
    
    def __str__(self) -> str:
        """Representação em string."""
        return f"{self.form} ({self.tense}, {self.person})"


class POSRecord(BaseModel):
    """
    Entity: Record of Part-of-Speech.
    
    Representa uma anotação gramatical de uma palavra em um contexto
    sentencial específico (dados do Masakhane-POS).
    
    Attributes:
        term: Palavra anotada
        tag: Tag gramatical (NOUN, VERB, ADJ, etc)
        prefix_chain: Cadeia de prefixos morfológicos
        sentence_id: ID da sentença no corpus
        word_order: Posição da palavra na sentença
        confidence: Confiança da anotação [0.0, 1.0]
    
    Business Rules:
        - sentence_id e word_order identificam posição única
        - confidence padrão é 1.0 (anotação manual)
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
        """Normalizes o termo."""
        return v.strip().lower()
    
    @field_validator('tag')
    @classmethod
    def normalize_tag(cls, v: str) -> str:
        """Normalizes a tag para maiúsculas."""
        return v.strip().upper()
    
    @property
    def is_confident(self, threshold: float = 0.8) -> bool:
        """Checks if a anotação tem alta confiança."""
        return self.confidence >= threshold
    
    def __str__(self) -> str:
        """Representação em string."""
        return f"{self.term}/{self.tag}"


class NewsArticle(BaseModel):
    """
    Agregado: Artigo de notícias.
    
    Representa um artigo completo com análises associadas.
    
    Attributes:
        content: Conteúdo textual completo
        category: Categoria da notícia (Kitaifa, Kimataifa, etc)
        date_published: Data de publicação
        sentiment_score: Análise de sentimento
        entities_mentioned: Entidades mencionadas (NER)
        source_url: URL da fonte original
    
    Business Rules:
        - Conteúdo não pode estar vazio
        - Sentimento é calculado, não fornecido manualmente
        - Entidades são extraídas via NER
    
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
        Associa análise de sentimento ao artigo.
        
        Business Rule: Sentimento deve ser calculado, não fornecido manualmente.
        
        Args:
            score: Pontuação de sentimento calculada
        """
        self.sentiment_score = score
    
    def add_entity(self, entity: str, entity_type: Optional[EntityType] = None) -> None:
        """
        Adiciona entidade mencionada no artigo.
        
        Args:
            entity: Nome da entidade
            entity_type: Tipo da entidade (opcional)
        """
        entity = entity.strip()
        if entity and entity not in self.entities_mentioned:
            self.entities_mentioned.append(entity)
    
    @property
    def has_sentiment(self) -> bool:
        """Verifica se tem análise de sentimento."""
        return self.sentiment_score is not None
    
    @property
    def has_entities(self) -> bool:
        """Verifica se tem entidades identificadas."""
        return len(self.entities_mentioned) > 0
    
    @property
    def sentiment_label(self) -> Optional[str]:
        """Retorna label de sentimento se disponível."""
        if self.sentiment_score:
            return self.sentiment_score.label
        return None
    
    @property
    def word_count(self) -> int:
        """Conta palavras no artigo."""
        return len(self.content.split())
    
    def __str__(self) -> str:
        """Representação em string."""
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"NewsArticle({self.category}: {preview})"


# Example de uso (para testes/documentação)
if __name__ == "__main__":
    # Criar termo
    term = SwahiliTerm(
        term="mtu",
        noun_class=BantuClass.M_WA,
        word_type=WordType.NOUN,
        etymology=Etymology.BANTU
    )
    print(f"Termo: {term}")
    print(f"É substantivo: {term.is_noun}")
    print(f"Tem classe Bantu: {term.has_bantu_class}")
    
    # Criar entrada de dicionário
    entry = DictionaryEntry(
        term=term,
        meaning="binadamu",
        english_translation="person"
    )
    entry.add_synonym("binadamu")
    entry.add_usage_example("Mtu huyu ni rafiki yangu")
    print(f"\nEntrada: {entry}")
    print(f"Sinônimos: {entry.synonyms}")
    
    # Criar artigo
    article = NewsArticle(
        content="Rais wa Tanzania ametembelea mkoa wa Zanzibar.",
        category="Kitaifa"
    )
    sentiment = SentimentScore(polarity=0.3, confidence=0.85)
    article.analyze_sentiment(sentiment)
    article.add_entity("Tanzania")
    article.add_entity("Zanzibar")
    print(f"\nArtigo: {article}")
    print(f"Sentimento: {article.sentiment_label}")
    print(f"Entidades: {article.entities_mentioned}")
