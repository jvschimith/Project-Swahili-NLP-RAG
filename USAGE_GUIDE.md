# 🚀 Complete Usage Guide

## Quick Start (3 Steps)

### Step 1: Install & Setup (2 minutes)

```bash
# Extract project
unzip swahili-nlp-rag-final.zip
cd swahili-nlp-rag-en

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install all dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.infrastructure.database import init_db; init_db()"
```

### Step 2: Start API (1 minute)

```bash
# Start the FastAPI server
uvicorn src.web.api:app --reload

# API will be available at:
# - http://localhost:8000
# - Docs: http://localhost:8000/docs
```

### Step 3: Launch Dashboard (1 minute)

```bash
# In a new terminal (keep API running)
streamlit run streamlit_app.py

# Dashboard will open at:
# - http://localhost:8501
```

**That's it! You're ready to analyze Swahili news! 🎉**

---

## Analyzing News from URLs

### Using the Dashboard (Easiest)

1. Open: http://localhost:8501
2. Go to **🔗 URL Analysis** page
3. Paste a news URL (e.g., https://www.bbc.com/swahili)
4. Click **🔍 Analyze**
5. View results:
   - Word count, sentences, vocabulary
   - Sentiment analysis (positive/negative/neutral)
   - Top keywords
   - Language statistics

### Using the API Directly

```bash
# Analyze a news URL
curl -X POST http://localhost:8000/analyze/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.bbc.com/swahili/articles/c1234567"
  }'
```

**Response:**
```json
{
  "success": true,
  "url": "https://www.bbc.com/swahili/...",
  "word_count": 450,
  "sentence_count": 25,
  "unique_words": 280,
  "vocabulary_richness": 0.62,
  "sentiment": {
    "polarity": 0.15,
    "confidence": 0.75,
    "label": "positive",
    "positive_words_found": 8,
    "negative_words_found": 3
  },
  "top_keywords": [
    {"word": "uchumi", "count": 12},
    {"word": "serikali", "count": 8}
  ]
}
```

### Supported News Sources

✅ **Swahili News Sites:**
- BBC Swahili: https://www.bbc.com/swahili
- VOA Swahili: https://www.voaswahili.com/
- DW Swahili: https://www.dw.com/sw
- Mwananchi: https://www.mwananchi.co.tz/
- The Citizen: https://www.thecitizen.co.tz/
- Daily News: https://dailynews.co.tz/

---

## Dashboard Features

### 🔗 URL Analysis Tab
- Paste any Swahili news URL
- Get instant analysis
- View sentiment gauge
- See top keywords (bar chart)
- Language statistics (pie chart)

### 📊 Database Analytics Tab
- View database statistics
- Articles by category (pie chart)
- Sentiment distribution (bar chart)
- Recent articles table

### 📈 Sentiment Trends Tab
- Sentiment over time (line chart)
- Positive/negative/neutral trends
- Summary statistics

### 🔤 Linguistic Statistics Tab
- Analyze custom Swahili text
- Test Bantu classification
- Word-level analysis

---

## API Endpoints Reference

### News Analysis

```bash
# Analyze URL
POST /analyze/url
Body: {"url": "https://..."}

# Analyze text
POST /analyze/sentiment
Body: {"text": "Habari njema leo..."}

# Get news articles
GET /news/articles?category=Kitaifa&limit=20

# Get sentiment trends
GET /news/trends
```

### Dictionary & Classification

```bash
# Lookup dictionary
GET /dictionary/mtu

# Search dictionary
GET /dictionary/search/?q=binadamu

# Classify Bantu
POST /classify/bantu
Body: {"word": "kitabu", "word_type": "noun"}

# Extract root
POST /extract/root
Body: {"word": "ninasoma", "word_type": "verb"}
```

### Database

```bash
# Get statistics
GET /stats

# Lookup term
GET /terms/mtu

# Search terms
GET /terms/search/?q=mtu
```

---

## Python Usage Examples

### Analyze Multiple URLs

```python
import requests

API_URL = "http://localhost:8000"

urls = [
    "https://www.bbc.com/swahili/articles/c123",
    "https://www.voaswahili.com/a/456.html",
    "https://www.dw.com/sw/789"
]

results = []
for url in urls:
    response = requests.post(
        f"{API_URL}/analyze/url",
        json={"url": url}
    )
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            results.append({
                "url": url,
                "sentiment": data["sentiment"]["label"],
                "polarity": data["sentiment"]["polarity"],
                "word_count": data["word_count"]
            })

# Save to CSV
import pandas as pd
df = pd.DataFrame(results)
df.to_csv("news_analysis.csv", index=False)
print(f"Analyzed {len(results)} articles")
```

### Batch Classification

```python
words = ["mtu", "watu", "kitabu", "vitabu", "nyumba"]

for word in words:
    response = requests.post(
        f"{API_URL}/classify/bantu",
        json={"word": word, "word_type": "noun"}
    )
    if response.status_code == 200:
        result = response.json()
        print(f"{word:15} → {result['bantu_class']:10} ({result['description']})")
```

---

## Troubleshooting

### API Won't Start

```bash
# Check if port 8000 is in use
lsof -i :8000  # Mac/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
uvicorn src.web.api:app --port 8001
```

### Dashboard Can't Connect

1. Make sure API is running first
2. Check API URL in `streamlit_app.py` (line 27)
3. Try accessing http://localhost:8000/docs manually

### URL Analysis Fails

**Common issues:**
- Website blocks scrapers → Try different URL
- No Swahili content → Check source language
- Timeout → Increase timeout in url_analyzer.py

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Python version (need 3.9+)
python --version
```

---

## Performance Tips

### For Faster Analysis

1. **Use batch endpoints** for multiple URLs
2. **Cache results** in database
3. **Run API on production server** (not --reload)
4. **Use async** for concurrent analysis

### Production Deployment

```bash
# Install production server
pip install gunicorn

# Run with workers
gunicorn src.web.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## Example Workflows

### Workflow 1: Daily News Monitoring

```python
# Monitor BBC Swahili daily
urls = [
    "https://www.bbc.com/swahili",
    # Add more URLs
]

for url in urls:
    result = analyze_url(url)
    if result["sentiment"]["label"] == "negative":
        send_alert(result)  # Custom function
```

### Workflow 2: Linguistic Research

```python
# Analyze vocabulary richness across sources
sources = {
    "BBC": "https://www.bbc.com/swahili/...",
    "VOA": "https://www.voaswahili.com/...",
}

for name, url in sources.items():
    result = analyze_url(url)
    print(f"{name}: Vocabulary Richness = {result['vocabulary_richness']}")
```

### Workflow 3: Content Classification

```python
# Classify articles by sentiment
articles = fetch_recent_articles()

positive = [a for a in articles if a["sentiment"] == "positive"]
negative = [a for a in articles if a["sentiment"] == "negative"]

print(f"Positive: {len(positive)}, Negative: {len(negative)}")
```

---

## Advanced Features

### Custom Sentiment Lexicon

Edit `src/application/services/url_analyzer.py`:

```python
positive_words = {
    'furaha', 'nzuri', 'vizuri',
    # Add your words here
}
```

### Custom Stopwords

Edit `src/application/services/text_processor.py`:

```python
STOPWORDS = {
    'na', 'ya', 'wa',
    # Add your stopwords here
}
```

### Export Data

```python
# From API to CSV
import pandas as pd

response = requests.get(f"{API_URL}/news/articles?limit=1000")
articles = response.json()
df = pd.DataFrame(articles)
df.to_csv("all_articles.csv", index=False)
```

---

## Getting Help

- **API Documentation**: http://localhost:8000/docs
- **Test Endpoints**: Use Swagger UI at /docs
- **Check Logs**: Look at terminal output
- **GitHub Issues**: (your repository URL)

---

## Next Steps

1. ✅ **Ingest Kamusi dictionary** (16,600 words)
   ```bash
   python scripts/04_ingest_kamusi.py --csv
   ```

2. ✅ **Analyze live news daily**
3. ✅ **Build custom dashboards**
4. ✅ **Integrate with other systems**
5. ✅ **Deploy to production**

---

**You're all set! Start analyzing Swahili news! 🚀**
