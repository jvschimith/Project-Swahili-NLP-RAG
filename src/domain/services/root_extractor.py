"""
Domain Service: Extrator de Radicais Morfológicos

Responsibilitys:
- Extrair raiz morfológica de palavras Swahili
- Identificar prefixos e sufixos
- Fornecer decomposição morfológica completa

Este é um Domain Service puro sem dependências de infraestrutura.
"""
from typing import Optional, List, Tuple
from loguru import logger

from ..value_objects import MorphologicalRoot, WordType


class RootExtractorService:
    """
    Domain Service: Extração de radicais morfológicos.
    
    O Swahili, como língua aglutinante, forma palavras através da adição
    de prefixos e sufixos a uma raiz. Este serviço identifica esses componentes.
    
    Estrutura Morfológica Swahili:
        VERBO: (sujeito)-(tempo)-(objeto)-raiz-(derivação)
        Exemplo: ni-na-ku-som-a = eu-presente-te-ler-final
        
        NOME: (prefixo_classe)-raiz-(sufixo)
        Exemplo: ki-tabu = classe_7-livro
    
    Business Rules:
        - Prefixos verbais: ni-, u-, a-, tu-, m-, wa-, ku-, li-, ta-, na-, me-
        - Prefixos nominais: m-, wa-, mi-, ki-, vi-, ma-, u-
        - Sufixos verbais: -a, -e, -i, -o, -u
        - Palavra mínima = raiz de 2+ caracteres
    
    Examples:
        >>> extractor = RootExtractorService()
        >>> root = extractor.extract("ninasoma")
        >>> root.root
        'som'
        >>> root.prefix
        'nina'
    """
    
    # Prefixos verbais comuns (subject markers + tense markers)
    VERBAL_PREFIXES = [
        # Compound prefixes (sujeito + tempo)
        'ninaku', 'ninali', 'ninata', 'ninana', 'ninajua',  # ni-na-ku-, etc
        'unaku', 'unali', 'unata', 'unana',
        'anaku', 'anali', 'anata', 'anana',
        'tunaku', 'tunali', 'tunata', 'tunana',
        'mnaku', 'mnali', 'mnata', 'mnana',
        'wanaku', 'wanali', 'wanata', 'wanana',
        
        # Tense markers alone
        'nina', 'una', 'ana', 'tuna', 'mna', 'wana',  # present (na-)
        'nita', 'uta', 'ata', 'tuta', 'mta', 'wata',  # future (ta-)
        'nili', 'uli', 'ali', 'tuli', 'mli', 'wali',  # past (li-)
        'nime', 'ume', 'ame', 'tume', 'mme', 'wame',  # perfect (me-)
        'niku', 'uku', 'aku', 'tuku', 'mku', 'waku',  # infinitive (ku-)
        'nihu', 'uhu', 'ahu', 'tuhu', 'mhu', 'wahu',  # habitual (hu-)
        'nisi', 'usi', 'asi', 'tusi', 'msi', 'wasi',  # negative (si-)
        
        # Subject markers alone
        'ni', 'u', 'a', 'tu', 'm', 'wa',
        
        # Other common verbal prefixes
        'ku', 'li', 'ta', 'na', 'me', 'ka', 'hu', 'si',
    ]
    
    # Prefixos nominais (noun class prefixes)
    NOMINAL_PREFIXES = [
        'wa', 'mi', 'ma', 'ki', 'vi', 'ku', 'pa', 'mu',
        'mw', 'mtu', 'mti', 'ji', 'ny', 'n', 'u',
    ]
    
    # Todos os prefixos (união)
    ALL_PREFIXES = sorted(
        set(VERBAL_PREFIXES + NOMINAL_PREFIXES),
        key=len,
        reverse=True  # Tenta os mais longos primeiro
    )
    
    # Sufixos verbais comuns
    VERBAL_SUFFIXES = [
        'wa', 'ni', 'ye', 'e', 'a', 'i', 'o', 'u',
        'ka', 'sha', 'po', 'ko', 'mo',
    ]
    
    # Sufixos nominais
    NOMINAL_SUFFIXES = [
        'ni', 'o', 'e', 'i',
    ]
    
    ALL_SUFFIXES = sorted(
        set(VERBAL_SUFFIXES + NOMINAL_SUFFIXES),
        key=len,
        reverse=True
    )
    
    @classmethod
    def extract(
        cls, 
        word: str, 
        word_type: Optional[WordType] = None,
        aggressive: bool = False
    ) -> MorphologicalRoot:
        """
        Extrai a raiz morfológica de uma palavra.
        
        Args:
            word: Palavra em Swahili (normalizada)
            word_type: Tipo gramatical (ajuda na extração)
            aggressive: Se True, remove mais afixos (pode ser impreciso)
            
        Returns:
            MorphologicalRoot com raiz e afixos identificados
            
        Business Rules:
            - Palavra mínima: 2 caracteres
            - Tenta prefixos mais longos primeiro
            - Mantém raiz de pelo menos 2 caracteres
            - Modo conservador: remove apenas prefixos conhecidos
            - Modo agressivo: tenta remover sufixos também
            
        Examples:
            >>> RootExtractorService.extract("ninasoma")
            MorphologicalRoot(root='som', prefix='nina', suffix='a')
            >>> RootExtractorService.extract("mtu")
            MorphologicalRoot(root='tu', prefix='m', suffix=None)
        """
        # Validação inicial
        if not word or len(word) < 2:
            logger.debug(f"Word too short: '{word}'")
            return MorphologicalRoot(root=word if word else "")
        
        # Normalizesr palavra
        original = word.lower().strip()
        prefix_found = None
        suffix_found = None
        root = original
        
        # Escolher lista de prefixos baseada no tipo
        if word_type == WordType.VERB:
            prefixes_to_try = cls.VERBAL_PREFIXES
        elif word_type == WordType.NOUN:
            prefixes_to_try = cls.NOMINAL_PREFIXES
        else:
            prefixes_to_try = cls.ALL_PREFIXES
        
        # 1. Tentar remover prefixos
        for prefix in prefixes_to_try:
            if root.startswith(prefix):
                # Verificar se sobra raiz suficiente
                remaining = root[len(prefix):]
                if len(remaining) >= 2:  # Raiz mínima de 2 caracteres
                    prefix_found = prefix
                    root = remaining
                    logger.debug(f"Removed prefix '{prefix}' from '{original}'")
                    break  # Apenas um prefixo por vez
        
        # 2. Tentar remover sufixos (se modo agressivo ou verbo)
        if aggressive or word_type == WordType.VERB:
            # Escolher sufixos apropriados
            if word_type == WordType.VERB:
                suffixes_to_try = cls.VERBAL_SUFFIXES
            else:
                suffixes_to_try = cls.ALL_SUFFIXES
            
            for suffix in suffixes_to_try:
                if root.endswith(suffix):
                    # Verificar se sobra raiz suficiente
                    remaining = root[:-len(suffix)]
                    if len(remaining) >= 2:  # Raiz mínima de 2 caracteres
                        suffix_found = suffix
                        root = remaining
                        logger.debug(f"Removed suffix '{suffix}' from '{original}'")
                        break  # Apenas um sufixo por vez
        
        # 3. Criar e retornar MorphologicalRoot
        result = MorphologicalRoot(
            root=root,
            prefix=prefix_found,
            suffix=suffix_found
        )
        
        logger.debug(f"Extracted: '{original}' → {result}")
        return result
    
    @classmethod
    def extract_verb_components(cls, verb: str) -> dict:
        """
        Extrai componentes específicos de verbos Swahili.
        
        Verbos Swahili têm estrutura:
        (sujeito)-(tempo)-(objeto)-raiz-(final)
        
        Args:
            verb: Verbo conjugado em Swahili
            
        Returns:
            Dicionário com componentes identificados
            
        Examples:
            >>> RootExtractorService.extract_verb_components("ninakupenda")
            {'subject': 'ni', 'tense': 'na', 'object': 'ku', 'root': 'pend', 'final': 'a'}
        """
        original = verb.lower().strip()
        components = {
            'subject': None,
            'tense': None,
            'object': None,
            'root': None,
            'final': None,
            'full_prefix': None
        }
        
        # Subject markers (1 ou 2 chars)
        subject_markers = {
            'ni': '1sg', 'u': '2sg', 'a': '3sg',
            'tu': '1pl', 'm': '2pl', 'wa': '3pl'
        }
        
        # Tense markers
        tense_markers = {
            'na': 'present', 'li': 'past', 'ta': 'future',
            'me': 'perfect', 'ku': 'infinitive', 'si': 'negative'
        }
        
        # Object markers
        object_markers = ['ni', 'ku', 'mu', 'tu', 'wa', 'm', 'ki', 'vi']
        
        remaining = original
        full_prefix = ""
        
        # 1. Tentar identificar sujeito
        for marker, person in subject_markers.items():
            if remaining.startswith(marker):
                components['subject'] = marker
                full_prefix += marker
                remaining = remaining[len(marker):]
                break
        
        # 2. Tentar identificar tempo
        for marker, tense in tense_markers.items():
            if remaining.startswith(marker):
                components['tense'] = marker
                full_prefix += marker
                remaining = remaining[len(marker):]
                break
        
        # 3. Tentar identificar objeto
        for marker in object_markers:
            if remaining.startswith(marker) and len(remaining) > len(marker) + 2:
                components['object'] = marker
                full_prefix += marker
                remaining = remaining[len(marker):]
                break
        
        # 4. Sufixo verbal final (geralmente -a, -e, -i)
        if remaining and remaining[-1] in 'aeiou':
            components['final'] = remaining[-1]
            remaining = remaining[:-1]
        
        # 5. O que sobrou é a raiz
        components['root'] = remaining if remaining else None
        components['full_prefix'] = full_prefix if full_prefix else None
        
        return components
    
    @classmethod
    def is_likely_compound(cls, word: str) -> bool:
        """
        Verifica se uma palavra é provavelmente composta.
        
        Args:
            word: Palavra a verificar
            
        Returns:
            True se provavelmente é palavra composta
            
        Examples:
            >>> RootExtractorService.is_likely_compound("ninakupenda")
            True
            >>> RootExtractorService.is_likely_compound("mtu")
            False
        """
        # Heurística: palavra longa com múltiplos prefixos conhecidos
        root = cls.extract(word, aggressive=False)
        
        # Se tem prefixo E sufixo, provavelmente é composta
        if root.has_prefix and root.has_suffix:
            return True
        
        # Se o prefixo é longo (>3 chars), provavelmente é composto
        if root.prefix and len(root.prefix) > 3:
            return True
        
        return False


