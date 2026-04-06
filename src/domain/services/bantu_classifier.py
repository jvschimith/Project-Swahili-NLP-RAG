"""
Domain Service: Classificador de Classes Bantu

Domain Services encapsulam lógica de negócio que não pertence
naturalmente a nenhuma Entity ou Value Object específico.

Responsibilitys deste serviço:
- Inferir classe nominal Bantu baseada em prefixos morfológicos
- Fornecer descrições semânticas das classes
- Validar consistência de classes

Este é um Domain Service puro:
- Sem dependências de infraestrutura
- Sem side effects
- Testável isoladamente
- Lógica de domínio complexa
"""
from typing import Dict, Tuple, Optional
from loguru import logger

from ..value_objects import BantuClass, WordType


class BantuClassifierService:
    """
    Domain Service: Classificação de classes nominais Bantu.
    
    O Swahili possui um sistema de classes nominais herdado das línguas Bantu,
    onde substantivos são agrupados por prefixos que indicam características
    semânticas e gramaticais.
    
    Classes Principais:
        1/2 (M-WA): Pessoas (mtu/watu - pessoa/pessoas)
        3/4 (M-MI): Plantas (mti/miti - árvore/árvores)
        5/6 (JI-MA): Frutas, pares (jicho/macho - olho/olhos)
        7/8 (KI-VI): Ferramentas (kisu/visu - faca/facas)
        9/10 (N-N): Animais (nyumba/nyumba - casa/casas)
        11/14 (U): Abstrações (uzuri - beleza)
        16/17/18 (PA-KU-MU): Locativos (pahali - lugar)
    
    Business Rules:
        - Apenas substantivos têm classes nominais
        - Prefixo pode variar entre singular e plural
        - Algumas palavras têm múltiplas classes (polissemia)
        - Empréstimos de outras línguas geralmente vão para classe 9/10
    
    Examples:
        >>> classifier = BantuClassifierService()
        >>> classifier.infer_class("mtu", WordType.NOUN)
        BantuClass.M_WA
        >>> classifier.infer_class("kiti", WordType.NOUN)
        BantuClass.KI_VI
        >>> classifier.infer_class("soma", WordType.VERB)
        BantuClass.UNKNOWN
    """
    
    # Mapeamento de prefixos para classes
    # Formato: {(prefixos_singular, prefixos_plural): BantuClass}
    PREFIX_TO_CLASS: Dict[Tuple[str, ...], BantuClass] = {
        # Classe 1/2 - M-WA (Pessoas)
        ('mtu', 'mwa', 'mw', 'mu'): BantuClass.M_WA,
        ('wa',): BantuClass.M_WA,  # Plural
        
        # Classe 3/4 - M-MI (Plantas, objetos)
        ('mti', 'mw'): BantuClass.M_MI,
        ('mi',): BantuClass.M_MI,  # Plural
        
        # Classe 5/6 - JI-MA (Frutas, aumentativos)
        ('ji', 'j'): BantuClass.JI_MA,
        ('ma',): BantuClass.JI_MA,  # Plural
        
        # Classe 7/8 - KI-VI (Ferramentas, diminutivos)
        ('ki', 'ch'): BantuClass.KI_VI,
        ('vi', 'vy'): BantuClass.KI_VI,  # Plural
        
        # Classe 9/10 - N-N (Animais, empréstimos)
        ('n', 'ny', 'ng', 'ndege', 'nyumba'): BantuClass.N_N,
        
        # Classe 11/14 - U (Abstrações)
        ('u',): BantuClass.U,
        
        # Classe 16/17/18 - PA-KU-MU (Locatives)
        ('pa', 'ku', 'mu', 'mw'): BantuClass.PA_KU_MU,
    }
    
    # Casos especiais (palavras que não seguem padrões regulares)
    SPECIAL_CASES: Dict[str, BantuClass] = {
        'mtu': BantuClass.M_WA,
        'watu': BantuClass.M_WA,
        'mti': BantuClass.M_MI,
        'miti': BantuClass.M_MI,
        'kiti': BantuClass.KI_VI,
        'viti': BantuClass.KI_VI,
        'jicho': BantuClass.JI_MA,
        'macho': BantuClass.JI_MA,
        'nyumba': BantuClass.N_N,
        'uzuri': BantuClass.U,
        'pahali': BantuClass.PA_KU_MU,
    }
    
    @classmethod
    def infer_class(cls, word: str, word_type: WordType = WordType.NOUN) -> BantuClass:
        """
        Infere a classe Bantu de uma palavra.
        
        Business Rules:
            - Apenas substantivos têm classes Bantu significativas
            - Verifica casos especiais primeiro
            - Usa matching de prefixos para casos gerais
            - Retorna UNKNOWN se não conseguir classificar
        
        Args:
            word: Palavra em Swahili (normalizada)
            word_type: Tipo gramatical da palavra
            
        Returns:
            BantuClass inferida
            
        Examples:
            >>> BantuClassifierService.infer_class("mtu", WordType.NOUN)
            BantuClass.M_WA
            >>> BantuClassifierService.infer_class("soma", WordType.VERB)
            BantuClass.UNKNOWN
        """
        # Regra 1: Apenas substantivos têm classes Bantu
        if word_type not in [WordType.NOUN, WordType.UNKNOWN]:
            logger.debug(
                f"Word '{word}' is {word_type.value}, not a noun. "
                f"Skipping Bantu class inference."
            )
            return BantuClass.UNKNOWN
        
        # Normalizesr palavra
        word_lower = word.lower().strip()
        
        # Regra 2: Verificar casos especiais primeiro
        if word_lower in cls.SPECIAL_CASES:
            result = cls.SPECIAL_CASES[word_lower]
            logger.debug(f"Found special case: '{word}' → {result.value}")
            return result
        
        # Regra 3: Tentar matching de prefixos
        for prefixes, bantu_class in cls.PREFIX_TO_CLASS.items():
            for prefix in prefixes:
                if word_lower.startswith(prefix):
                    # Verificar se não é apenas o prefixo (palavra deve ter raiz)
                    if len(word_lower) > len(prefix) + 1:
                        logger.debug(
                            f"Matched '{word}' to {bantu_class.value} "
                            f"via prefix '{prefix}'"
                        )
                        return bantu_class
        
        # Regra 4: Se não conseguiu classificar
        logger.debug(f"Could not infer Bantu class for '{word}'")
        return BantuClass.UNKNOWN
    
    @classmethod
    def get_class_description(cls, bantu_class: BantuClass) -> str:
        """
        Retorna descrição semântica detalhada da classe Bantu.
        
        Args:
            bantu_class: Classe Bantu
            
        Returns:
            Descrição em português
            
        Examples:
            >>> desc = BantuClassifierService.get_class_description(BantuClass.M_WA)
            >>> "Pessoas" in desc
            True
        """
        return bantu_class.description
    
    @classmethod
    def get_typical_examples(cls, bantu_class: BantuClass) -> list:
        """
        Retorna exemplos típicos de palavras da classe.
        
        Args:
            bantu_class: Classe Bantu
            
        Returns:
            Lista de exemplos (singular/plural)
            
        Examples:
            >>> examples = BantuClassifierService.get_typical_examples(BantuClass.M_WA)
            >>> ("mtu", "watu") in examples
            True
        """
        examples = {
            BantuClass.M_WA: [
                ("mtu", "watu", "pessoa/pessoas"),
                ("mwalimu", "walimu", "professor/professores"),
                ("mwana", "wana", "criança/crianças"),
            ],
            BantuClass.M_MI: [
                ("mti", "miti", "árvore/árvores"),
                ("mkono", "mikono", "mão/mãos"),
                ("mwaka", "miaka", "ano/anos"),
            ],
            BantuClass.JI_MA: [
                ("jicho", "macho", "olho/olhos"),
                ("tunda", "matunda", "fruta/frutas"),
                ("jina", "majina", "nome/nomes"),
            ],
            BantuClass.KI_VI: [
                ("kiti", "viti", "cadeira/cadeiras"),
                ("kisu", "visu", "faca/facas"),
                ("kitabu", "vitabu", "livro/livros"),
            ],
            BantuClass.N_N: [
                ("nyumba", "nyumba", "casa/casas"),
                ("ndege", "ndege", "pássaro/pássaros"),
                ("ngoma", "ngoma", "tambor/tambores"),
            ],
            BantuClass.U: [
                ("uzuri", "", "beleza"),
                ("utu", "", "humanidade"),
                ("uchungu", "", "amargura"),
            ],
            BantuClass.PA_KU_MU: [
                ("pahali", "", "lugar"),
                ("kule", "", "lá"),
                ("ndani", "", "dentro"),
            ],
        }
        return examples.get(bantu_class, [])
    
    @classmethod
    def validate_class_for_word(cls, word: str, claimed_class: BantuClass) -> bool:
        """
        Valida se uma classe Bantu é consistente com a palavra.
        
        Útil para validar dados de dicionários externos.
        
        Args:
            word: Palavra em Swahili
            claimed_class: Classe alegada
            
        Returns:
            True se consistente, False caso contrário
            
        Examples:
            >>> BantuClassifierService.validate_class_for_word("mtu", BantuClass.M_WA)
            True
            >>> BantuClassifierService.validate_class_for_word("mtu", BantuClass.KI_VI)
            False
        """
        inferred = cls.infer_class(word, WordType.NOUN)
        
        # Se não conseguimos inferir, não podemos validar
        if inferred == BantuClass.UNKNOWN:
            logger.warning(
                f"Cannot validate class for '{word}': inference returned UNKNOWN"
            )
            return True  # Assume válido se não conseguimos inferir
        
        # Compara com a classe alegada
        is_valid = inferred == claimed_class
        
        if not is_valid:
            logger.warning(
                f"Class mismatch for '{word}': "
                f"claimed {claimed_class.value}, inferred {inferred.value}"
            )
        
        return is_valid
    
    @classmethod
    def get_all_classes(cls) -> list:
        """
        Returns lista de todas as classes Bantu disponíveis.
        
        Returns:
            Lista de BantuClass
        """
        return [
            BantuClass.M_WA,
            BantuClass.M_MI,
            BantuClass.JI_MA,
            BantuClass.KI_VI,
            BantuClass.N_N,
            BantuClass.U,
            BantuClass.PA_KU_MU,
        ]


