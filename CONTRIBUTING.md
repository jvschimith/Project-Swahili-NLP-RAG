# 🤝 Contribution Guide

Obrigado por contribuir com o projeto **Swahili NLP RAG**!

---

## 📋 Índice

- [How to Contribute](#como-contribuir)
- [Conventional Commits](#conventional-commits)
- [Branch Strategy](#estratégia-de-branches)
- [Configurando Ambiente](#configurando-ambiente)
- [Rodando Testes](#rodando-testes)
- [Code Style](#code-style)

---

## 🚀 How to Contribute

### 1. Fork & Clone

```bash
# Fork o repositório no GitHub
# Depois clone seu fork
git clone https://github.com/SEU-USUARIO/swahili-nlp-rag.git
cd swahili-nlp-rag
```

### 2. Crie uma Branch

```bash
# Para novas features
git checkout -b feature/nome-da-feature

# Para correções de bug
git checkout -b fix/descricao-do-bug

# Para documentação
git checkout -b docs/descricao
```

### 3. Faça suas Mudanças

- Escreva código seguindo o [Code Style](#code-style)
- Adicione testes se aplicável
- Atualize documentação se necessário

### 4. Commit com Conventional Commits

```bash
git add .
git commit -m "feat: adiciona integração com Kamusi dictionary"
```

### 5. Push & Pull Request

```bash
git push origin feature/nome-da-feature
# Abra um Pull Request no GitHub
```

---

## 📝 Conventional Commits

Usamos **Conventional Commits** para mensagens padronizadas e changelogs automáticos.

### Formato

```
<tipo>(<escopo>): <descrição curta>

[corpo opcional]

[rodapé opcional]
```

### Tipos Principais

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| `feat` | Nova funcionalidade | `feat: adiciona extração de radicais Bantu` |
| `fix` | Correção de bug | `fix: corrige tokenização em palavras compostas` |
| `docs` | Documentação | `docs: atualiza README com exemplos de uso` |
| `refactor` | Refatoração de código | `refactor: move domain services para camada correta` |
| `test` | Testes | `test: adiciona testes para BantuClassifier` |
| `chore` | Manutenção | `chore: atualiza dependências` |
| `perf` | Performance | `perf: otimiza query de busca de entidades` |
| `style` | Formatação | `style: formata código com black` |
| `ci` | CI/CD | `ci: adiciona GitHub Actions workflow` |
| `build` | Build system | `build: atualiza requirements.txt` |

### Exemplos Completos

#### Feature
```
feat(domain): adiciona Value Object SentimentScore

Implementa SentimentScore como dataclass imutável
com validação de polaridade [-1.0, 1.0]

Closes #42
```

#### Fix
```
fix(infrastructure): corrige encoding UTF-8 na leitura de CSV

Adiciona parâmetro encoding='utf-8' para evitar erros
com caracteres especiais do Swahili

Fixes #38
```

#### Breaking Change
```
feat(api)!: muda endpoint de /terms para /vocabulary

BREAKING CHANGE: A rota /terms foi renomeada para /vocabulary.
Atualize suas integrações.
```

---

## 🌳 Branch Strategy

### Branches Principais

- **`main`** - Código em produção (sempre estável)
- **`develop`** - Branch de desenvolvimento (integração contínua)

### Branches Temporárias

- **`feature/*`** - Novas funcionalidades
  - Exemplo: `feature/kamusi-integration`
  
- **`fix/*`** - Correções de bugs
  - Exemplo: `fix/sentiment-lexicon-encoding`
  
- **`hotfix/*`** - Correções urgentes em produção
  - Exemplo: `hotfix/database-connection-leak`
  
- **`docs/*`** - Documentação
  - Exemplo: `docs/api-documentation`
  
- **`refactor/*`** - Refatorações grandes
  - Exemplo: `refactor/ddd-architecture`

- **`test/*`** - Adição de testes
  - Exemplo: `test/unit-tests-domain-layer`

### Workflow

```bash
# 1. Sempre começar do develop atualizado
git checkout develop
git pull origin develop

# 2. Criar branch da feature
git checkout -b feature/minha-feature

# 3. Trabalhar na feature
git add .
git commit -m "feat: implementa feature X"

# 4. Atualizar com develop antes do PR
git checkout develop
git pull origin develop
git checkout feature/minha-feature
git rebase develop

# 5. Push e criar Pull Request
git push origin feature/minha-feature
```

### Regras de Merge

- ✅ **Feature branches** → merge para `develop`
- ✅ **Develop** → merge para `main` (release)
- ✅ **Hotfix** → merge para `main` E `develop`

---

## 🛠️ Configurando Ambiente

### 1. Pré-requisitos

- Python 3.9+
- Git 2.13+ (para Git LFS)
- Git LFS instalado

### 2. Instalar Git LFS

```bash
# Ubuntu/Debian
sudo apt-get install git-lfs

# macOS
brew install git-lfs

# Windows
# Download de: https://git-lfs.github.com/

# Inicializar
git lfs install
```

### 3. Setup do Projeto

```bash
# Clone
git clone https://github.com/seu-usuario/swahili-nlp-rag.git
cd swahili-nlp-rag

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Copiar .env de exemplo
cp .env.example .env

# Inicializar banco de dados
python -m src.infrastructure.database init
```

---

## ✅ Rodando Testes

### Todos os Testes

```bash
pytest
```

### Testes com Coverage

```bash
pytest --cov=src --cov-report=html
# Abrir htmlcov/index.html no navegador
```

### Testes de uma Camada Específica

```bash
# Domain layer
pytest tests/domain/

# Application layer
pytest tests/application/

# Infrastructure layer
pytest tests/infrastructure/
```

### Testes de um Arquivo

```bash
pytest tests/domain/test_value_objects.py
```

---

## 🎨 Code Style

### Python

Seguimos **PEP 8** com algumas customizações:

- **Black** para formatação automática
- **isort** para ordenar imports
- **flake8** para linting
- **mypy** para type checking

### Formatação Automática

```bash
# Black
black src/ tests/

# isort
isort src/ tests/

# Verificar com flake8
flake8 src/ tests/
```

### Type Hints

✅ **Use type hints sempre que possível**:

```python
def extract_root(word: str) -> MorphologicalRoot:
    """Extrai raiz morfológica."""
    pass
```

### Docstrings

✅ **Use docstrings no estilo Google**:

```python
def infer_class(word: str, word_type: WordType) -> BantuClass:
    """
    Infere classe Bantu de uma palavra.
    
    Args:
        word: Palavra em Swahili
        word_type: Tipo gramatical
        
    Returns:
        Classe Bantu inferida
        
    Raises:
        ValueError: Se word for vazio
    """
    pass
```

---

## 📐 Arquitetura DDD

Ao contribuir, respeite as camadas da arquitetura:

```
Domain Layer (src/domain/)
├── Entities & Value Objects
├── Domain Services
└── Repository Interfaces

Application Layer (src/application/)
├── Use Cases
└── Application Services

Infrastructure Layer (src/infrastructure/)
├── Database (ORM)
├── Repositories (Implementations)
└── External Services
```

### Regras de Dependência

- ❌ **Domain** NÃO pode depender de Application ou Infrastructure
- ✅ **Application** pode depender de Domain
- ✅ **Infrastructure** pode depender de Domain (via interfaces)

---

## 🐛 Reportando Bugs

Use o template de issue:

```markdown
**Descrição do Bug**
Descrição clara do problema

**Passos para Reproduzir**
1. Passo 1
2. Passo 2
3. Ver erro

**Comportamento Esperado**
O que deveria acontecer

**Comportamento Atual**
O que está acontecendo

**Ambiente**
- OS: Ubuntu 22.04
- Python: 3.11
- Versão do projeto: v0.2.0
```

---

## 💡 Sugerindo Features

Use o template de feature request:

```markdown
**Problema a Resolver**
Qual problema esta feature resolve?

**Solução Proposta**
Descrição da solução

**Alternativas Consideradas**
Outras abordagens possíveis

**Complexidade Estimada**
- [ ] Pequena (1-2 dias)
- [ ] Média (1 semana)
- [ ] Grande (2+ semanas)
```

---

## 📞 Contato

Dúvidas? Abra uma **issue** ou entre em contato:

- 📧 Email: seu-email@example.com
- 💬 Discussions: GitHub Discussions

---

**Obrigado por contribuir!** 🙏
