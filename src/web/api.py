"""
Web Layer - REST API

FastAPI REST API for Swahili NLP RAG.

Endpoints:
- GET /terms/{term} - Lookup term
- GET /terms/search - Search terms
- POST /analyze/sentiment - Analyze sentiment
- GET /news/trends - Get sentiment trends
- GET /classify/bantu - Classify Bantu class
- POST /extract/root - Extract morphological root
- GET /health - Health check
"""

from collections.abc import Generator
from datetime import datetime
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from src.application.services.batch_processor import BatchProcessor
from src.application.services.export_formats import ConfidenceScorer
from src.application.services.text_processor import SwahiliTextProcessor
from src.application.services.url_analyzer import URLNewsAnalyzer
from src.domain.services.bantu_classifier import BantuClassifierService
from src.domain.services.root_extractor import RootExtractorService
from src.domain.value_objects import WordType
from src.infrastructure.database import get_session
from src.infrastructure.repositories.dictionary_repository import DictionaryRepository
from src.infrastructure.repositories.news_repository import NewsRepository
from src.infrastructure.repositories.term_repository import TermRepository

# Create FastAPI app
app = FastAPI(
    title="Swahili Linguistic Intelligence API",
    description="Research API for structured Swahili lexical and morphological analysis",
    version="v2.1.1-alpha",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Initialize batch processor
batch_processor = BatchProcessor(max_workers=3, delay_between_requests=2.0)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== SCHEMAS ====================


class TermResponse(BaseModel):
    """Response model for term lookup."""

    term: str
    root: str | None = None
    noun_class: str
    etymology: str
    word_type: str
    is_stopword: bool
    frequency_score: float

    model_config = ConfigDict(from_attributes=True)


class BantuClassificationRequest(BaseModel):
    """Request model for Bantu classification."""

    word: str = Field(..., min_length=1, max_length=100)
    word_type: str | None = "noun"


class BantuClassificationResponse(BaseModel):
    """Response model for Bantu classification."""

    word: str
    bantu_class: str
    description: str
    examples: list[tuple]


class RootExtractionRequest(BaseModel):
    """Request model for root extraction."""

    word: str = Field(..., min_length=1, max_length=100)
    word_type: str | None = None
    aggressive: bool = False


class RootExtractionResponse(BaseModel):
    """Response model for root extraction."""

    word: str
    root: str
    prefix: str | None = None
    suffix: str | None = None
    full_word: str


class SentimentAnalysisRequest(BaseModel):
    """Request model for sentiment analysis."""

    text: str = Field(..., min_length=1)


class SentimentAnalysisResponse(BaseModel):
    """Response model for sentiment analysis."""

    text: str
    polarity: float
    confidence: float
    label: str
    word_count: int


class NewsArticleResponse(BaseModel):
    """Response model for news article."""

    id: int
    content: str
    category: str
    date_published: datetime
    sentiment_label: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TrendDataPoint(BaseModel):
    """Data point for trends."""

    date: str
    positive: int
    negative: int
    neutral: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    database: str


class DictionaryEntryResponse(BaseModel):
    """Response model for dictionary entry."""

    term: str
    meaning: str
    english_translation: str | None = None
    synonyms: list[str] = Field(default_factory=list)
    usage_examples: list[str] = Field(default_factory=list)
    usage_context: str | None = None


class URLAnalysisRequest(BaseModel):
    """Request model for URL analysis."""

    url: str = Field(..., description="News article URL to analyze")


class SaveNewsRequest(BaseModel):
    """Request model for saving news article."""

    content: str = Field(..., min_length=10)
    category: str
    source_url: str | None = None
    sentiment_polarity: float | None = None
    sentiment_confidence: float | None = None
    sentiment_label: str | None = None


class URLAnalysisResponse(BaseModel):
    """Response model for URL analysis."""

    success: bool
    url: str | None = None
    text_preview: str | None = None
    word_count: int | None = None
    sentence_count: int | None = None
    unique_words: int | None = None
    vocabulary_richness: float | None = None
    top_keywords: list[dict] | None = None
    sentiment: dict | None = None
    language_stats: dict | None = None
    error: str | None = None


# ==================== DEPENDENCIES ====================


def get_api_db() -> Generator[Session, None, None]:
    """Request-scoped database session with commit/rollback handling."""
    db = get_session()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def get_term_repository(db: Session = Depends(get_api_db)) -> TermRepository:
    """Dependency for term repository."""
    return TermRepository(db)


async def get_news_repository(db: Session = Depends(get_api_db)) -> NewsRepository:
    """Dependency for news repository."""
    return NewsRepository(db)


async def get_dictionary_repository(
    db: Session = Depends(get_api_db),
) -> DictionaryRepository:
    """Dependency for dictionary repository."""
    return DictionaryRepository(db)


# ==================== ENDPOINTS ====================


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Swahili Linguistic Intelligence API",
        "version": "v2.1.1-alpha",
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "v2.1.1-alpha", "database": "connected"}


