"""
Domain Layer - Repository Interfaces

Repositories são abstrações que encapsulam a lógica de acesso a dados.
São interfaces (contratos) definidas no domínio, mas implementadas na
camada de infraestrutura.

Seguem o Repository Pattern:
- Interface no Domain Layer (este arquivo)
- Implementação no Infrastructure Layer
- Permite trocar implementação sem afetar domínio

Benefícios:
- Testabilidade (mock fácil)
- Inversão de dependência (DIP)
- Separação de concerns
- Flexibilidade de implementação
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .entities import (
    SwahiliTerm,
    DictionaryEntry,
    VerbConjugation,
    POSRecord,
    NewsArticle
)
from .value_objects import BantuClass, WordType, Etymology


class ITermRepository(ABC):
    """
    Interface: Repository de termos Swahili.
    
    Responsibility: Manage persistence de termos do vocabulário.
    
    Design Decisions:
        - Search por termo (string) é o caso de uso mais comum
        - Exists() evita queries desnecessárias
        - Update de frequência é operação frequente (otimizar)
    """
    
    @abstractmethod
    def save(self, term: SwahiliTerm) -> int:
        """
        Persists um termo no repositório.
        
        Args:
            term: Entity SwahiliTerm a persistir
            
        Returns:
            ID do termo salvo
            
        Raises:
            ValueError: Se termo já existe (constraint de unicidade)
        """
        pass
    
    @abstractmethod
    def find_by_id(self, term_id: int) -> Optional[SwahiliTerm]:
        """
        Search termo por ID.
        
        Args:
            term_id: Identificador único do termo
            
        Returns:
            SwahiliTerm se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def find_by_term(self, term: str) -> Optional[SwahiliTerm]:
        """
        Search termo pela string (case-insensitive).
        
        Args:
            term: Palavra em Swahili
            
        Returns:
            SwahiliTerm se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def exists(self, term: str) -> bool:
        """
        Checks if termo existe sem carregar o objeto.
        
        Args:
            term: Palavra em Swahili
            
        Returns:
            True se existe, False caso contrário
        """
        pass
    
    @abstractmethod
    def find_by_bantu_class(self, bantu_class: BantuClass, limit: int = 100) -> List[SwahiliTerm]:
        """
        Search termos por classe Bantu.
        
        Args:
            bantu_class: Classe nominal Bantu
            limit: Número máximo de resultados
            
        Returns:
            Lista de termos da classe especificada
        """
        pass
    
    @abstractmethod
    def find_by_etymology(self, etymology: Etymology, limit: int = 100) -> List[SwahiliTerm]:
        """
        Search termos por origem etimológica.
        
        Args:
            etymology: Origem da palavra
            limit: Número máximo de resultados
            
        Returns:
            Lista de termos da origem especificada
        """
        pass
    
    @abstractmethod
    def find_stopwords(self) -> List[SwahiliTerm]:
        """
        Returns todos os termos marcados como stopwords.
        
        Returns:
            Lista de stopwords
        """
        pass
    
    @abstractmethod
    def update_frequency(self, term_id: int, increment: float) -> None:
        """
        Updates frequência de uso de um termo.
        
        Otimização: Esta operação deve ser eficiente pois é chamada
        frequentemente durante processamento de corpora.
        
        Args:
            term_id: ID do termo
            increment: Valor a incrementar
        """
        pass
    
    @abstractmethod
    def get_most_frequent(self, limit: int = 100, exclude_stopwords: bool = True) -> List[SwahiliTerm]:
        """
        Returns termos mais frequentes.
        
        Args:
            limit: Número máximo de termos
            exclude_stopwords: Se True, exclui stopwords
            
        Returns:
            Lista ordenada por frequência (decrescente)
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Returns contagem total de termos.
        
        Returns:
            Número de termos no repositório
        """
        pass


class IDictionaryRepository(ABC):
    """
    Interface: Repository de entradas de dicionário.
    
    Responsibility: Manage persistence de definições do Kamusi.
    """
    
    @abstractmethod
    def save(self, entry: DictionaryEntry, term_id: int) -> int:
        """
        Persists entrada de dicionário.
        
        Args:
            entry: Entrada completa do dicionário
            term_id: ID do termo associado
            
        Returns:
            ID da entrada salva
        """
        pass
    
    @abstractmethod
    def find_by_term_id(self, term_id: int) -> Optional[DictionaryEntry]:
        """
        Search entrada de dicionário por ID do termo.
        
        Args:
            term_id: ID do termo
            
        Returns:
            DictionaryEntry se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def find_by_term_string(self, term: str) -> Optional[DictionaryEntry]:
        """
        Search entrada por palavra (convenience method).
        
        Args:
            term: Palavra em Swahili
            
        Returns:
            DictionaryEntry se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def find_synonyms(self, term_id: int) -> List[str]:
        """
        Returns sinônimos de um termo.
        
        Args:
            term_id: ID do termo
            
        Returns:
            Lista de sinônimos
        """
        pass
    
    @abstractmethod
    def search_by_meaning(self, query: str, limit: int = 50) -> List[DictionaryEntry]:
        """
        Search entries por semelhança no significado.
        
        Args:
            query: Texto a buscar no significado
            limit: Número máximo de resultados
            
        Returns:
            Lista de entries que contêm a query
        """
        pass


class IConjugationRepository(ABC):
    """
    Interface: Repository de conjugações verbais.
    
    Responsibility: Gerenciar conjugações de verbos Swahili.
    """
    
    @abstractmethod
    def save(self, conjugation: VerbConjugation, verb_id: int) -> int:
        """
        Persists conjugação verbal.
        
        Args:
            conjugation: Forma conjugada
            verb_id: ID do verbo (termo)
            
        Returns:
            ID da conjugação salva
        """
        pass
    
    @abstractmethod
    def find_by_verb(self, verb_id: int) -> List[VerbConjugation]:
        """
        Returns todas as conjugações de um verbo.
        
        Args:
            verb_id: ID do verbo
            
        Returns:
            Lista de conjugações
        """
        pass
    
    @abstractmethod
    def find_by_tense(self, verb_id: int, tense: str) -> List[VerbConjugation]:
        """
        Search conjugações por tempo verbal.
        
        Args:
            verb_id: ID do verbo
            tense: Tempo verbal (present, past, etc)
            
        Returns:
            Lista de conjugações no tempo especificado
        """
        pass
    
    @abstractmethod
    def find_by_person(self, verb_id: int, person: str) -> List[VerbConjugation]:
        """
        Search conjugações por pessoa gramatical.
        
        Args:
            verb_id: ID do verbo
            person: Pessoa (1sg, 2sg, etc)
            
        Returns:
            Lista de conjugações na pessoa especificada
        """
        pass


class IPOSRepository(ABC):
    """
    Interface: Repository de anotações POS (Part-of-Speech).
    
    Responsibility: Gerenciar dados do Masakhane-POS.
    """
    
    @abstractmethod
    def save(self, pos_record: POSRecord, term_id: int) -> int:
        """
        Persists registro POS.
        
        Args:
            pos_record: Anotação gramatical
            term_id: ID do termo anotado
            
        Returns:
            ID do registro salvo
        """
        pass
    
    @abstractmethod
    def find_by_sentence(self, sentence_id: int) -> List[POSRecord]:
        """
        Returns todos os registros de uma sentença.
        
        Args:
            sentence_id: ID da sentença
            
        Returns:
            Lista de registros ordenados por word_order
        """
        pass
    
    @abstractmethod
    def find_by_tag(self, tag: str, limit: int = 100) -> List[POSRecord]:
        """
        Search registros por tag gramatical.
        
        Args:
            tag: Tag gramatical (NOUN, VERB, etc)
            limit: Número máximo de resultados
            
        Returns:
            Lista de registros com a tag especificada
        """
        pass
    
    @abstractmethod
    def count_by_tag(self) -> dict:
        """
        Returns contagem de registros por tag.
        
        Returns:
            Dicionário {tag: count}
        """
        pass


class INewsRepository(ABC):
    """
    Interface: Repository de artigos de notícias.
    
    Responsibility: Gerenciar corpus de notícias (Masakhane-News).
    """
    
    @abstractmethod
    def save(self, article: NewsArticle) -> int:
        """
        Persists artigo de notícias.
        
        Args:
            article: Artigo completo
            
        Returns:
            ID do artigo salvo
        """
        pass
    
    @abstractmethod
    def find_by_id(self, article_id: int) -> Optional[NewsArticle]:
        """
        Search artigo por ID.
        
        Args:
            article_id: ID do artigo
            
        Returns:
            NewsArticle se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def find_all(self, limit: int = 100, offset: int = 0) -> List[NewsArticle]:
        """
        Returns todos os artigos (paginado).
        
        Args:
            limit: Número máximo de artigos
            offset: Deslocamento para paginação
            
        Returns:
            Lista de artigos
        """
        pass
    
    @abstractmethod
    def find_by_category(self, category: str, limit: int = 100) -> List[NewsArticle]:
        """
        Search artigos por categoria.
        
        Args:
            category: Categoria (Kitaifa, Kimataifa, etc)
            limit: Número máximo de resultados
            
        Returns:
            Lista de artigos da categoria
        """
        pass
    
    @abstractmethod
    def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 100
    ) -> List[NewsArticle]:
        """
        Search artigos em intervalo de datas.
        
        Args:
            start_date: Data inicial (inclusive)
            end_date: Data final (inclusive)
            limit: Número máximo de resultados
            
        Returns:
            Lista de artigos no período
        """
        pass
    
    @abstractmethod
    def find_with_sentiment(
        self,
        sentiment_label: str,
        limit: int = 100
    ) -> List[NewsArticle]:
        """
        Search artigos por sentimento.
        
        Args:
            sentiment_label: Label de sentimento (positive, negative, neutral)
            limit: Número máximo de resultados
            
        Returns:
            Lista de artigos com o sentimento especificado
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Returns contagem total de artigos.
        
        Returns:
            Número de artigos no repositório
        """
        pass
    
    @abstractmethod
    def count_by_category(self) -> dict:
        """
        Returns contagem de artigos por categoria.
        
        Returns:
            Dicionário {category: count}
        """
        pass


# Type hints para facilitar uso
TermRepo = ITermRepository
DictRepo = IDictionaryRepository
ConjugRepo = IConjugationRepository
POSRepo = IPOSRepository
NewsRepo = INewsRepository


# Example de uso em testes/documentação
if __name__ == "__main__":
    print("Repository Interfaces - Domain Layer")
    print("\nInterfaces disponíveis:")
    print("- ITermRepository: Gerencia termos Swahili")
    print("- IDictionaryRepository: Gerencia entradas de dicionário")
    print("- IConjugationRepository: Gerencia conjugações verbais")
    print("- IPOSRepository: Gerencia anotações POS")
    print("- INewsRepository: Gerencia corpus de notícias")
    print("\nEstas interfaces são implementadas na Infrastructure Layer.")
