# 🌍 Swahili NLP RAG v2.1.1-alpha

**Internal/local alpha release baseline for Swahili linguistic analysis and knowledge infrastructure.**

## Release Identity

- **Version:** `v2.1.1-alpha`
- **Release type:** Internal/local alpha release
- **Scope:** Documentation and metadata baseline only
- **Stability:** Not a public or production release

## Supported In This Alpha

- 🔤 Swahili linguistic analysis with morphology-oriented domain modeling
- 📚 Lexical and dictionary-oriented lookup flows
- 🧬 Bantu noun-class classification and root extraction
- 📰 Swahili news text and URL analysis workflows already present in the repository
- 🌐 FastAPI API and Streamlit dashboard for local/internal evaluation

## Experimental In This Alpha

- 🔍 URL fetching and article analysis across external news websites
- 📊 Research/export-oriented workflows and batch processing
- 🧪 End-to-end integration quality outside local development setups
- 🏗️ Ongoing transition from legacy term-centric structures toward lexeme-first domain modeling

## Intentionally Out Of Scope For v2.1.1-alpha

- 🚫 API route redesign or versioned route migration
- 🚫 Database schema changes or migration changes
- 🚫 Public production-readiness claims
- 🚫 Expansion of product scope beyond the current linguistic knowledge engine direction

## 🚀 Quick Start

### Local Prerequisites

- Python `3.9` to `3.11`
- `pip`
- SQLite for the default local setup
- Internet access only if you want URL-based article fetching or to install packages

### Local Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Copy local environment settings
cp .env.example .env

# 4. Initialize the local SQLite database
python -c "from src.infrastructure.database import init_db; init_db()"

# 5. Start API
uvicorn src.web.api:app --reload

# 6. Start Dashboard
streamlit run streamlit_app.py
```

### Local Run Commands

```bash
# Start the API
uvicorn src.web.api:app --reload --host 0.0.0.0 --port 8000

# Start Streamlit in a second terminal
streamlit run streamlit_app.py

# Run tests
pytest
```

### Optional Makefile Helpers

```bash
make install
make init-db
make run-api
make run-streamlit
make run-tests
```

See [RUN_LOCAL.md](/home/johnpenguim/Desktop/swahili-nlp-rag-v2.0-RESEARCH-EDITION/swahili-nlp-rag-v2/RUN_LOCAL.md) for the reproducible local runbook and [RELEASE_NOTES.md](/home/johnpenguim/Desktop/swahili-nlp-rag-v2.0-RESEARCH-EDITION/swahili-nlp-rag-v2/RELEASE_NOTES.md) for the concise alpha release notes.