@app.get("/terms/{term}", response_model=TermResponse, tags=["Terms"])
async def get_term(term: str, repo: TermRepository = Depends(get_term_repository)):
    """
    Get term information by term string.

    Args:
        term: Swahili term to lookup

    Returns:
        Term information including Bantu class, etymology, etc.
    """
    term_entity = repo.find_by_term(term)

    if not term_entity:
        raise HTTPException(status_code=404, detail=f"Term '{term}' not found")

    return TermResponse(
        term=term_entity.term,
        root=term_entity.root.root if term_entity.root else None,
        noun_class=term_entity.noun_class.value,
        etymology=term_entity.etymology.value,
        word_type=term_entity.word_type.value,
        is_stopword=term_entity.is_stopword,
        frequency_score=term_entity.frequency_score,
    )


@app.get("/terms/search/", response_model=list[TermResponse], tags=["Terms"])
async def search_terms(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=100),
    repo: TermRepository = Depends(get_term_repository),
):
    """
    Search terms by prefix.

    Args:
        q: Search query
        limit: Maximum results

    Returns:
        List of matching terms
    """
    # Simple implementation - can be enhanced
    # For now, just check if term exists
    term_entity = repo.find_by_term(q)

    if not term_entity:
        return []

    return [
        TermResponse(
            term=term_entity.term,
            root=term_entity.root.root if term_entity.root else None,
            noun_class=term_entity.noun_class.value,
            etymology=term_entity.etymology.value,
            word_type=term_entity.word_type.value,
            is_stopword=term_entity.is_stopword,
            frequency_score=term_entity.frequency_score,
        )
    ]


@app.post(
    "/classify/bantu",
    response_model=BantuClassificationResponse,
    tags=["Classification"],
)
async def classify_bantu(request: BantuClassificationRequest):
    """
    Classify Bantu noun class of a word.

    Args:
        request: Word and word type

    Returns:
        Bantu classification with description and examples
    """
    service = BantuClassifierService()

    # Map string to WordType
    word_type = WordType.NOUN
    if request.word_type:
        word_type_map = {
            "noun": WordType.NOUN,
            "verb": WordType.VERB,
            "adjective": WordType.ADJECTIVE,
        }
        word_type = word_type_map.get(request.word_type.lower(), WordType.NOUN)

    # Classify
    bantu_class = service.infer_class(request.word, word_type)
    description = service.get_class_description(bantu_class)
    examples = service.get_typical_examples(bantu_class)

    return BantuClassificationResponse(
        word=request.word,
        bantu_class=bantu_class.value,
        description=description,
        examples=examples[:3],  # Return first 3 examples
    )


@app.post("/extract/root", response_model=RootExtractionResponse, tags=["Morphology"])
async def extract_root(request: RootExtractionRequest):
    """
    Extract morphological root from a word.

    Args:
        request: Word and extraction parameters

    Returns:
        Morphological root with prefix/suffix
    """
    service = RootExtractorService()

    # Map string to WordType if provided
    word_type = None
    if request.word_type:
        word_type_map = {
            "noun": WordType.NOUN,
            "verb": WordType.VERB,
        }
        word_type = word_type_map.get(request.word_type.lower())

    # Extract
    root = service.extract(
        request.word, word_type=word_type, aggressive=request.aggressive
    )

    return RootExtractionResponse(
        word=request.word,
        root=root.root,
        prefix=root.prefix,
        suffix=root.suffix,
        full_word=root.full_word,
    )


