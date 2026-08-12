"""
Stable local smoke tests for alpha API readiness.
"""

import pytest


@pytest.mark.smoke
def test_health_endpoint_is_available(client):
    """`/health` should boot and report alpha version metadata."""
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["version"] == "v2.1.1-alpha"
    assert payload["database"] == "connected"


@pytest.mark.smoke
def test_term_lookup_returns_expected_structure(client):
    """`/terms/{term}` should return a stable term payload."""
    response = client.get("/terms/mtu")

    assert response.status_code == 200
    payload = response.json()

    assert payload["term"] == "mtu"
    assert payload["root"] == "tu"
    assert payload["noun_class"] == "1/2"
    assert payload["etymology"] == "bantu"
    assert payload["word_type"] == "noun"
    assert payload["is_stopword"] is False
    assert isinstance(payload["frequency_score"], (int, float))


@pytest.mark.smoke
def test_term_search_returns_list_shape(client):
    """`/terms/search/` should return a list of matching terms."""
    response = client.get("/terms/search/", params={"q": "mtu", "limit": 10})

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload, list)
    assert len(payload) == 1
    assert payload[0]["term"] == "mtu"


@pytest.mark.smoke
def test_bantu_classification_returns_basic_result(client):
    """`/classify/bantu` should classify a typical noun."""
    response = client.post(
        "/classify/bantu",
        json={"word": "kitabu", "word_type": "noun"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["word"] == "kitabu"
    assert "bantu_class" in payload
    assert "description" in payload
    assert isinstance(payload["examples"], list)


@pytest.mark.smoke
def test_root_extraction_returns_components(client):
    """`/extract/root` should expose the extracted root structure."""
    response = client.post(
        "/extract/root",
        json={"word": "ninasoma", "word_type": "verb", "aggressive": False},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["word"] == "ninasoma"
    assert payload["root"] == "som"
    assert payload["prefix"] == "nina"
    assert payload["suffix"] == "a"
    assert payload["full_word"] == "ninasoma"


@pytest.mark.smoke
def test_dictionary_lookup_returns_expected_structure(client):
    """`/dictionary/{term}` should return dictionary data for a known term."""
    response = client.get("/dictionary/mtu")

    assert response.status_code == 200
    payload = response.json()

    assert payload["term"] == "mtu"
    assert payload["meaning"] == "binadamu, mwanadamu"
    assert payload["english_translation"] == "person, human being"
    assert isinstance(payload["synonyms"], list)
    assert isinstance(payload["usage_examples"], list)
    assert payload["usage_context"] == "formal"


@pytest.mark.smoke
def test_news_save_accepts_local_article_payload(client):
    """`/news/save` should accept a minimal article payload and return success."""
    response = client.post(
        "/news/save",
        json={
            "content": "Rais wa Tanzania ametembelea Zanzibar kwa mkutano rasmi.",
            "category": "Politics",
            "source_url": "https://example.com/article",
            "sentiment_polarity": 0.2,
            "sentiment_confidence": 0.8,
            "sentiment_label": "positive",
        },
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["message"] == "Article saved successfully"
    assert payload["article_id"] == 1
    assert payload["category"] == "Politics"
    assert payload["sentiment"] == "positive"


@pytest.mark.smoke
def test_news_trends_returns_list_of_points(client):
    """`/news/trends` should return a list of trend points."""
    response = client.get("/news/trends")

    assert response.status_code == 200
    payload = response.json()

    assert isinstance(payload, list)
    assert len(payload) >= 1
    first_point = payload[0]
    assert set(first_point.keys()) == {"date", "positive", "negative", "neutral"}


@pytest.mark.smoke
def test_stats_returns_basic_counts(client):
    """`/stats` should expose alpha-friendly count metrics."""
    response = client.get("/stats")

    assert response.status_code == 200
    payload = response.json()

    assert "terms" in payload
    assert "news_articles" in payload
    assert "bantu_classes" in payload
    assert payload["terms"] == 1
    assert isinstance(payload["news_articles"], int)
    assert payload["bantu_classes"] >= 1


@pytest.mark.smoke
def test_url_analysis_endpoint_is_stable_with_stubbed_analyzer(client, monkeypatch):
    """`/analyze/url` should return the documented response shape without network access."""
    from src.web import api as api_module

    class StubAnalyzer:
        def analyze_url(self, url: str):
            return {
                "success": True,
                "url": url,
                "text_preview": "Habari za leo kuhusu uchumi wa Tanzania.",
                "word_count": 6,
                "sentence_count": 1,
                "unique_words": 6,
                "vocabulary_richness": 1.0,
                "top_keywords": [{"word": "uchumi", "count": 1}],
                "sentiment": {
                    "polarity": 0.1,
                    "confidence": 0.7,
                    "label": "positive",
                },
                "language_stats": {
                    "total_tokens": 6,
                    "filtered_tokens": 4,
                    "stopwords_removed": 2,
                },
                "error": None,
            }

    monkeypatch.setattr(api_module, "URLNewsAnalyzer", StubAnalyzer)

    response = client.post(
        "/analyze/url",
        json={"url": "https://example.com/swahili-article"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["success"] is True
    assert payload["url"] == "https://example.com/swahili-article"
    assert isinstance(payload["top_keywords"], list)
    assert isinstance(payload["sentiment"], dict)
    assert isinstance(payload["language_stats"], dict)
