"""Deterministic tests for URL safety, extraction, and baseline analysis."""

from unittest.mock import Mock

import pytest

from src.application.services.url_analyzer import URLNewsAnalyzer


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/article",
        "http://localhost/article",
        "http://user:secret@example.com/article",
    ],
)
def test_public_url_policy_rejects_unsupported_or_local_urls(url):
    with pytest.raises(ValueError):
        URLNewsAnalyzer.validate_public_url(url)


def test_public_url_policy_rejects_private_resolved_address(monkeypatch):
    monkeypatch.setattr(
        "src.application.services.url_analyzer.socket.getaddrinfo",
        lambda *_args, **_kwargs: [(2, 1, 6, "", ("10.0.0.8", 80))],
    )

    with pytest.raises(ValueError, match="non-public"):
        URLNewsAnalyzer.validate_public_url("https://news.example/article")


def test_fetch_revalidates_redirect_target(monkeypatch):
    monkeypatch.setattr(
        "src.application.services.url_analyzer.socket.getaddrinfo",
        lambda *_args, **_kwargs: [(2, 1, 6, "", ("93.184.216.34", 443))],
    )
    redirect = Mock(status_code=302, headers={"Location": "http://127.0.0.1/admin"})
    monkeypatch.setattr("src.application.services.url_analyzer.requests.get", Mock(return_value=redirect))

    assert URLNewsAnalyzer().fetch_url("https://example.com/article") is None


def test_fetch_accepts_bounded_html_response(monkeypatch):
    monkeypatch.setattr(
        "src.application.services.url_analyzer.socket.getaddrinfo",
        lambda *_args, **_kwargs: [(2, 1, 6, "", ("93.184.216.34", 443))],
    )
    response = Mock(
        status_code=200,
        headers={"Content-Type": "text/html; charset=utf-8"},
        content=b"<html><p>Habari za Kiswahili</p></html>",
        encoding="utf-8",
        apparent_encoding="utf-8",
        text="<html><p>Habari za Kiswahili</p></html>",
    )
    response.raise_for_status.return_value = None
    monkeypatch.setattr("src.application.services.url_analyzer.requests.get", Mock(return_value=response))

    assert "Habari" in URLNewsAnalyzer().fetch_url("https://example.com/article")


def test_extract_text_prefers_paragraphs_and_removes_boilerplate():
    html = """
    <html lang="sw"><body><header>Navigation</header><article>
      <p>Sentensi ya kwanza ya habari.</p><p>Sentensi ya pili ya habari.</p>
    </article><footer>Copyright</footer></body></html>
    """

    text = URLNewsAnalyzer().extract_text(html)

    assert text == "Sentensi ya kwanza ya habari. Sentensi ya pili ya habari."
    assert "Navigation" not in text


def test_sentiment_is_documented_lexicon_baseline_not_economic_judgment():
    analyzer = URLNewsAnalyzer()
    result = analyzer.analyze_text("Uchumi una maendeleo na faida.")

    assert result["sentiment"]["negative_words_found"] == 0
    assert result["sentiment"]["label"] == "positive"
