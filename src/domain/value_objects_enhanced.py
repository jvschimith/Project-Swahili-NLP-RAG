"""
Domain Layer - Enhanced Value Objects (v2.1)

Phase 1 Enhancements:
- VerbTense system with complete tense markers
- SwahiliTenses enumeration
- MasakhanePOS standardized tags
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional


# ==================== PHASE 1: TENSE SYSTEM ====================

@dataclass(frozen=True)
class VerbTense:
    """
    Value Object: Swahili verb tense/aspect system.
    
    Swahili has a rich tense/aspect system with 12+ tenses.
    Each tense has specific markers that appear in verb conjugations.
    
    Examples:
        present: ni-na-soma (I am reading)
        past: ni-li-soma (I read)
        future: ni-ta-soma (I will read)
        perfect: ni-me-soma (I have read)
    """
    marker: str
    name: str
    aspect: str  # past, present, future, perfect, habitual, etc.
    is_negative: bool = False
    time_reference: str = "present"  # past, present, future
    
    def __str__(self) -> str:
        return f"{self.name} ({self.marker})"
    
    @property
    def description(self) -> str:
        """Get human-readable description."""
        neg = "Negative " if self.is_negative else ""
        return f"{neg}{self.name} - {self.aspect} aspect"


class SwahiliTenses:
    """
    Complete tense/aspect system for Swahili verbs.
    
    Based on Standard Swahili grammar (Ashton, 1944; TUKI, 2004).
    """
    
    # Affirmative tenses
    PRESENT = VerbTense("na", "Present Continuous", "present", False, "present")
    PAST = VerbTense("li", "Simple Past", "past", False, "past")
    FUTURE = VerbTense("ta", "Simple Future", "future", False, "future")
    PERFECT = VerbTense("me", "Present Perfect", "perfect", False, "present")
    HABITUAL = VerbTense("hu", "Habitual", "habitual", False, "present")
    
    # Perfect tenses
    PAST_PERFECT = VerbTense("li_me", "Past Perfect", "past_perfect", False, "past")
    FUTURE_PERFECT = VerbTense("ta_me", "Future Perfect", "future_perfect", False, "future")
    
    # Conditional/Subjunctive
    CONDITIONAL = VerbTense("nge", "Conditional", "conditional", False, "hypothetical")
    POTENTIAL = VerbTense("ngali", "Potential", "potential", False, "hypothetical")
    SUBJUNCTIVE = VerbTense("", "Subjunctive", "subjunctive", False, "modal")
    
    # Infinitive and Imperative
    INFINITIVE = VerbTense("ku", "Infinitive", "infinitive", False, "timeless")
    IMPERATIVE = VerbTense("", "Imperative", "imperative", False, "present")
    
    # Negative forms
    NEG_PRESENT = VerbTense("", "Negative Present", "present", True, "present")
    NEG_PAST = VerbTense("ku", "Negative Past", "past", True, "past")
    NEG_FUTURE = VerbTense("ta", "Negative Future", "future", True, "future")
    NEG_PERFECT = VerbTense("ja", "Negative Perfect", "perfect", True, "present")
    
    # Relative tenses
    REL_PRESENT = VerbTense("o", "Relative Present", "relative", False, "present")
    REL_PAST = VerbTense("liye", "Relative Past", "relative", False, "past")
    REL_FUTURE = VerbTense("taka", "Relative Future", "relative", False, "future")
    
    @classmethod
    def get_tense_by_marker(cls, marker: str) -> Optional[VerbTense]:
        """
        Get tense by its marker.
        
        Args:
            marker: Tense marker (e.g., "na", "li", "ta")
            
        Returns:
            VerbTense if found, None otherwise
            
        Examples:
            >>> SwahiliTenses.get_tense_by_marker("na")
            VerbTense(marker='na', name='Present Continuous', ...)
        """
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, VerbTense) and attr.marker == marker:
                return attr
        return None
    
    @classmethod
    def get_all_tenses(cls) -> list[VerbTense]:
        """Get all defined tenses."""
        tenses = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, VerbTense):
                tenses.append(attr)
        return tenses
    
    @classmethod
    def get_affirmative_tenses(cls) -> list[VerbTense]:
        """Get only affirmative tenses."""
        return [t for t in cls.get_all_tenses() if not t.is_negative]
    
    @classmethod
    def get_negative_tenses(cls) -> list[VerbTense]:
        """Get only negative tenses."""
        return [t for t in cls.get_all_tenses() if t.is_negative]


# ==================== PHASE 3: MASAKHANE POS TAGS ====================

class MasakhanePOS(str, Enum):
    """
    Masakhane POS tagset for Swahili.
    
    Standardized tags for East African Bantu languages.
    Based on Universal Dependencies with Bantu-specific extensions.
    
    References:
        - Masakhane NER dataset
        - UD Swahili treebank
        - AfriBooms annotation guidelines
    """
    # Content words
    NOUN = "NOUN"      # Nomino (mtoto, meza, habari)
    VERB = "VERB"      # Kitenzi (kusoma, kunwa, kwenda)
    ADJ = "ADJ"        # Kivumishi (-zuri, -kubwa, -refu)
    ADV = "ADV"        # Kielezi (vizuri, sana, leo)
    
    # Function words
    ADP = "ADP"        # Preposition (kwa, ya, wa, katika)
    CONJ = "CONJ"      # Conjunction (na, au, lakini, kwa sababu)
    SCONJ = "SCONJ"    # Subordinating conjunction (kwamba, kama, ingawa)
    DET = "DET"        # Determiner (huyu, hizi, kile)
    PRON = "PRON"      # Pronoun (mimi, wewe, yeye, sisi)
    NUM = "NUM"        # Numeral (moja, mbili, tatu, ishirini)
    
    # Bantu-specific tags
    AGR = "AGR"        # Agreement marker (a-, wa-, ki-, vi-)
    NC = "NC"          # Noun class prefix (m-, wa-, ki-)
    COP = "COP"        # Copula (ni, si)
    DEM = "DEM"        # Demonstrative (huyu, hizi, kile, huko)
    POSS = "POSS"      # Possessive (-angu, -ako, -ake)
    
    # Other categories
    PART = "PART"      # Particle (ndi-, si-)
    INTJ = "INTJ"      # Interjection (kumbe!, lo!, naam!)
    AUX = "AUX"        # Auxiliary (kuwa, -li-)
    PROPN = "PROPN"    # Proper noun (Tanzania, Samia, Dar es Salaam)
    
    # Punctuation and symbols
    PUNCT = "PUNCT"    # Punctuation (., !, ?)
    SYM = "SYM"        # Symbol ($, %, @)
    X = "X"            # Unknown/Other
    
    @property
    def description(self) -> str:
        """Get description in Swahili."""
        descriptions = {
            self.NOUN: "Nomino (jina la kitu, mtu, mahali)",
            self.VERB: "Kitenzi (kitendo)",
            self.ADJ: "Kivumishi (sifa)",
            self.ADV: "Kielezi (jinsi, wakati, mahali)",
            self.ADP: "Kihusishi (kwa, ya, wa)",
            self.CONJ: "Kiunganishi (na, au, lakini)",
            self.DET: "Kiashiria (huyu, hizi, kile)",
            self.PRON: "Dhamira (mimi, wewe, yeye)",
            self.NUM: "Namba (moja, mbili, tatu)",
            self.AGR: "Kiambishi patano (a-, wa-, ki-)",
            self.NC: "Kiambishi ngeli (m-, wa-, ki-)",
            self.COP: "Kiunganishi (ni, si)",
            self.DEM: "Kiashiria (huyu, hizi, huko)",
            self.POSS: "Kiambishi umiliki (-angu, -ako)",
            self.PART: "Kiambishi (ndi-, si-)",
            self.INTJ: "Kihisishi (lo!, kumbe!)",
            self.AUX: "Kitenzi kisaidizi (kuwa)",
            self.PROPN: "Jina maalum (Tanzania, Juma)",
            self.PUNCT: "Alama za uandishi",
            self.SYM: "Ishara",
            self.X: "Isiyojulikana"
        }
        return descriptions.get(self, "Aina ya neno")
    
    @classmethod
    def from_tag(cls, tag: str) -> 'MasakhanePOS':
        """
        Convert string tag to enum.
        
        Args:
            tag: POS tag string
            
        Returns:
            MasakhanePOS enum value
            
        Examples:
            >>> MasakhanePOS.from_tag("noun")
            MasakhanePOS.NOUN
            >>> MasakhanePOS.from_tag("unknown")
            MasakhanePOS.X
        """
        try:
            return cls(tag.upper())
        except (ValueError, AttributeError):
            return cls.X
    
    @classmethod
    def is_content_word(cls, tag: 'MasakhanePOS') -> bool:
        """Check if tag represents content word."""
        return tag in {cls.NOUN, cls.VERB, cls.ADJ, cls.ADV, cls.PROPN}
    
    @classmethod
    def is_function_word(cls, tag: 'MasakhanePOS') -> bool:
        """Check if tag represents function word."""
        return tag in {cls.ADP, cls.CONJ, cls.SCONJ, cls.DET, cls.PRON, 
                       cls.NUM, cls.PART, cls.AUX, cls.COP}
    
    @classmethod
    def is_bantu_specific(cls, tag: 'MasakhanePOS') -> bool:
        """Check if tag is Bantu-specific."""
        return tag in {cls.AGR, cls.NC, cls.COP, cls.DEM, cls.POSS}


# ==================== EXISTING VALUE OBJECTS (keep as is) ====================

class BantuClass(str, Enum):
    """
    Value Object: Classes Nominais Bantu (Ngeli) do Swahili.
    
    O Swahili, como língua Bantu, possui um sistema de classes nominais
    que agrupam substantivos por características semânticas e morfológicas.
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
            self.UNKNOWN: "Classe não identificada"
        }
        return descriptions.get(self, "Unknown")
    
    @property
    def is_identified(self) -> bool:
        """Verifica se a classe foi identificada."""
        return self != self.UNKNOWN