@app.post(
    "/analyze/sentiment", response_model=SentimentAnalysisResponse, tags=["Analysis"]
)
async def analyze_sentiment(request: SentimentAnalysisRequest):
    """
    Analyze sentiment of Swahili text.

    Args:
        request: Text to analyze

    Returns:
        Sentiment analysis with polarity and label
    """
    processor = SwahiliTextProcessor()

    # Simple sentiment analysis (placeholder)
    # In production, use actual sentiment model
    word_count = processor.count_words(request.text)

    # Placeholder sentiment
    polarity = 0.0
    confidence = 0.5
    label = "neutral"

    return SentimentAnalysisResponse(
        text=request.text[:100] + "..." if len(request.text) > 100 else request.text,
        polarity=polarity,
        confidence=confidence,
        label=label,
        word_count=word_count,
    )


@app.get("/news/articles", response_model=list[NewsArticleResponse], tags=["News"])
async def get_news_articles(
    category: str | None = None,
    limit: int = Query(10, ge=1, le=100),
    repo: NewsRepository = Depends(get_news_repository),
):
    """
    Get news articles, optionally filtered by category.

    Args:
        category: Filter by category
        limit: Maximum results

    Returns:
        List of news articles
    """
    if category:
        articles = repo.find_by_category(category, limit=limit)
    else:
        articles = repo.find_all(limit=limit)

    return [
        NewsArticleResponse(
            id=i,  # Placeholder ID
            content=article.content[:200] + "...",
            category=article.category,
            date_published=article.date_published or datetime.utcnow(),
            sentiment_label=article.sentiment_label,
        )
        for i, article in enumerate(articles, 1)
    ]


@app.post("/news/save", tags=["News"])
async def save_news_article(
    request: SaveNewsRequest, repo: NewsRepository = Depends(get_news_repository)
):
    """
    Save a news article to database.

    This endpoint allows you to store analyzed articles for later study.
    Used by the dashboard when "Save to database" is checked.

    Args:
        request: Article data including content, category, and sentiment

    Returns:
        Success message with article ID
    """
    try:
        from src.domain.entities import NewsArticle
        from src.domain.value_objects import SentimentScore

        # Create NewsArticle entity
        sentiment_score = None
        if request.sentiment_polarity is not None:
            try:
                sentiment_score = SentimentScore(
                    polarity=float(request.sentiment_polarity),
                    confidence=float(request.sentiment_confidence or 0.5),
                )
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail=f"Invalid sentiment values: {e!s}"
                )

        # Create article
        article = NewsArticle(
            content=str(request.content),
            category=str(request.category),
            source_url=str(request.source_url) if request.source_url else None,
        )

        # Add sentiment if provided
        if sentiment_score:
            article.analyze_sentiment(sentiment_score)

        # Save to database
        article_id = repo.save(article)

        if not article_id:
            raise HTTPException(
                status_code=500, detail="Failed to save article - no ID returned"
            )

        return {
            "success": True,
            "message": "Article saved successfully",
            "article_id": article_id,
            "category": request.category,
            "sentiment": request.sentiment_label,
        }

    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        # Log the full error for debugging
        import traceback

        error_detail = f"{type(e).__name__}: {e!s}"
        traceback_str = traceback.format_exc()
        print(f"ERROR in /news/save: {error_detail}")
        print(traceback_str)

        raise HTTPException(
            status_code=500, detail=f"Failed to save article: {error_detail}"
        )


@app.get("/news/trends", response_model=list[TrendDataPoint], tags=["News"])
async def get_sentiment_trends(repo: NewsRepository = Depends(get_news_repository)):
    """
    Get sentiment trends over time.

    Returns:
        Sentiment distribution by date
    """
    # Placeholder implementation
    # In production, aggregate by date from database
    return [
        TrendDataPoint(date="2024-01", positive=10, negative=5, neutral=15),
        TrendDataPoint(date="2024-02", positive=12, negative=3, neutral=18),
        TrendDataPoint(date="2024-03", positive=15, negative=4, neutral=20),
    ]


