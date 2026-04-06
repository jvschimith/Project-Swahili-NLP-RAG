# Unit Tests

Comprehensive test suite for the Swahili NLP RAG project.

## Test Structure

```
tests/
├── domain/                # Domain layer tests
│   ├── test_value_objects.py   # Value object tests
│   └── test_services.py        # Domain service tests
├── application/           # Application layer tests
│   └── test_text_processor.py  # Text processing tests
└── infrastructure/        # Infrastructure tests (future)
```

## Running Tests

### Run All Tests

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage
pytest --cov=src --cov-report=html
```

### Run Specific Test File

```bash
# Domain tests
pytest tests/domain/test_value_objects.py
pytest tests/domain/test_services.py

# Application tests
pytest tests/application/test_text_processor.py
```

### Run Specific Test Class

```bash
pytest tests/domain/test_value_objects.py::TestSentimentScore
```

### Run Specific Test Method

```bash
pytest tests/domain/test_value_objects.py::TestSentimentScore::test_valid_sentiment_score
```

## Test Coverage

Generate coverage report:

```bash
# Generate HTML report
pytest --cov=src --cov-report=html

# Open report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Test Categories

### Domain Layer Tests (52 tests)

**Value Objects** (35 tests):
- BantuClass enum (5 tests)
- Etymology enum (5 tests)
- WordType enum (3 tests)
- SentimentScore (10 tests)
- MorphologicalRoot (8 tests)
- EntityType (4 tests)

**Domain Services** (17 tests):
- BantuClassifierService (10 tests)
- RootExtractorService (7 tests)

### Application Layer Tests (28 tests)

**Text Processor**:
- Normalization (5 tests)
- Tokenization (5 tests)
- Stopword removal (3 tests)
- N-gram extraction (4 tests)
- Text cleaning (3 tests)
- Sentence extraction (3 tests)
- Word counting (3 tests)
- Word frequency (3 tests)

**Total: 80+ tests**

## Test Markers

Tests can be marked for selective running:

```python
@pytest.mark.unit  # Fast, isolated tests
@pytest.mark.integration  # Tests with dependencies
@pytest.mark.slow  # Slow-running tests
```

Run tests by marker:

```bash
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## Writing New Tests

### Test File Naming

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

### Example Test

```python
import pytest
from src.domain.entities import SwahiliTerm

class TestSwahiliTerm:
    """Tests for SwahiliTerm entity."""
    
    def test_create_term(self):
        """Test creating a term."""
        term = SwahiliTerm(term="mtu")
        assert term.term == "mtu"
    
    def test_invalid_term_raises_error(self):
        """Test invalid term raises error."""
        with pytest.raises(ValueError):
            SwahiliTerm(term="")
```

## Fixtures

Create reusable test data with fixtures:

```python
@pytest.fixture
def sample_term():
    """Create a sample term for testing."""
    return SwahiliTerm(
        term="mtu",
        noun_class=BantuClass.M_WA,
        word_type=WordType.NOUN
    )

def test_with_fixture(sample_term):
    """Test using fixture."""
    assert sample_term.term == "mtu"
```

## Continuous Integration

Tests run automatically on:
- Every commit
- Every pull request
- Before deployment

## Test Best Practices

1. **One assertion per test** (when possible)
2. **Use descriptive test names**
3. **Test both success and failure cases**
4. **Keep tests independent**
5. **Mock external dependencies**
6. **Test edge cases**

## Common Issues

### Import Errors

If you get import errors, ensure you're running from project root:

```bash
cd /path/to/swahili-nlp-rag
pytest
```

### Database Tests

For tests requiring database:

```python
@pytest.fixture
def db_session():
    """Create test database session."""
    # Setup
    init_db()
    session = get_session()
    
    yield session
    
    # Teardown
    session.rollback()
    session.close()
```

## Performance

Current test suite runs in ~5 seconds.

Expected coverage: >90%

## Future Tests

- [ ] Repository tests (with test database)
- [ ] Use case integration tests
- [ ] API endpoint tests
- [ ] Performance tests
- [ ] Load tests