# Example de uso (para testes/documentação)
if __name__ == "__main__":
    print("=== Root Extractor Service ===\n")
    
    # Testar extração de radicais
    test_words = [
        ("mtu", WordType.NOUN),
        ("watu", WordType.NOUN),
        ("kitabu", WordType.NOUN),
        ("ninasoma", WordType.VERB),
        ("anakupenda", WordType.VERB),
        ("tumemaliza", WordType.VERB),
        ("uzuri", WordType.NOUN),
    ]
    
    print("Extraindo radicais:\n")
    for word, wtype in test_words:
        root = RootExtractorService.extract(word, wtype)
        print(f"{word:15} → {root}")
    
    # Testar extração de componentes verbais
    print("\n\nComponentes verbais:\n")
    verbs = ["ninasoma", "anakupenda", "tumemaliza", "wataenda"]
    
    for verb in verbs:
        components = RootExtractorService.extract_verb_components(verb)
        print(f"\n{verb}:")
        for key, value in components.items():
            if value:
                print(f"  {key:12}: {value}")
    
    # Testar detecção de compostos
    print("\n\nPalavras compostas:\n")
    words = ["ninakupenda", "mtu", "tumemaliza", "uzuri"]
    
    for word in words:
        is_compound = RootExtractorService.is_likely_compound(word)
        status = "✓ Composta" if is_compound else "✗ Simples"
        print(f"{status:15} - {word}")
