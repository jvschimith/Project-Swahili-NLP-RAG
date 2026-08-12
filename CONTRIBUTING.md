# 🤝 Contribution Guide

Thank you for contributing to the **Swahili NLP RAG** project!

---

## 📋 Table of Contents

- [How to Contribute](#-how-to-contribute)
- [Conventional Commits](#-conventional-commits)
- [Branch Strategy](#-branch-strategy)
- [Environment Setup](#-environment-setup)
- [Running Tests](#-running-tests)
- [Code Style](#-code-style)

---

## 🚀 How to Contribute

### 1. Fork & Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/swahili-nlp-rag.git
cd swahili-nlp-rag
```

### 2. Create a Branch

```bash
# For new features
git checkout -b feature/feature-name

# For bug fixes
git checkout -b fix/bug-description

# For documentation
git checkout -b docs/description
```

### 3. Make Your Changes

- Write code following the [Code Style](#-code-style)
- Add tests when applicable
- Update documentation when needed

### 4. Commit with Conventional Commits

```bash
git add .
git commit -m "feat: add Kamusi dictionary integration"
```

### 5. Push & Pull Request

```bash
git push origin feature/feature-name
# Open a Pull Request on GitHub
```

---

## 📝 Conventional Commits

We use **Conventional Commits** for standardized messages and automatic changelogs.

### Format

```text
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

### Main Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add Bantu root extraction` |
| `fix` | Bug fix | `fix: correct compound-word tokenization` |
| `docs` | Documentation | `docs: update README with usage examples` |
| `refactor` | Code refactor | `refactor: move domain services to the correct layer` |
| `test` | Tests | `test: add tests for BantuClassifier` |
| `chore` | Maintenance | `chore: update dependencies` |
| `perf` | Performance | `perf: optimize entity search query` |
| `style` | Formatting | `style: format code with black` |
| `ci` | CI/CD | `ci: add GitHub Actions workflow` |
| `build` | Build system | `build: update requirements.txt` |

### Full Examples

#### Feature
```text
feat(domain): add SentimentScore Value Object

Implement SentimentScore as an immutable dataclass
with polarity validation in the range [-1.0, 1.0]

Closes #42
```

#### Fix
```text
fix(infrastructure): fix UTF-8 encoding in CSV reading

Add encoding='utf-8' to avoid issues
with Swahili special characters

Fixes #38
```

#### Breaking Change
```text
feat(api)!: change endpoint from /terms to /vocabulary

BREAKING CHANGE: The /terms route has been renamed to /vocabulary.
Update your integrations.
```

---

## 🌳 Branch Strategy

### Main Branches

- **`main`** - Production code (always stable)
- **`develop`** - Development branch (continuous integration)

### Temporary Branches

- **`feature/*`** - New features
  Example: `feature/kamusi-integration`

- **`fix/*`** - Bug fixes
  Example: `fix/sentiment-lexicon-encoding`

- **`hotfix/*`** - Urgent production fixes
  Example: `hotfix/database-connection-leak`

- **`docs/*`** - Documentation
  Example: `docs/api-documentation`

- **`refactor/*`** - Large refactors
  Example: `refactor/ddd-architecture`

- **`test/*`** - Test additions
  Example: `test/unit-tests-domain-layer`

### Workflow

```bash
# 1. Always start from an up-to-date develop branch
git checkout develop
git pull origin develop

# 2. Create a feature branch
git checkout -b feature/my-feature

# 3. Work on the feature
git add .
git commit -m "feat: implement feature X"

# 4. Update from develop before opening the PR
git checkout develop
git pull origin develop
git checkout feature/my-feature
git rebase develop

# 5. Push and create Pull Request
git push origin feature/my-feature
```

### Merge Rules

- ✅ **Feature branches** → merge into `develop`
- ✅ **Develop** → merge into `main` (release)
- ✅ **Hotfix** → merge into both `main` and `develop`

---

## 🛠️ Environment Setup

### 1. Prerequisites

- Python 3.9+
- Git 2.13+ (for Git LFS)
- Git LFS installed

### 2. Install Git LFS

```bash
# Ubuntu/Debian
sudo apt-get install git-lfs

# macOS
brew install git-lfs

# Windows
# Download from: https://git-lfs.github.com/

# Initialize
git lfs install
```

### 3. Project Setup

```bash
# Clone
git clone https://github.com/your-username/swahili-nlp-rag.git
cd swahili-nlp-rag

# Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy example .env
cp .env.example .env

# Initialize database
python -m src.infrastructure.database init
```

---

## ✅ Running Tests

### All Tests

```bash
pytest
```

### Tests with Coverage

```bash
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in a browser
```

### Tests for a Specific Layer

```bash
# Domain layer
pytest tests/domain/

# Application layer
pytest tests/application/

# Infrastructure layer
pytest tests/infrastructure/
```

### Tests for a Single File

```bash
pytest tests/domain/test_value_objects.py
```

---

## 🎨 Code Style

### Python

We follow **PEP 8** with a few customizations:

- **Black** for automatic formatting
- **isort** for import ordering
- **flake8** for linting
- **mypy** for type checking

### Automatic Formatting

```bash
# Black
black src/ tests/

# isort
isort src/ tests/

# Check with flake8
flake8 src/ tests/
```

### Type Hints

✅ **Use type hints whenever possible**:

```python
def extract_root(word: str) -> MorphologicalRoot:
    """Extract the morphological root."""
    pass
```

### Docstrings

✅ **Use Google-style docstrings**:

```python
def infer_class(word: str, word_type: WordType) -> BantuClass:
    """
    Infer the Bantu class of a word.

    Args:
        word: Swahili word
        word_type: Grammatical type

    Returns:
        Inferred Bantu class

    Raises:
        ValueError: If `word` is empty
    """
    pass
```

---

## 📐 DDD Architecture

When contributing, respect the architecture layers:

```text
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

### Dependency Rules

- ❌ **Domain** must NOT depend on Application or Infrastructure
- ✅ **Application** may depend on Domain
- ✅ **Infrastructure** may depend on Domain (through interfaces)

---

## 🐛 Reporting Bugs

Use this issue template:

```markdown
**Bug Description**
Clear description of the problem

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Observe the error

**Expected Behavior**
What should happen

**Current Behavior**
What is happening now

**Environment**
- OS: Ubuntu 22.04
- Python: 3.11
- Project version: v0.2.0
```

---

## 💡 Suggesting Features

Use this feature request template:

```markdown
**Problem to Solve**
What problem does this feature solve?

**Proposed Solution**
Description of the solution

**Alternatives Considered**
Other possible approaches

**Estimated Complexity**
- [ ] Small (1-2 days)
- [ ] Medium (1 week)
- [ ] Large (2+ weeks)
```

---

## 📞 Contact

Questions? Open an **issue** or get in touch:

- 📧 Email: your-email@example.com
- 💬 Discussions: GitHub Discussions

---

**Thank you for contributing!** 🙏
