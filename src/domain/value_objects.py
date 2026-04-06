"""
Domain Layer - Value Objects

Value Objects are immutable objects that represent domain concepts
through their attributes. Dois Value Objects com os mesmos atributos são
considered equal.

Characteristics:
- Immutable (frozen=True)
- No identity of their own
- Comparison by value
- Self-validating
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class BantuClass(str, Enum):
    """
    Value Object: Classes Nominais Bantu (Ngeli) do Swahili.
    
    O Swahili, como língua Bantu, possui um sistema de classes nominais
    que agrupam substantivos por características semânticas e morfológicas.
    
    Examples:
        M_WA (1/2): mtu (pessoa) → watu (pessoas)
        M_MI (3/4): mti (árvore) → miti (árvores)
        KI_VI (7/8): kiti (cadeira) → viti (cadeiras)
    """
    M_WA = "1/2"          # Pessoas (Mtu/Watu)
    M_MI = "3/4"          # Plantas, objetos alongados (Mti/Miti)
    JI_MA = "5/6"         # Frutas, aumentativos (Tunda/Matunda)
    KI_VI = "7/8"         # Ferramentas, artefatos (Kiti/Viti)
    N_N = "9/10"          # Animais, objetos comuns (Nyumba/Nyumba)
    U = "11/14"           # Abstrações, singular (Uzuri)
    PA_KU_MU = "16/17/18" # Locatives (pahali, kule, ndani)
    UNKNOWN = "N/A"       # Classe não identificada
    
    @property
    def description(self) -> str:
        """Returns descrição semântica da classe."""
        descriptions = {
            self.M_WA: "Pessoas e seres humanos",
            self.M_MI: "Plantas e objetos alongados",
            self.JI_MA: "Frutas, pares e aumentativos",
            self.KI_VI: "Ferramentas e artefatos",
            self.N_N: "Animais e objetos comuns",
            self.U: "Abstrações e conceitos",
            self.PA_KU_MU: "Locativos (lugar, direção)",
            self.UNKNOWN: "Classe desconhecida"
        }
        return descriptions.get(self, "Sem descrição")
    
    @property
    def is_identified(self) -> bool:
        """Checks if a classe foi identificada."""
        return self != self.UNKNOWN


class Etymology(str, Enum):
    """
    Value Object: Origem etimológica de palavras Swahili.
    
    O Swahili é uma língua com influências de múltiplas fontes:
    - Bantu: Base gramatical e vocabulário fundamental
    - Árabe: ~40% do vocabulário (comércio, religião)
    - Inglês: Loanwords modernos (tecnologia, administração)
    - Português: Período colonial
    - Outros: Alemão, Hindi, Persa
    """
    BANTU = "bantu"           # Bantu origin (native)
    ARABIC = "arabic"         # Loanword árabe
    ENGLISH = "english"       # Loanword inglês
    PORTUGUESE = "portuguese" # Loanword português
    GERMAN = "german"         # Loanword alemão
    INDIAN = "indian"         # Loanword de línguas indianas (Hindi, Gujarati)
    PERSIAN = "persian"       # Loanword persa
    UNKNOWN = "unknown"       # Origem desconhecida
    
    @property
    def is_native(self) -> bool:
        """Checks if a palavra é de origem Bantu (nativa)."""
        return self == self.BANTU
    
    @property
    def is_loanword(self) -> bool:
        """Checks if a palavra é empréstimo de outra língua."""
        return self not in [self.BANTU, self.UNKNOWN]


class WordType(str, Enum):
    """
    Value Object: Grammatical type da palavra.
    
    Classification morfossintática básica.
    """
    NOUN = "noun"               # Noun (nomino)
    VERB = "verb"               # Verb (kitenzi)
    ADJECTIVE = "adjective"     # Adjective (kivumishi)
    ADVERB = "adverb"           # Adverb (kielezi)
    PRONOUN = "pronoun"         # Pronome
    CONJUNCTION = "conjunction" # Conjunção
    PREPOSITION = "preposition" # Preposição
    INTERJECTION = "interjection" # Interjeição
    DETERMINER = "determiner"   # Determinante
    NUMERAL = "numeral"         # Numeral
    UNKNOWN = "unknown"         # Tipo desconhecido
    
    @property
    def is_content_word(self) -> bool:
        """Checks if é palavra de conteúdo (não função)."""
        return self in [self.NOUN, self.VERB, self.ADJECTIVE, self.ADVERB]


@dataclass(frozen=True)
class SentimentScore:
    """
    Value Object: Sentiment score de um texto.
    
    Representa a polaridade e confiança de uma análise de sentimento.
    Imutável e auto-validável.
    
    Attributes:
        polarity: Polaridade do sentimento [-1.0, 1.0]
                 -1.0 = muito negativo
                  0.0 = neutro
                 +1.0 = muito positivo
        confidence: Confiança da análise [0.0, 1.0]
                   0.0 = sem confiança
                   1.0 = total confiança
    
    Examples:
        >>> score = SentimentScore(polarity=0.8, confidence=0.9)
        >>> score.label
        'positive'
        >>> score.is_positive
        True
    """
    polarity: float
    confidence: float
    
    def __post_init__(self):
        """Validates values após inicialização."""
        if not -1.0 <= self.polarity <= 1.0:
            raise ValueError(
                f"Polarity must be between -1.0 and 1.0, got {self.polarity}"
            )
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"Confidence must be between 0.0 and 1.0, got {self.confidence}"
            )
    
    @property
    def label(self) -> str:
        """
        Returns label categórico baseado na polaridade.
        
        Returns:
            'positive', 'negative' ou 'neutral'
        """
        if self.polarity > 0.1:
            return "positive"
        elif self.polarity < -0.1:
            return "negative"
        return "neutral"
    
    @property
    def is_positive(self) -> bool:
        """Checks if o sentimento é positivo."""
        return self.polarity > 0.1
    
    @property
    def is_negative(self) -> bool:
        """Checks if o sentimento é negativo."""
        return self.polarity < -0.1
    
    @property
    def is_neutral(self) -> bool:
        """Checks if o sentimento é neutro."""
        return -0.1 <= self.polarity <= 0.1
    
    @property
    def is_confident(self, threshold: float = 0.7) -> bool:
        """Checks if a análise tem alta confiança."""
        return self.confidence >= threshold
    
    def __str__(self) -> str:
        """Representação em string."""
        return f"{self.label} (polarity={self.polarity:.2f}, confidence={self.confidence:.2f})"


@dataclass(frozen=True)
class MorphologicalRoot:
    """
    Value Object: Raiz morfológica de uma palavra Swahili.
    
    Representa a decomposição morfológica de uma palavra em:
    - Prefixo (opcional): Marcadores gramaticais (wa-, ki-, m-)
    - Raiz: Core semântico da palavra
    - Sufixo (opcional): Marcadores gramaticais finais (-a, -i, -e)
    
    Examples:
        >>> root = MorphologicalRoot(root="som", prefix="wa", suffix="a")
        >>> root.full_word
        'wasoma'
        >>> root.has_prefix
        True
    """
    root: str
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    
    def __post_init__(self):
        """Valida a raiz."""
        if not self.root or len(self.root) < 1:
            raise ValueError("Root cannot be empty")
        
        # Normalizes para lowercase
        object.__setattr__(self, 'root', self.root.lower())
        if self.prefix:
            object.__setattr__(self, 'prefix', self.prefix.lower())
        if self.suffix:
            object.__setattr__(self, 'suffix', self.suffix.lower())
    
    @property
    def full_word(self) -> str:
        """
        Reconstructs a palavra completa a partir dos componentes.
        
        Returns:
            Palavra completa (prefix + root + suffix)
        """
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        parts.append(self.root)
        if self.suffix:
            parts.append(self.suffix)
        return ''.join(parts)
    
    @property
    def has_prefix(self) -> bool:
        """Checks if possui prefixo."""
        return self.prefix is not None
    
    @property
    def has_suffix(self) -> bool:
        """Checks if possui sufixo."""
        return self.suffix is not None
    
    @property
    def is_simple(self) -> bool:
        """Checks if é palavra simples (sem afixos)."""
        return not (self.has_prefix or self.has_suffix)
    
    def __str__(self) -> str:
        """Representação em string."""
        if self.is_simple:
            return f"[{self.root}]"
        return f"[{self.prefix or ''}-{self.root}-{self.suffix or ''}]"


@dataclass(frozen=True)
class EntityType:
    """
    Value Object: Entity type nomeada (NER).
    
    Representa categorias de Named Entity Recognition.
    
    Attributes:
        group: Grupo da entidade (PER, LOC, ORG, DATE, etc.)
        subtype: Subtipo opcional (e.g., 'country' para LOC)
    """
    group: str
    subtype: Optional[str] = None
    
    def __post_init__(self):
        """Valida e normaliza o grupo."""
        valid_groups = {'PER', 'LOC', 'ORG', 'DATE', 'TIME', 'MONEY', 'PERCENT', 'MISC'}
        
        group_upper = self.group.upper()
        if group_upper not in valid_groups:
            raise ValueError(f"Invalid entity group: {self.group}")
        
        object.__setattr__(self, 'group', group_upper)
        
        if self.subtype:
            object.__setattr__(self, 'subtype', self.subtype.lower())
    
    @property
    def is_person(self) -> bool:
        """Checks if é uma pessoa."""
        return self.group == 'PER'
    
    @property
    def is_location(self) -> bool:
        """Checks if é uma localização."""
        return self.group == 'LOC'
    
    @property
    def is_organization(self) -> bool:
        """Checks if é uma organização."""
        return self.group == 'ORG'
    
    def __str__(self) -> str:
        """Representação em string."""
        if self.subtype:
            return f"{self.group}:{self.subtype}"
        return self.group


# Example de uso (para testes/documentação)
if __name__ == "__main__":
    # Testar BantuClass
    bantu = BantuClass.M_WA
    print(f"Classe: {bantu}, Descrição: {bantu.description}")
    
    # Testar SentimentScore
    sentiment = SentimentScore(polarity=0.75, confidence=0.85)
    print(f"Sentimento: {sentiment}")
    
    # Testar MorphologicalRoot
    root = MorphologicalRoot(root="som", prefix="wa")
    print(f"Raiz: {root}, Palavra completa: {root.full_word}")
    
    # Testar EntityType
    entity = EntityType(group="PER", subtype="politician")
    print(f"Entidade: {entity}, É pessoa: {entity.is_person}")
