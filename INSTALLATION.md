# 📦 Installation & Setup Guide - v2.1 Complete

## 🚀 Quick Installation (5 Minutes)

### **Step 1: Extract Package**

```bash
# Extract the ZIP
unzip swahili-nlp-rag-v2.1-COMPLETE.zip
cd swahili-nlp-rag-v2.1-COMPLETE
```

### **Step 2: Create Virtual Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### **Step 3: Install Dependencies**

```bash
# Install all requirements
pip install -r requirements.txt

# This installs:
# - FastAPI (API)
# - Streamlit (Dashboard)
# - SQLAlchemy (Database)
# - BeautifulSoup (Web scraping)
# - Pandas, NumPy (Data)
# - Research tools (datasets, transformers, torch)
# - And more...
```

### **Step 4: Initialize Database**

```bash
# Initialize SQLite database
python -c "from src.infrastructure.database import init_db; init_db()"

# This creates:
# - swahili_nlp.db (main database)
# - Tables for news, dictionary, etc.
# - Loads Kamusi dictionary (16,600+ words)
# - Loads Masakhane datasets
```

### **Step 5: Verify Installation**

```bash
# Test import
python -c "from src.domain.services.root_extractor_enhanced import ParadigmGenerator; print('✅ Installation successful!')"
```

---

## 🖥️ Running the Application

### **Option 1: API Only**

```bash
# Start FastAPI server
uvicorn src.web.api:app --reload --host 0.0.0.0 --port 8000

# Access API docs
# http://localhost:8000/docs
```

### **Option 2: Dashboard Only**

```bash
# Start Streamlit dashboard
streamlit run streamlit_app.py

# Access dashboard
# http://localhost:8501
```

### **Option 3: Both (Recommended)**

```bash
# Terminal 1: API
uvicorn src.web.api:app --reload --port 8000

# Terminal 2: Dashboard
streamlit run streamlit_app.py

# Access:
# - API: http://localhost:8000/docs
# - Dashboard: http://localhost:8501
```

---

## 🧪 Testing Installation

### **Test 1: Basic Import**

```python
# test_installation.py
from src.domain.value_objects_enhanced import SwahiliTenses, MasakhanePOS
from src.domain.services.root_extractor_enhanced import ParadigmGenerator, EnhancedRootExtractor
from src.application.tokenizers.syllable_tokenizer import SwahiliSyllableTokenizer
from src.application.features.morphological_features import MorphologicalFeatureExtractor
from src.application.augmentation.morphological_augmenter import MorphologicalAugmenter

print("✅ All imports successful!")
```

```bash
python test_installation.py
```

### **Test 2: Paradigm Generation**

```python
# test_paradigm.py
from src.domain.services.root_extractor_enhanced import ParadigmGenerator

# Generate forms
forms = ParadigmGenerator.generate_all_forms("som")
print(f"✅ Generated {sum(len(v) for v in forms.values())} verb forms")
print(f"Present forms: {forms['present'][:3]}")
```

### **Test 3: Syllable Tokenization**

```python
# test_syllables.py
from src.application.tokenizers.syllable_tokenizer import SwahiliSyllableTokenizer

syllables = SwahiliSyllableTokenizer.tokenize("ninasoma")
print(f"✅ Syllables: {syllables}")
assert syllables == ['ni', 'na', 'so', 'ma']
```

### **Test 4: Feature Extraction**

```python
# test_features.py
from src.application.features.morphological_features import MorphologicalFeatureExtractor

features = MorphologicalFeatureExtractor.extract_features("ninasoma")
print(f"✅ Extracted {len(features.to_dict())} features")
print(f"Verb root: {features.verb_root}")
print(f"Syllable count: {features.syllable_count}")
```

### **Test 5: Data Augmentation**

```python
# test_augmentation.py
from src.application.augmentation.morphological_augmenter import MorphologicalAugmenter

original = ["Ninasoma kitabu"]
augmented = MorphologicalAugmenter.augment_with_tense_variants(original)
print(f"✅ Augmented {len(original)} → {len(augmented)} examples")
```

### **Run All Tests**

