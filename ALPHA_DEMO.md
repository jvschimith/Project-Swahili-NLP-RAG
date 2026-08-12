# Alpha Demo

This file describes the main Release 1 internal alpha workflow that is realistic for local use today.

## Recommended Demo Path

Use the stable local flow instead of live URL scraping:

1. start the API
2. start Streamlit
3. load the minimal local seed dataset
4. save one additional local article through the API
5. query the saved data back through the API
6. open the dashboard and view the saved records and trends

This path avoids depending on external websites during the demo.

## Commands

### 1. Install dependencies and prepare local config

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

### 2. Initialize the database and load seed data

```bash
make init-db
make seed-data
```

### 3. Start the API

```bash
make run-api
```

Expected:

- API root: `http://localhost:8000/`
- docs: `http://localhost:8000/docs`

### 4. Start Streamlit in another terminal

```bash
source .venv/bin/activate
make run-streamlit
```

Expected:

- dashboard: `http://localhost:8501`

### 5. Save one additional local article through the API

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

### 6. Query results through the API

```bash
curl http://localhost:8000/stats
curl "http://localhost:8000/news/articles?limit=20"
curl http://localhost:8000/dictionary/mtu
curl http://localhost:8000/news/trends
```

### 7. View data in Streamlit

Open the dashboard and use:

- `📊 Database Analytics` to see saved articles and counts
- `📈 Sentiment Trends` to view trend output
- `🔤 Linguistic Insights` for local text exploration

## What This Demo Validates

- API boot
- Streamlit boot
- local data availability via seed fixtures
- article saving through `/news/save`
- persisted querying through `/stats` and `/news/articles`
- dictionary lookup through `/dictionary/{term}`
- dashboard visibility for saved data

## What Still Remains Fragile

- the URL analysis path depends on external fetching and scraping quality
- `/news/trends` is still placeholder-style rather than true database aggregation
- the dashboard is strongest for analytics and viewing, not guided ingestion from local text
- some broader ingestion flows still assume optional corpora or external raw data are available