# Example de uso (para testes/documentação)
if __name__ == "__main__":
    print("=== Bantu Classifier Service ===\n")
    
    # Testar classificação
    test_words = [
        ("mtu", WordType.NOUN),
        ("watu", WordType.NOUN),
        ("kiti", WordType.NOUN),
        ("mti", WordType.NOUN),
        ("uzuri", WordType.NOUN),
        ("soma", WordType.VERB),
    ]
    
    print("Classificando palavras:\n")
    for word, wtype in test_words:
        cls = BantuClassifierService.infer_class(word, wtype)
        print(f"{word:15} ({wtype.value:10}) → {cls.value:10} - {cls.description}")
    
    # Mostrar exemplos
    print("\n\nExemplos por classe:\n")
    for bantu_class in BantuClassifierService.get_all_classes():
        examples = BantuClassifierService.get_typical_examples(bantu_class)
        print(f"\n{bantu_class.value} - {bantu_class.description}:")
        for ex in examples[:2]:  # Mostrar 2 exemplos
            if ex[1]:  # Se tem plural
                print(f"  {ex[0]:15} / {ex[1]:15} ({ex[2]})")
            else:
                print(f"  {ex[0]:15} ({ex[2]})")
    
    # Testar validação
    print("\n\nValidação de classes:\n")
    validations = [
        ("mtu", BantuClass.M_WA, True),
        ("mtu", BantuClass.KI_VI, False),
        ("kiti", BantuClass.KI_VI, True),
    ]
    
    for word, cls, expected in validations:
        result = BantuClassifierService.validate_class_for_word(word, cls)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{word}' como {cls.value}: {result}")
