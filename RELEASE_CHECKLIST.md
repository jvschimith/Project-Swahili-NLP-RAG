# Release Checklist

## v2.1.1-alpha

Use this checklist to decide whether the repository is ready for internal alpha use.

## Environment Setup

- [ ] Work from the repository root
- [ ] Use Python `3.9` to `3.11`
- [ ] Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## Dependency Install

- [ ] Upgrade `pip`
- [ ] Install dependencies from `requirements.txt`
- [ ] Copy `.env.example` to `.env`

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

## Database Init

- [ ] Initialize the local SQLite database
- [ ] Confirm no initialization errors

```bash
make init-db
```

## Seed Loading

- [ ] Load the minimal Release 1 seed dataset
- [ ] Confirm dictionary, linguistic sample, and news/example rows are inserted

```bash
make seed-data
```

## API Startup

- [ ] Start FastAPI locally
- [ ] Confirm `http://localhost:8000/health` responds successfully
- [ ] Confirm docs load at `http://localhost:8000/docs`

```bash
make run-api
```

## Streamlit Startup

- [ ] Start Streamlit in a second terminal
- [ ] Confirm the dashboard loads at `http://localhost:8501`
- [ ] Confirm sidebar stats render when the API is running

```bash
make run-streamlit
```

## Smoke Tests

- [ ] Run the stable local smoke suite
- [ ] Confirm health, lookup, classification, root extraction, save, trends, stats, and stubbed URL analysis checks pass
- [ ] Run optional integration smoke tests only if explicitly needed

```bash
python3 -m pytest tests/smoke/test_api_smoke.py -q
RUN_OPTIONAL_INTEGRATION=1 python3 -m pytest tests/smoke/test_api_optional_integration.py -q
```

## Linguistic Validation

- [ ] Run the frozen linguistic/domain tests
- [ ] Confirm the required forms remain stable:
  `mtu`, `watu`, `soma`, `ninasoma`, `ninakupenda`
- [ ] Confirm lemma, word type, noun class, morphology, and Lexeme/WordForm consistency remain unchanged

```bash
python3 -m pytest tests/domain/test_linguistic_analysis_service.py -q
```

## Demo Validation

- [ ] Follow the stable local alpha demo path in `ALPHA_DEMO.md`
- [ ] Save one local article through `/news/save`
- [ ] Confirm `/stats`, `/news/articles`, `/dictionary/mtu`, and `/news/trends` return usable results
- [ ] Confirm data is visible in `Database Analytics` and `Sentiment Trends`

Key command from the demo:

```bash
curl -X POST http://localhost:8000/news/save \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Mtu mmoja anasoma habari za elimu mjini Dodoma kila asubuhi.",
    "category": "Education",
    "source_url": "seed://alpha-demo/manual-save-001",
    "sentiment_polarity": 0.3,
    "sentiment_confidence": 0.8,
    "sentiment_label": "positive"
  }'
```

## Go / No-Go

### Go

Choose **Go** for internal alpha if all of the following are true:

- [ ] local setup succeeds from a clean environment
- [ ] database init and seed loading succeed
- [ ] API and Streamlit both start locally
- [ ] stable smoke tests pass
- [ ] frozen linguistic validation passes
- [ ] the local alpha demo workflow completes successfully

### No-Go

Choose **No-Go** if any of the following are true:

- [ ] local setup cannot be reproduced from the documented steps
- [ ] `/news/save` does not persist data across requests
- [ ] dashboard cannot read the local API
- [ ] stable smoke or frozen linguistic tests fail
- [ ] the demo depends on live URL scraping to succeed

## Known Alpha Fragility

- `/analyze/url` remains dependent on external fetching and scraping quality
- `/news/trends` is still placeholder-style, not true DB aggregation
- full validation still depends on having local test/runtime dependencies installed
