# REST API Documentation

FastAPI REST API for Swahili Linguistic Intelligence.

**Release baseline:** `v2.1.1-alpha`  
**Release type:** internal/local alpha release

## Quick Start

### Run the API

```bash
# From project root
uvicorn src.web.api:app --reload

# Or with custom host/port
uvicorn src.web.api:app --host 0.0.0.0 --port 8000
```

### Access Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Endpoints

### Health & Info

#### `GET /`
Root endpoint with API information.

**Response:**
```json
{
  "message": "Swahili Linguistic Intelligence API",
  "version": "v2.1.1-alpha",
  "docs": "/docs"
}
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "v2.1.1-alpha",
  "database": "connected"
}
```

#### `GET /stats`
Get database statistics.

**Response:**
```json
{
  "terms": 1500,
  "news_articles": 1000,
  "bantu_classes": 7
}
```

---

### Terms

#### `GET /terms/{term}`
Lookup a Swahili term.

**Parameters:**
- `term` (path) - Swahili word to lookup

**Response:**
```json
{
  "term": "mtu",
  "root": "tu",
  "noun_class": "1/2",
  "etymology": "bantu",
  "word_type": "noun",
  "is_stopword": false,
  "frequency_score": 15.5
}
```

**Error Codes:**
- `404` - Term not found

#### `GET /terms/search/?q={query}`
Search terms by prefix.

**Query Parameters:**
- `q` (required) - Search query
- `limit` (optional) - Max results (default: 10, max: 100)

**Response:**
```json
[
  {
    "term": "mtu",
    "root": "tu",
    "noun_class": "1/2",
    ...
  }
]
```

---

### Dictionary (Kamusi)

#### `GET /dictionary/{term}`
Get dictionary entry for a term.

**Parameters:**
- `term` (path) - Swahili word

**Response:**
```json
{
  "term": "mtu",
  "meaning": "binadamu, mwanadamu",
  "english_translation": "person, human being",
  "synonyms": ["binadamu", "mwanadamu"],
  "usage_examples": [
    "Mtu huyu ni rafiki yangu",
    "Watu wote ni sawa"
  ],
  "usage_context": "formal"
}
```

**Error Codes:**
- `404` - Dictionary entry not found

#### `GET /dictionary/search/?q={query}`
Search dictionary by meaning.

**Query Parameters:**
- `q` (required) - Search query (in Swahili)
- `limit` (optional) - Max results (default: 10, max: 50)

**Response:**
```json
[
  {
    "term": "mtu",
    "meaning": "binadamu",
    ...
  },
  {
    "term": "binadamu",
    "meaning": "mwanadamu",
    ...
  }
]
```

---

### Classification

#### `POST /classify/bantu`
Classify Bantu noun class of a word.

**Request Body:**
```json
{
  "word": "kitabu",
  "word_type": "noun"
}
```

**Response:**
```json
{
  "word": "kitabu",
  "bantu_class": "7/8",
  "description": "Tools and artifacts",
  "examples": [
    ["kiti", "viti", "chair/chairs"],
    ["kisu", "visu", "knife/knives"]
  ]
}
```

---

### Morphology

#### `POST /extract/root`
Extract morphological root from a word.

**Request Body:**
```json
{
  "word": "ninasoma",
  "word_type": "verb",
  "aggressive": false
}
```

**Response:**
```json
{
  "word": "ninasoma",
  "root": "som",
  "prefix": "nina",
  "suffix": "a",
  "full_word": "ninasoma"
}
```

---

### Analysis

#### `POST /analyze/sentiment`
Analyze sentiment of Swahili text.

**Request Body:**
```json
{
  "text": "Ninafurahi sana leo!"
}
```

**Response:**
```json
{
  "text": "Ninafurahi sana leo!",
  "polarity": 0.8,
  "confidence": 0.9,
  "label": "positive",
  "word_count": 3
}
```

---

### News

#### `GET /news/articles`
Get news articles.

**Query Parameters:**
- `category` (optional) - Filter by category
- `limit` (optional) - Max results (default: 10, max: 100)

**Response:**
```json
[
  {
    "id": 1,
    "content": "Rais ametembelea...",
    "category": "Kitaifa",
    "date_published": "2024-03-01T10:00:00",
    "sentiment_label": "neutral"
  }
]
```

#### `GET /news/trends`
Get sentiment trends over time.

**Response:**
```json
[
  {
    "date": "2024-01",
    "positive": 10,
    "negative": 5,
    "neutral": 15
  },
  {
    "date": "2024-02",
    "positive": 12,
    "negative": 3,
    "neutral": 18
  }
]
```

---

## Authentication

Currently, the API is open (no authentication required).

For production, consider adding:
- API keys
- OAuth2 / JWT tokens
- Rate limiting

---

## Error Responses

All errors follow this format:

```json
{
  "error": "Error message",
  "status_code": 404
}
```

**Common Status Codes:**
- `200` - Success
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

---

## Rate Limiting

No rate limiting currently implemented.

Recommended for production:
- 100 requests/minute per IP
- 1000 requests/hour per API key

---

## CORS

CORS is enabled for all origins (`*`).

For production, configure specific origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

---

## Testing the API

### cURL Examples

```bash
# Get term
curl http://localhost:8000/terms/mtu

# Classify Bantu
curl -X POST http://localhost:8000/classify/bantu \
  -H "Content-Type: application/json" \
  -d '{"word": "kitabu", "word_type": "noun"}'

# Extract root
curl -X POST http://localhost:8000/extract/root \
  -H "Content-Type: application/json" \
  -d '{"word": "ninasoma", "word_type": "verb"}'

# Get dictionary entry
curl http://localhost:8000/dictionary/mtu
```

### Python Examples

```python
import requests

# Get term
response = requests.get("http://localhost:8000/terms/mtu")
print(response.json())

# Classify Bantu
response = requests.post(
    "http://localhost:8000/classify/bantu",
    json={"word": "kitabu", "word_type": "noun"}
)
print(response.json())

# Get dictionary entry
response = requests.get("http://localhost:8000/dictionary/mtu")
print(response.json())
```

### JavaScript Examples

```javascript
// Get term
fetch('http://localhost:8000/terms/mtu')
  .then(res => res.json())
  .then(data => console.log(data));

// Classify Bantu
fetch('http://localhost:8000/classify/bantu', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({word: 'kitabu', word_type: 'noun'})
})
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Deployment

### Production Setup

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn src.web.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.web.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
export DATABASE_URL=postgresql://user:pass@host:5432/db
export LOG_LEVEL=INFO
export DEBUG=False
```

---

## Performance

Expected performance:
- Response time: <100ms (local database)
- Throughput: ~1000 req/s (single worker)
- Memory: ~100MB per worker

---

## Future Enhancements

- [ ] Authentication (JWT)
- [ ] Rate limiting
- [ ] Caching (Redis)
- [ ] Async database queries
- [ ] WebSocket support for streaming
- [ ] GraphQL endpoint
- [ ] API versioning (/v1/, /v2/)
