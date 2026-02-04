# 🚀 PLANO DE MELHORIAS - Projeto Swahili NLP RAG

## 📋 Contexto
Projeto de análise linguística de Swahili com:
- **Fontes atuais**: Masakhane (POS, NER, News)
- **Nova fonte**: Kamusi Dictionary (16.600+ palavras com significados, sinônimos, conjugações)
- **Arquitetura**: Clean Architecture (Domain → Application → Infrastructure)

---

## 🎯 OBJETIVOS PRINCIPAIS

### 1. **Integração do Kamusi Dictionary**
- Adicionar vocabulário rico (16.600+ palavras)
- Enriquecer metadados linguísticos (sinônimos, conjugações)
- Melhorar cobertura do vocabulário central

### 2. **Correção de Pontos Fracos Identificados**
- ❌ `session.query(DBNews).delete()` - risco de perda de dados
- ❌ Tokenização simples (`.split()`)
- ❌ Paths hardcoded
- ❌ Lexicon de sentimento estático
- ❌ Falta de testes unitários

### 3. **Novas Funcionalidades**
- Sistema de versionamento de dados
- API REST para consultas
- Processamento mais robusto de texto
- Expandir análise linguística Bantu

---

## 📦 PASSO 1: PREPARAÇÃO DA INFRAESTRUTURA

### 1.1 Criação de Novos Modelos de Banco de Dados

**Objetivo**: Adicionar tabelas para o dicionário Kamusi

**Modelos necessários**:

```python
class DBDictionary(Base):
    """
    Tabela principal do dicionário Kamusi
    """
    __tablename__ = 'dictionary'
    
    id = Column(Integer, primary_key=True)
    term_id = Column(Integer, ForeignKey('terms.id'), unique=True)
    meaning = Column(String, nullable=False)  # Definição em Swahili
    english_translation = Column(String)
    synonyms = Column(String)  # JSON array de sinônimos
    conjugations = Column(String)  # JSON array de conjugações
    usage_examples = Column(String)  # JSON array de exemplos
    word_type = Column(String)  # noun, verb, adjective, etc.
    etymology = Column(String)  # Origem (Bantu, Arabic, etc.)
    frequency_score = Column(Float, default=0.0)  # Para ranking

class DBSynonym(Base):
    """
    Tabela de relacionamento para sinônimos (muitos-para-muitos)
    """
    __tablename__ = 'synonyms'
    
    id = Column(Integer, primary_key=True)
    term_id = Column(Integer, ForeignKey('terms.id'))
    synonym_term_id = Column(Integer, ForeignKey('terms.id'))
    confidence = Column(Float, default=1.0)

class DBConjugation(Base):
    """
    Tabela de conjugações verbais
    """
    __tablename__ = 'conjugations'
    
    id = Column(Integer, primary_key=True)
    verb_id = Column(Integer, ForeignKey('terms.id'))
    tense = Column(String)  # present, past, future, etc.
    person = Column(String)  # 1sg, 2sg, 3sg, 1pl, 2pl, 3pl
    form = Column(String, nullable=False)  # e.g., "ninasoma"
    prefix_chain = Column(String)  # e.g., "ni-na-"
```

**Alterações no DBTerm existente**:

```python
class DBTerm(Base):
    # ... campos existentes ...
    
    # NOVOS CAMPOS
    etymology = Column(String)  # "bantu", "arabic", "english"
    word_type = Column(String)  # "noun", "verb", "adjective"
    frequency_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

---

### 1.2 Sistema de Configuração (Config Management)

**Objetivo**: Eliminar hardcoded paths e centralizar configurações

**Arquivo**: `src/infrastructure/config.py`

```python
import os
from pathlib import Path
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """
    Configurações centralizadas do projeto
    """
    # Diretórios base
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = PROJECT_ROOT / "data"
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    EMBEDDINGS_DIR: Path = DATA_DIR / "embeddings"
    
    # Banco de dados
    DB_PATH: str = Field(
        default="sqlite:///data/swahili_knowledge.db",
        env="DATABASE_URL"
    )
    
    # Arquivos de dados
    MASAKHANE_POS: Path = RAW_DIR / "pos_swa_test.txt"
    MASAKHANE_NER: Path = RAW_DIR / "ner_swa_test.txt"
    MASAKHANE_NEWS: Path = RAW_DIR / "news_swa_test.tsv"
    KAMUSI_CSV: Path = RAW_DIR / "kamusi" / "words.csv"
    KAMUSI_JSON: Path = RAW_DIR / "kamusi" / "words.json"
    
    # Configurações de processamento
    BATCH_SIZE: int = 1000
    MIN_WORD_LENGTH: int = 2
    MAX_WORD_LENGTH: int = 50
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = DATA_DIR / "logs" / "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton instance
settings = Settings()