@app.get("/stats", tags=["Statistics"])
async def get_statistics(
    term_repo: TermRepository = Depends(get_term_repository),
    news_repo: NewsRepository = Depends(get_news_repository),
):
    """
    Get database statistics.

    Returns:
        Statistics about terms, news, etc.
    """
    term_count = term_repo.count()
    news_count = news_repo.count()

    return {
        "terms": term_count,
        "news_articles": news_count,
        "bantu_classes": len(BantuClassifierService.get_all_classes()),
    }


@app.get(
    "/dictionary/{term}", response_model=DictionaryEntryResponse, tags=["Dictionary"]
)
async def get_dictionary_entry(
    term: str, repo: DictionaryRepository = Depends(get_dictionary_repository)
):
    """
    Get dictionary entry for a Swahili term.

    Args:
        term: Swahili word to lookup

    Returns:
        Dictionary entry with meaning, translation, synonyms, examples
    """
    entry = repo.find_by_term_string(term)

    if not entry:
        raise HTTPException(
            status_code=404, detail=f"Dictionary entry for '{term}' not found"
        )

    return DictionaryEntryResponse(
        term=entry.term.term,
        meaning=entry.meaning,
        english_translation=entry.english_translation,
        synonyms=entry.synonyms,
        usage_examples=entry.usage_examples,
        usage_context=entry.usage_context,
    )


@app.get(
    "/dictionary/search/",
    response_model=list[DictionaryEntryResponse],
    tags=["Dictionary"],
)
async def search_dictionary(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    repo: DictionaryRepository = Depends(get_dictionary_repository),
):
    """
    Search dictionary by meaning.

    Args:
        q: Search query in Swahili
        limit: Maximum results

    Returns:
        List of matching dictionary entries
    """
    entries = repo.search_by_meaning(q, limit=limit)

    return [
        DictionaryEntryResponse(
            term=entry.term.term,
            meaning=entry.meaning,
            english_translation=entry.english_translation,
            synonyms=entry.synonyms,
            usage_examples=entry.usage_examples,
            usage_context=entry.usage_context,
        )
        for entry in entries
    ]


@app.post("/analyze/url", response_model=URLAnalysisResponse, tags=["Analysis"])
async def analyze_news_url(request: URLAnalysisRequest):
    """
    Analyze Swahili news article from URL.

    Fetches content from URL and performs:
    - Text extraction
    - Sentiment analysis
    - Keyword extraction
    - Language statistics

    Args:
        request: URL to analyze

    Returns:
        Comprehensive analysis results

    Examples:
        - BBC Swahili: https://www.bbc.com/swahili
        - Mwananchi: https://www.mwananchi.co.tz/
        - Daily News: https://dailynews.co.tz/
    """
    analyzer = URLNewsAnalyzer()
    result = analyzer.analyze_url(request.url)

    return URLAnalysisResponse(**result)


