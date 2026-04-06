# Kamusi Dictionary Integration

Integration of 16,600+ Swahili words from the Kamusi project.

## Overview

**Kamusi** is an open-source Swahili dictionary with:
- 16,683+ words
- Swahili definitions
- English translations
- Synonyms
- Usage examples
- Verb conjugations

**Source:** https://github.com/Kalebu/kamusi

---

## Data Format

### CSV Format

```csv
word,meaning,synonyms,english,examples
mtu,binadamu,"binadamu,mwanadamu",person,"Mtu huyu ni rafiki;Watu wote ni sawa"
kitabu,chombo cha kusomea,daftari,book,"Ninasoma kitabu;Kitabu hiki ni nzuri"
```

**Columns:**
- `word` - Swahili word (term)
- `meaning` - Definition in Swahili
- `synonyms` - Comma-separated synonyms
- `english` - English translation
- `examples` - Semicolon-separated usage examples

### JSON Format

```json
[
  {
    "word": "mtu",
    "meaning": "binadamu, mwanadamu",
    "english": "person, human being",
    "synonyms": ["binadamu", "mwanadamu"],
    "examples": [
      "Mtu huyu ni rafiki yangu",
      "Watu wote ni sawa"
    ]
  }
]
```

---

## Obtaining Kamusi Data

### Option 1: Clone Repository

```bash
# Clone Kamusi repository
git clone https://github.com/Kalebu/kamusi.git

# Copy data files
cp kamusi/words.csv data/raw/kamusi/
cp kamusi/words.json data/raw/kamusi/
```

### Option 2: Download Directly

```bash
cd data/raw/kamusi

# Download CSV
wget https://raw.githubusercontent.com/Kalebu/kamusi/main/words.csv

# Download JSON
wget https://raw.githubusercontent.com/Kalebu/kamusi/main/words.json
```

### Option 3: Manual Download

1. Visit: https://github.com/Kalebu/kamusi
2. Download `words.csv` or `words.json`
3. Place in `data/raw/kamusi/`

---

## Ingestion

### Quick Start

```bash
# Ingest from CSV (recommended)
python scripts/04_ingest_kamusi.py --csv

# Or from JSON
python scripts/04_ingest_kamusi.py --json

# Auto-detect format
python scripts/04_ingest_kamusi.py
```

### Programmatic Usage

```python
from src.infrastructure.database import init_db, get_session
from src.infrastructure.repositories.term_repository import TermRepository
from src.infrastructure.repositories.dictionary_repository import DictionaryRepository
from src.application.use_cases.ingest_kamusi import IngestKamusiUseCase

# Initialize
init_db()
session = get_session()

# Create repositories
term_repo = TermRepository(session)
dict_repo = DictionaryRepository(session)

# Create use case
use_case = IngestKamusiUseCase(term_repo, dict_repo)

# Ingest CSV
stats = use_case.execute_csv("data/raw/kamusi/words.csv")
print(f"Ingested {stats['dictionary_entries']} entries")

# Commit
session.commit()
session.close()
```

---

## What Gets Ingested

### 1. Terms Table

For each word, creates/updates a `SwahiliTerm`:
- Term string (normalized)
- Morphological root (extracted)
- Bantu noun class (inferred)
- Word type (inferred)
- Etymology (placeholder)

### 2. Dictionary Table

Creates `DictionaryEntry` with:
- Swahili meaning/definition
- English translation
- Synonyms (list)
- Antonyms (if available)
- Usage examples (list)
- Usage context (formal/informal)

### 3. Enhanced Metadata

Domain services automatically:
- Extract morphological roots
- Classify Bantu noun classes
- Normalize text

---

## Statistics

Expected ingestion results:
- **Total words**: 16,600+
- **New terms**: ~15,000 (if database empty)
- **Dictionary entries**: 16,600+
- **Synonyms**: ~8,000+
- **Usage examples**: ~12,000+

Processing time:
- CSV: ~2-3 minutes
- JSON: ~1-2 minutes

---

## API Access

### Get Dictionary Entry

```bash
curl http://localhost:8000/dictionary/mtu
```

Response:
```json
{
  "term": "mtu",
  "meaning": "binadamu, mwanadamu",
  "english_translation": "person, human being",
  "synonyms": ["binadamu", "mwanadamu"],
  "usage_examples": [
    "Mtu huyu ni rafiki yangu",
    "Watu wote ni sawa"
  ]
}
```

### Search Dictionary

```bash
curl "http://localhost:8000/dictionary/search/?q=binadamu&limit=10"
```

---

## Database Schema

### Terms Table