# Garantir que diretórios existam
for dir_path in [settings.DATA_DIR, settings.RAW_DIR, 
                 settings.PROCESSED_DIR, settings.EMBEDDINGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
```

**Arquivo `.env`** (criar na raiz):

```env
# Database
DATABASE_URL=sqlite:///data/swahili_knowledge.db

# Logging
LOG_LEVEL=INFO

# Processing
BATCH_SIZE=1000
```

---

### 1.3 Sistema de Logging Melhorado

**Objetivo**: Logging estruturado e rotacionado

**Arquivo**: `src/infrastructure/logging_config.py`

```python
from loguru import logger
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: Path = None):
    """
    Configura logging centralizado com Loguru
    """
    # Remove handlers padrão
    logger.remove()
    
    # Console output com cores
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True
    )
    
    # File output com rotação
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
            rotation="10 MB",  # Rotaciona quando atinge 10MB
            retention="1 week",  # Mantém logs por 1 semana
            compression="zip"  # Comprime logs antigos
        )
    
    return logger
```

---

### 1.4 Utilitários de Processamento de Texto

**Objetivo**: Tokenização e normalização robustas

**Arquivo**: `src/application/text_processing.py`

```python
import re
from typing import List, Set
from loguru import logger

class SwahiliTextProcessor:
    """
    Processador de texto especializado para Swahili
    """
    
    # Stopwords comuns em Swahili
    STOPWORDS: Set[str] = {
        'na', 'ya', 'wa', 'ni', 'si', 'la', 'kwa', 'za', 'katika',
        'hii', 'hizo', 'hilo', 'hiyo', 'ile', 'wale', 'yule',
        'au', 'lakini', 'kama', 'kwamba', 'pale'
    }
    
    # Pontuação para remover
    PUNCTUATION = r'[.,!?;:()\[\]{}"\'«»—…]'
    
    @staticmethod
    def normalize(text: str) -> str:
        """
        Normaliza texto: lowercase, remove espaços extras
        """
        if not text:
            return ""
        
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)  # Remove espaços múltiplos
        return text
    
    @staticmethod
    def tokenize(text: str, remove_punct: bool = True) -> List[str]:
        """
        Tokenização inteligente para Swahili
        
        Args:
            text: Texto a tokenizar
            remove_punct: Se True, remove pontuação
            
        Returns:
            Lista de tokens
        """
        if not text:
            return []
        
        # Normaliza primeiro
        text = SwahiliTextProcessor.normalize(text)
        
        # Remove pontuação se solicitado
        if remove_punct:
            text = re.sub(SwahiliTextProcessor.PUNCTUATION, ' ', text)
        
        # Split por espaços, mas mantém hífens em palavras compostas
        tokens = text.split()
        
        # Filtra tokens vazios
        tokens = [t for t in tokens if t]
        
        return tokens
    
    @staticmethod
    def remove_stopwords(tokens: List[str]) -> List[str]:
        """
        Remove stopwords de uma lista de tokens
        """
        return [t for t in tokens if t not in SwahiliTextProcessor.STOPWORDS]
    
    @staticmethod
    def extract_ngrams(tokens: List[str], n: int = 2) -> List[str]:
        """
        Extrai n-gramas de uma lista de tokens
        
        Args:
            tokens: Lista de tokens
            n: Tamanho do n-grama (default: 2 = bigramas)
            
        Returns:
            Lista de n-gramas como strings
        """
        if len(tokens) < n:
            return []
        
        ngrams = []
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i+n])
            ngrams.append(ngram)
        
        return ngrams
    
    @staticmethod
    def clean_for_db(text: str, max_length: int = 500) -> str:
        """
        Limpa texto para inserção no banco de dados
        """
        text = SwahiliTextProcessor.normalize(text)
        
        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Trunca se necessário
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
```

---

## 📝 RESUMO DO PASSO 1

✅ **O que será criado**:

1. **Novos modelos de banco** (`DBDictionary`, `DBSynonym`, `DBConjugation`)
2. **Sistema de configuração** (`config.py` + `.env`)
3. **Logging melhorado** (`logging_config.py`)
4. **Processamento de texto robusto** (`text_processing.py`)

✅ **Benefícios**:

- ✨ Código mais organizado e manutenível
- 🔒 Configurações centralizadas e seguras
- 📊 Logs estruturados e rotacionados
- 🧹 Tokenização profissional

✅ **Próximos passos após PASSO 1**:

- **PASSO 2**: Script de ingestão do Kamusi (`04_ingest_kamusi.py`)
- **PASSO 3**: Refatoração dos scripts existentes para usar config
- **PASSO 4**: Sistema de versionamento de dados
- **PASSO 5**: Testes unitários

---

## 🚦 STATUS

- [ ] PASSO 1.1 - Novos modelos de banco
- [ ] PASSO 1.2 - Sistema de configuração
- [ ] PASSO 1.3 - Logging melhorado
- [ ] PASSO 1.4 - Processamento de texto