```bash
# Create test file
cat > test_all.py << 'EOF'
from src.domain.services.root_extractor_enhanced import ParadigmGenerator
from src.application.tokenizers.syllable_tokenizer import SwahiliSyllableTokenizer
from src.application.features.morphological_features import MorphologicalFeatureExtractor

# Test 1: Paradigm
forms = ParadigmGenerator.generate_all_forms("som")
assert len(forms) > 0
print("✅ Test 1: Paradigm generation - PASSED")

# Test 2: Syllables
syllables = SwahiliSyllableTokenizer.tokenize("ninasoma")
assert syllables == ['ni', 'na', 'so', 'ma']
print("✅ Test 2: Syllable tokenization - PASSED")

# Test 3: Features
features = MorphologicalFeatureExtractor.extract_features("ninasoma")
assert features.syllable_count == 4
print("✅ Test 3: Feature extraction - PASSED")

print("\n🎉 All tests PASSED! Installation is correct.")
EOF

python test_all.py
```

---

## 📁 Project Structure Overview

```
swahili-nlp-rag-v2.1-COMPLETE/
│
├── src/                          # Source code
│   ├── domain/                   # Core logic
│   │   ├── value_objects_enhanced.py      # ⭐ NEW
│   │   └── services/
│   │       └── root_extractor_enhanced.py  # ⭐ NEW
│   │
│   ├── application/              # Application layer
│   │   ├── tokenizers/           # ⭐ NEW
│   │   │   └── syllable_tokenizer.py
│   │   ├── features/             # ⭐ NEW
│   │   │   └── morphological_features.py
│   │   ├── augmentation/         # ⭐ NEW
│   │   │   └── morphological_augmenter.py
│   │   └── services/
│   │       ├── batch_processor.py        # v2.0
│   │       └── export_formats.py         # v2.0
│   │
│   ├── infrastructure/           # External deps
│   └── web/
│       └── api.py
│
├── data/                         # Data files
├── tests/                        # Test suite
├── streamlit_app.py             # Dashboard
├── requirements.txt             # Dependencies
│
└── Documentation/
    ├── README.md
    ├── MORPHOLOGICAL_ENHANCEMENTS_v2.1.md
    ├── QUICK_START_v2.1.md
    ├── PHASE1_COMPLETE.md
    └── ...
```

---

## 🔧 Troubleshooting

### **Issue: Import Errors**

```bash
# Make sure you're in virtual environment
which python  # Should show venv path

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

### **Issue: Database Not Found**

```bash
# Reinitialize database
python -c "from src.infrastructure.database import init_db; init_db()"
```

### **Issue: Module Not Found**

```python
# Add to PYTHONPATH
import sys
sys.path.append('/path/to/swahili-nlp-rag-v2.1-COMPLETE')
```

### **Issue: Port Already in Use**

```bash
# Use different port
uvicorn src.web.api:app --reload --port 8001

# Or kill process
lsof -ti:8000 | xargs kill -9
```

---

## 🎯 Next Steps

After installation:

1. ✅ Read [QUICK_START_v2.1.md](QUICK_START_v2.1.md) for examples
2. ✅ Try the dashboard at http://localhost:8501
3. ✅ Explore API at http://localhost:8000/docs
4. ✅ Read [MORPHOLOGICAL_ENHANCEMENTS_v2.1.md](MORPHOLOGICAL_ENHANCEMENTS_v2.1.md)
5. ✅ Start building your research project!

---

## 📚 Documentation Links

- **Quick Examples**: [QUICK_START_v2.1.md](QUICK_START_v2.1.md)
- **All Features**: [MORPHOLOGICAL_ENHANCEMENTS_v2.1.md](MORPHOLOGICAL_ENHANCEMENTS_v2.1.md)
- **Research Guide**: [RESEARCH_IMPORTANCE.md](RESEARCH_IMPORTANCE.md)
- **API Reference**: http://localhost:8000/docs (after starting)

---

## ✅ Installation Checklist

- [ ] Extracted ZIP file
- [ ] Created virtual environment
- [ ] Installed dependencies
- [ ] Initialized database
- [ ] Tested imports
- [ ] Started API server
- [ ] Started dashboard
- [ ] Ran test scripts
- [ ] Read documentation

---

**Installation time:** ~5 minutes  
**Difficulty:** Easy  
**Requirements:** Python 3.10+, pip, 500MB disk space

**Need help?** Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

🎉 **You're ready to go!** Start analyzing Swahili text! 🚀