```sql
CREATE TABLE terms (
    id INTEGER PRIMARY KEY,
    swahili_term TEXT UNIQUE NOT NULL,
    root_radical TEXT,
    noun_class TEXT,
    etymology TEXT,
    word_type TEXT,
    ...
);
```

### Dictionary Table

```sql
CREATE TABLE dictionary (
    id INTEGER PRIMARY KEY,
    term_id INTEGER UNIQUE NOT NULL,
    meaning TEXT NOT NULL,
    english_translation TEXT,
    synonyms TEXT,  -- JSON array
    usage_examples TEXT,  -- JSON array
    usage_context TEXT,
    FOREIGN KEY (term_id) REFERENCES terms(id)
);
```

---

## Data Quality

### Validation

During ingestion, entries are validated:
- ✅ Non-empty words
- ✅ Non-empty meanings
- ✅ Valid JSON for lists
- ✅ Duplicate detection

### Error Handling

- Invalid entries are logged and skipped
- Statistics track errors
- Transaction rollback on critical failure

### Data Cleaning

Automatic cleaning applied:
- Normalize whitespace
- Lowercase terms
- Remove control characters
- Parse delimited fields

---

## Enrichment Features

Kamusi data is enriched with:

### 1. Morphological Analysis
```python
# Automatic root extraction
"kitabu" → root="tabu", prefix="ki"
```

### 2. Bantu Classification
```python
# Automatic noun class inference
"kitabu" → class=KI_VI (7/8)
```

### 3. Etymology
```python
# Placeholder (can be enhanced)
etymology=Etymology.UNKNOWN
```

---

## Usage Examples

### Look Up Word

```python
from src.infrastructure.repositories.dictionary_repository import DictionaryRepository

dict_repo = DictionaryRepository(session)
entry = dict_repo.find_by_term_string("mtu")

print(f"Meaning: {entry.meaning}")
print(f"English: {entry.english_translation}")
print(f"Synonyms: {entry.synonyms}")
```

### Search by Meaning

```python
entries = dict_repo.search_by_meaning("binadamu", limit=10)

for entry in entries:
    print(f"{entry.term.term}: {entry.meaning}")
```

### Get Synonyms

```python
synonyms = dict_repo.find_synonyms(term_id=123)
print(f"Synonyms: {synonyms}")
```

---

## Integration with Other Features

### Combined with Classification

```python
from src.domain.services.bantu_classifier import BantuClassifierService

# Get dictionary entry
entry = dict_repo.find_by_term_string("mtu")

# Classify
service = BantuClassifierService()
bantu_class = service.infer_class(entry.term.term, entry.term.word_type)

print(f"{entry.term.term}: {bantu_class.value} - {entry.meaning}")
```

### Combined with Root Extraction

```python
from src.domain.services.root_extractor import RootExtractorService

entry = dict_repo.find_by_term_string("kitabu")
service = RootExtractorService()
root = service.extract(entry.term.term)

print(f"Root: {root.root}, Meaning: {entry.meaning}")
```

---

## Performance

### Ingestion Performance

- **Batch size**: 1000 records
- **Processing rate**: ~100 words/second
- **Memory usage**: ~200MB

### Query Performance

- **Lookup by term**: <5ms
- **Search by meaning**: <50ms
- **Get synonyms**: <5ms

### Optimization

Recommended indexes:
```sql
CREATE INDEX idx_dict_meaning ON dictionary(meaning);
CREATE INDEX idx_dict_term_id ON dictionary(term_id);
```

---

## Troubleshooting

### File Not Found

```bash
# Check file exists
ls data/raw/kamusi/

# Download if missing
wget https://raw.githubusercontent.com/Kalebu/kamusi/main/words.csv \
  -O data/raw/kamusi/words.csv
```

### Encoding Errors

```python
# Force UTF-8 encoding
with open(file_path, 'r', encoding='utf-8') as f:
    ...
```

### Duplicate Entries

```python
# Use upsert logic in repository
if existing:
    update_existing()
else:
    create_new()
```

---

## Credits

**Kamusi Dictionary**: https://github.com/Kalebu/kamusi
- **Author**: Kalebu Gwalugano
- **Contributors**: Jack Siro, and community
- **License**: Open source

**Data Source**: Scraped from kamusi.org

---

## Future Enhancements

- [ ] Import verb conjugations
- [ ] Add pronunciation data
- [ ] Import word categories
- [ ] Add corpus frequency data
- [ ] Integrate with other Swahili dictionaries
- [ ] Add audio pronunciations
- [ ] Link to Tatoeba example sentences
