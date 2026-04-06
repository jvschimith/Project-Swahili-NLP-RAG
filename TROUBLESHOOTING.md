# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### Installation Issues

#### **Issue: Import Errors**

```bash
ModuleNotFoundError: No module named 'src'
```

**Solution:**
```bash
# Make sure you're in the project root
cd swahili-nlp-rag-v2.1-FINAL

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### **Issue: Database Not Found**

```bash
sqlite3.OperationalError: no such table: terms
```

**Solution:**
```bash
# Initialize database
python -c "from src.infrastructure.database import init_db; init_db()"
```

#### **Issue: Port Already in Use**

```bash
ERROR: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows

# Or use different port
uvicorn src.web.api:app --port 8001
```

---

### Runtime Issues

#### **Issue: Relative Import Errors**

```python
ImportError: attempted relative import beyond top-level package
```

**Solution:**
```python
# Run from project root
cd swahili-nlp-rag-v2.1-FINAL
python -m src.web.api

# Or use uvicorn
uvicorn src.web.api:app --reload
```

#### **Issue: Missing Enhancement Modules**

```python
ModuleNotFoundError: No module named 'src.application.tokenizers'
```

**Solution:**
```bash
# Check directory structure
ls src/application/tokenizers/
ls src/application/features/
ls src/application/augmentation/

# Should see __init__.py files
# If missing, create them:
touch src/application/tokenizers/__init__.py
touch src/application/features/__init__.py
touch src/application/augmentation/__init__.py
```

---

### Feature-Specific Issues

#### **Issue: Paradigm Generation Fails**

```python
AttributeError: 'VerbComponents' object has no attribute 'root'
```

**Solution:**
```python
# Use enhanced root extractor
from src.domain.services.root_extractor_enhanced import EnhancedRootExtractor

# Not the old one
# from src.domain.services.root_extractor import RootExtractorService
```

#### **Issue: Syllable Tokenizer Returns Empty List**

```python
syllables = SwahiliSyllableTokenizer.tokenize("test")
# Returns: []
```

**Solution:**
```python
# Make sure word is lowercase
word = "Ninasoma".lower()
syllables = SwahiliSyllableTokenizer.tokenize(word)
# Returns: ['ni', 'na', 'so', 'ma']
```

---

### API Issues

#### **Issue: 404 on /batch Endpoints**

```bash
404 Not Found: POST /batch/create
```

**Solution:**
```bash
# Make sure you're using v2.1 API
# Check version at http://localhost:8000/
# Should return: "version": "2.1.0"

# If not, restart API
uvicorn src.web.api:app --reload
```

#### **Issue: Database Locked**

```bash
sqlite3.OperationalError: database is locked
```

**Solution:**
```python
# This is already fixed in v2.1 with WAL mode
# If still occurs, restart the application

# Or manually enable WAL:
import sqlite3
conn = sqlite3.connect('swahili_nlp.db')
conn.execute('PRAGMA journal_mode=WAL')
conn.close()
```

---

### Dashboard Issues

#### **Issue: Streamlit Won't Start**

```bash
streamlit: command not found
```

**Solution:**
```bash
# Install streamlit
pip install streamlit

# Or reinstall all dependencies
pip install -r requirements.txt
```

#### **Issue: Dashboard Shows Old Version**

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart dashboard
streamlit run streamlit_app.py
```

---

### Data Augmentation Issues

#### **Issue: Augmentation Returns Same Data**

```python
augmented = MorphologicalAugmenter.augment_with_tense_variants(["Ninasoma"])
# Returns only 1 item
```

**Solution:**
```python
# Check that your input contains verbs
# Augmentation only works on verbs with extractable roots

# Verify extraction works:
components = EnhancedRootExtractor.extract_verb_components("ninasoma")
print(components.root)  # Should print 'som'
```

---

### Performance Issues

#### **Issue: Batch Processing Too Slow**

**Solution:**
```python
# Increase workers (default is 3)
batch_processor = BatchProcessor(max_workers=5)

# Or decrease delay
batch_processor = BatchProcessor(delay_between_requests=1.0)  # Default 2.0
```

#### **Issue: Memory Usage Too High**

**Solution:**
```bash
# Process in smaller batches
# Instead of 1000 URLs at once, do 100 at a time

# Or increase system memory
# Recommended: 2GB+ for batch processing
```

---

### Testing Issues

#### **Issue: Tests Fail with Import Errors**

```bash
pytest tests/
# ImportError: cannot import name...
```

**Solution:**
```bash
# Install in development mode
pip install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;%cd%          # Windows

# Run tests
pytest tests/ -v
```

---

## Environment-Specific Issues

### **Windows**

#### Issue: venv Activation
```bash
# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then activate
.\venv\Scripts\activate
```

### **Mac M1/M2**

#### Issue: Torch Installation
```bash
# Use conda for torch on M1/M2
conda install pytorch -c pytorch

# Or install CPU-only version
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### **Linux**

#### Issue: Permission Denied
```bash
# If database file has permission issues
chmod 666 swahili_nlp.db
```

---

## Getting Help

If your issue isn't listed here:

1. Check the [INSTALLATION.md](INSTALLATION.md) guide
2. Review [MORPHOLOGICAL_ENHANCEMENTS_v2.1.md](MORPHOLOGICAL_ENHANCEMENTS_v2.1.md)
3. Search existing GitHub issues
4. Create a new issue with:
   - Python version (`python --version`)
   - OS and version
   - Complete error message
   - Steps to reproduce

---

## Quick Diagnostics

Run this diagnostic script:

```python
# diagnose.py
print("=== Swahili NLP v2.1 Diagnostics ===\n")

# 1. Check Python version
import sys
print(f"Python: {sys.version}")

# 2. Check imports
try:
    from src.domain.services.root_extractor_enhanced import ParadigmGenerator
    print("✅ Enhanced root extractor: OK")
except Exception as e:
    print(f"❌ Enhanced root extractor: {e}")

try:
    from src.application.tokenizers.syllable_tokenizer import SwahiliSyllableTokenizer
    print("✅ Syllable tokenizer: OK")
except Exception as e:
    print(f"❌ Syllable tokenizer: {e}")

try:
    from src.application.features.morphological_features import MorphologicalFeatureExtractor
    print("✅ Feature extractor: OK")
except Exception as e:
    print(f"❌ Feature extractor: {e}")

try:
    from src.application.augmentation.morphological_augmenter import MorphologicalAugmenter
    print("✅ Augmenter: OK")
except Exception as e:
    print(f"❌ Augmenter: {e}")

# 3. Check database
try:
    from src.infrastructure.database import get_session
    session = next(get_session())
    print("✅ Database: OK")
except Exception as e:
    print(f"❌ Database: {e}")

print("\n=== Diagnostics Complete ===")
```

```bash
python diagnose.py
```

---

**Version:** 2.1.0  
**Last Updated:** March 2026