@dataclass(frozen=True)
class MorphologicalRoot:
    """
    Value Object: Raiz morfológica extraída de uma palavra Swahili.
    
    Representa a decomposição morfológica de uma palavra em seus componentes.
    """
    original: str
    root: str
    prefix: Optional[str] = None
    suffix: Optional[str] = None
    bantu_class: BantuClass = BantuClass.UNKNOWN
    
    def __post_init__(self):
        """Validação pós-inicialização."""
        if not self.root:
            raise ValueError("Root cannot be empty")
        if len(self.root) < 1:
            raise ValueError("Root must have at least 1 character")
    
    @property
    def has_prefix(self) -> bool:
        """Verifica se possui prefixo."""
        return self.prefix is not None and len(self.prefix) > 0
    
    @property
    def has_suffix(self) -> bool:
        """Verifica se possui sufixo."""
        return self.suffix is not None and len(self.suffix) > 0
    
    @property
    def morpheme_count(self) -> int:
        """Conta número de morfemas."""
        count = 1  # raiz sempre presente
        if self.has_prefix:
            count += 1
        if self.has_suffix:
            count += 1
        return count
    
    def reconstruct(self) -> str:
        """Reconstrói a palavra original a partir dos componentes."""
        parts = []
        if self.has_prefix:
            parts.append(self.prefix)
        parts.append(self.root)
        if self.has_suffix:
            parts.append(self.suffix)
        return "".join(parts)


@dataclass(frozen=True)
class SentimentScore:
    """
    Value Object: Score de sentimento calculado.
    """
    polarity: float  # -1.0 (negativo) a +1.0 (positivo)
    label: str      # 'positive', 'negative', 'neutral'
    confidence: float = 1.0
    
    def __post_init__(self):
        """Validação."""
        if not -1.0 <= self.polarity <= 1.0:
            raise ValueError("Polarity must be between -1.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.label not in {'positive', 'negative', 'neutral'}:
            raise ValueError("Label must be 'positive', 'negative', or 'neutral'")
    
    @property
    def is_positive(self) -> bool:
        return self.label == 'positive'
    
    @property
    def is_negative(self) -> bool:
        return self.label == 'negative'
    
    @property
    def is_neutral(self) -> bool:
        return self.label == 'neutral'
    
    @property
    def strength(self) -> str:
        """Classifica a força do sentimento."""
        abs_polarity = abs(self.polarity)
        if abs_polarity >= 0.7:
            return 'strong'
        elif abs_polarity >= 0.4:
            return 'moderate'
        else:
            return 'weak'