# ==================== BATCH PROCESSING ENDPOINTS ====================


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis."""

    urls: list[str] = Field(
        ..., min_length=1, max_length=1000, description="List of URLs to analyze"
    )


class BatchJobResponse(BaseModel):
    """Response model for batch job."""

    job_id: str
    status: str
    progress: int
    total_urls: int
    completed_urls: int
    message: str


class ExportRequest(BaseModel):
    """Request model for exporting results."""

    format: str = Field("json", description="Export format: json, conll, bio, tsv")
    create_splits: bool = Field(True, description="Create train/dev/test splits")
    include_confidence: bool = Field(True, description="Include confidence scores")


@app.post("/batch/create", response_model=BatchJobResponse, tags=["Batch Processing"])
async def create_batch_job(request: BatchAnalysisRequest):
    """
    Create a batch analysis job for multiple URLs.

    Process up to 1000 URLs in a single batch.
    Returns immediately with a job ID for tracking progress.

    Args:
        request: List of URLs to analyze

    Returns:
        Job ID and initial status
    """
    job_id = batch_processor.create_job(request.urls)

    return BatchJobResponse(
        job_id=job_id,
        status="pending",
        progress=0,
        total_urls=len(request.urls),
        completed_urls=0,
        message=f"Batch job created with {len(request.urls)} URLs",
    )


@app.post(
    "/batch/{job_id}/start", response_model=BatchJobResponse, tags=["Batch Processing"]
)
async def start_batch_job(job_id: str, background_tasks: BackgroundTasks):
    """
    Start processing a batch job in the background.

    Args:
        job_id: Job ID from create_batch_job

    Returns:
        Updated job status
    """
    # Add to background tasks
    background_tasks.add_task(batch_processor.process_batch, job_id)

    job_status = batch_processor.get_job_status(job_id)

    if not job_status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return BatchJobResponse(
        job_id=job_id,
        status="running",
        progress=job_status["progress"],
        total_urls=job_status["total_urls"],
        completed_urls=job_status["completed_urls"],
        message="Batch job started",
    )


@app.get(
    "/batch/{job_id}/status", response_model=BatchJobResponse, tags=["Batch Processing"]
)
async def get_batch_status(job_id: str):
    """
    Get status of a batch job.

    Args:
        job_id: Job ID

    Returns:
        Current job status and progress
    """
    job_status = batch_processor.get_job_status(job_id)

    if not job_status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return BatchJobResponse(
        job_id=job_id,
        status=job_status["status"],
        progress=job_status["progress"],
        total_urls=job_status["total_urls"],
        completed_urls=job_status["completed_urls"],
        message=f"{job_status['completed_urls']}/{job_status['total_urls']} completed",
    )


@app.post("/batch/{job_id}/export", tags=["Batch Processing"])
async def export_batch_results(job_id: str, request: ExportRequest):
    """
    Export batch results in research-ready format.

    Supports:
    - JSON (research-ready with confidence scores)
    - CoNLL (NER standard format)
    - BIO (sequence labeling format)
    - TSV (SpaCy training format)

    Can automatically create train/dev/test splits (70/15/15).

    Args:
        job_id: Job ID
        request: Export configuration

    Returns:
        Download URLs for exported files
    """
    from pathlib import Path

    # Check job exists and is completed
    job_status = batch_processor.get_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    if job_status["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Job is not completed (status: {job_status['status']})",
        )

    # Export results
    output_dir = Path("data/exports") / job_id

    try:
        file_paths = batch_processor.export_results(
            job_id,
            output_dir,
            format=request.format,
            create_splits=request.create_splits,
        )

        # Convert paths to download URLs
        downloads = {}
        for split_name, file_path in file_paths.items():
            rel_path = file_path.relative_to("data/exports")
            downloads[split_name] = f"/downloads/{rel_path}"

        return {
            "success": True,
            "job_id": job_id,
            "format": request.format,
            "downloads": downloads,
            "message": f"Exported {job_status['completed_urls']} documents",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e!s}")


# ==================== RESEARCH FEATURES ====================


class ConfidenceRequest(BaseModel):
    """Request for adding confidence scores."""

    text: str
    sentiment_result: dict[str, Any]


@app.post("/research/add_confidence", tags=["Research Features"])
async def add_confidence_scores(request: ConfidenceRequest):
    """
    Add confidence scores to analysis results.

    Useful for filtering low-quality predictions and active learning.

    Args:
        request: Text and sentiment result

    Returns:
        Results with confidence scores
    """
    sentiment = request.sentiment_result
    words = request.text.split()

    confidence = ConfidenceScorer.calculate_sentiment_confidence(
        polarity=sentiment.get("polarity", 0),
        positive_words=sentiment.get("positive_words_found", 0),
        negative_words=sentiment.get("negative_words_found", 0),
        total_words=len(words),
    )

    return {
        **sentiment,
        "confidence": confidence,
        "quality": "high"
        if confidence > 0.7
        else "medium"
        if confidence > 0.5
        else "low",
    }


# ==================== ERROR HANDLERS ====================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return {"error": exc.detail, "status_code": exc.status_code}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return {"error": "Internal server error", "detail": str(exc)}


# Run with: uvicorn src.web.api:app --reload
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
