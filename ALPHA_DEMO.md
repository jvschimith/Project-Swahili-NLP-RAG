# Current Project Presentation and Demo

This is the presentation-ready path for the current alpha. It shows a Swahili linguistic
knowledge system with a deterministic local core and an experimental, provenance-preserving
public-corpus workflow. It is not a chatbot, a generic RAG product, or a production crawler.

## Presentation Narrative

1. **Problem:** Swahili surface words encode grammatical structure that term-centric search
   loses.
2. **Linguistic model:** the system separates `Lexeme`, `WordForm`, `Meaning`, `Context`,
   `Derivation`, and morphological analysis.
3. **Working product surface:** FastAPI exposes structured lexical, morphology, dictionary,
   article, and research-helper responses in English.
4. **Knowledge acquisition:** static public pages pass URL safety, robots, rate, budget,
   candidate-quality, extraction, language, provenance, and deduplication controls.
5. **Research evidence:** a bounded seven-source pilot produced 52 artifacts in 70 attempts;
   its limitations and rejection reasons are recorded rather than hidden.
6. **Next milestone:** improve generic corpus acceptance for short pages, media placeholders,
   boilerplate, and wrong content types before expanding collection.

## Current Architecture

```text
public/local Swahili text
          |
          v
responsible crawl -> acquisition/validation -> immutable JSON + JSONL corpus
          |                     |
          v                     v
 SQLite checkpoints       provenance and review
          \_____________________/
                    |
          research query service -> local Streamlit console

local text -> morphology and lexical services -> FastAPI -> structured English output
```

## Recommended Demo Path

Start with the stable local flow. It does not depend on external websites:

1. start the API
2. start Streamlit
3. load the minimal local seed dataset
4. save one additional local article through the API
5. query the saved data back through the API
6. open the dashboard and view the saved records and trends;
7. analyze a Swahili form and explain the lexeme/word-form distinction.

This path avoids depending on external websites during the demo.

## Commands

### 1. Install dependencies and prepare local config

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[web,dashboard,dev]'
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

Use the interactive documentation at `http://localhost:8000/docs` to run the morphology
endpoint with a form such as `ninasoma`. Explain that the observed form is preserved while
the current analyzer derives the canonical verb `kusoma`, radical `som`, final vowel `a`,
and grammatical prefix evidence. The analyzer is heuristic and must not be presented as a
gold-standard annotation system.

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
- structured linguistic output that preserves the lexeme/word-form distinction

## Optional Corpus Research Demonstration

This part performs real requests to public sites. Run it only with intended network access,
and never make it a prerequisite for the stable local demo.

```bash
python -m src.research.run_corpus_pilot
```

In another terminal:

```bash
CORPUS_PILOT_DB=data/corpus-pilot/pilot.sqlite \
CORPUS_PILOT_ROOT=data/corpus-pilot/corpus \
streamlit run src/research_ui/corpus_pilot.py --server.address 127.0.0.1
```

Present these views in order:

1. overview and current persisted activity;
2. frontier eligibility and pre-acquisition skips;
3. acquisition outcomes and structured rejection reasons;
4. immutable corpus artifacts and provenance;
5. source comparison;
6. deterministic quality-review sample.

The recorded reference pilot discovered 1,937 URLs, attempted 70 acquisitions, stored 52
artifacts, and preserved 204,627 normalized characters. Its 74.3% artifact yield is an
operational measure. In the deliberately weakness-enriched review sample, 10 of 21 items
were good or acceptable; this is not a population-quality estimate. Full evidence is in
`docs/PUBLIC_SWAHILI_CORPUS_PILOT.md`.

## Boundaries to State Clearly

- morphology and noun-class decisions remain heuristic and uncalibrated;
- the corpus pilot is bounded and not representative of Swahili usage;
- accepted pages may still contain boilerplate, media placeholders, or the wrong content type;
- Streamlit is temporary local research infrastructure, not the production frontend;
- live results depend on publisher content, robots policy, connectivity, and static HTML;
- no LLM or evidence-to-generation RAG path is present in the runtime.

## Suggested Closing

The project now demonstrates an end-to-end path from real Swahili usage to inspectable,
provenance-preserving research artifacts and structured linguistic queries. Its strongest
claim is not that every analysis is solved, but that linguistic structure, uncertainty,
source policy, and empirical failures are represented explicitly enough to improve the
system without collapsing language into undifferentiated text.
