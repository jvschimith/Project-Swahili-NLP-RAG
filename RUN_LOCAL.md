# Run Local

This runbook is the reproducible local execution path for Release 1.

## Runtime Assumptions

- Python `3.9` to `3.11`
- `pip` available
- Local SQLite database for default development
- Commands are run from the repository root
- A virtual environment is strongly recommended

## Required Dependencies

- Core application dependencies are listed in `requirements.txt`
- FastAPI and Uvicorn are used for the API
- Streamlit and Plotly are used for the local dashboard
- SQLAlchemy is used for database initialization and access
- Pytest is used for tests

## First-Time Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python -c "from src.infrastructure.database import init_db; init_db()"
```

## Local Environment

Default local execution uses:

- `DATABASE_URL=sqlite:///data/swahili_knowledge.db`
- `ENVIRONMENT=development`
- `DEBUG=True`
- `API_URL=http://localhost:8000`

You can keep the defaults from `.env.example` for the first local run.

## Run the API

```bash
uvicorn src.web.api:app --reload --host 0.0.0.0 --port 8000
```

Expected local endpoints:

- API root: `http://localhost:8000/`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Run Streamlit

Open a second terminal, activate the same virtual environment, then run:

```bash
streamlit run streamlit_app.py
```

Expected local endpoint:

- Streamlit UI: `http://localhost:8501`

The Streamlit app reads `API_URL` from `.env`. For the default local setup, keep:

```bash
API_URL=http://localhost:8000
```

## Initialize or Reinitialize the Database

```bash
python -c "from src.infrastructure.database import init_db; init_db()"
```

This creates the current SQLAlchemy-defined schema for the configured database.

## Load The Minimal Release 1 Seed

```bash
python scripts/seed_release1_alpha.py
```

Or:

```bash
make seed-data
```

See [SEED_DATA.md](/home/johnpenguim/Desktop/swahili-nlp-rag-v2.0-RESEARCH-EDITION/swahili-nlp-rag-v2/SEED_DATA.md) for the fixture summary and seed contents.

## Run Tests

```bash
pytest
```

Useful variants:

```bash
pytest -v
pytest --cov=src --cov-report=html
```

## Makefile Helpers

If you prefer shorter commands:

```bash
make install
make init-db
make seed-data
make run-api
make run-streamlit
make run-tests
```

## Troubleshooting

### API cannot start

- Confirm the virtual environment is active
- Confirm dependencies are installed from `requirements.txt`
- Confirm `.env` exists or defaults are acceptable

### Streamlit cannot reach the API

- Confirm the API is running on `http://localhost:8000`
- Confirm `.env` contains `API_URL=http://localhost:8000`

### Database issues

- Confirm `DATABASE_URL` points to a writable local SQLite path
- Re-run the database init command

## Scope Notes

- This runbook does not change API routes
- This runbook does not change database schema or migrations
- This is for local/internal reproducible execution only
