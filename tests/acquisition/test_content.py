from pathlib import Path

import pytest

from src.acquisition.content import (
    StaticArticleExtractor,
    canonicalize_url,
    content_hash,
    normalize_text,
    validate_language,
)
from src.acquisition.inspector import PageInspector
from src.acquisition.models import ExtractionStrategy, LanguageStatus

FIXTURES = Path(__file__).parents[1] / "fixtures" / "acquisition"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_canonicalization_removes_fragment_default_port_and_tracking_only():
    assert (
        canonicalize_url("HTTPS://Example.COM:443/a?utm_source=x&id=7&fbclid=z#part")
        == "https://example.com/a?id=7"
    )


@pytest.mark.parametrize(
    "url",
    ["file:///etc/passwd", "https://user:secret@example.com/article", "https://example.com:bad"],
)
def test_canonicalization_rejects_unsafe_or_malformed_identity_urls(url):
    with pytest.raises(ValueError):
        canonicalize_url(url)


def test_normalization_preserves_case_punctuation_and_deduplicates_paragraphs():
    source = "Habari  nzuri.\n\nHabari  nzuri.\n\nMaelezo\u200b zaidi!"
    assert normalize_text(source) == "Habari nzuri.\n\nMaelezo zaidi!"
    assert content_hash(normalize_text(source)) == content_hash(normalize_text(source))


def test_structural_and_json_ld_strategies_are_deterministic():
    semantic = fixture("semantic_sw.html")
    result = StaticArticleExtractor.extract(
        semantic, PageInspector.inspect_html("https://habari.example/x", semantic)
    )
    assert result.strategy == ExtractionStrategy.SEMANTIC_ARTICLE
    assert "Wanafunzi" in result.raw_text

    structured = fixture("jsonld_sw.html")
    result = StaticArticleExtractor.extract(
        structured, PageInspector.inspect_html("https://habari.example/afya", structured)
    )
    assert result.strategy == ExtractionStrategy.JSON_LD_ARTICLE
    assert result.author == "Asha Musa"


def test_language_uses_article_lexicon_and_rejects_misleading_lang_attribute():
    sw = validate_language(
        "Serikali na wananchi pia wamesema kuwa elimu ni muhimu kwa jamii.", html_language="sw"
    )
    assert sw.status == LanguageStatus.LIKELY_SWAHILI
    assert sw.is_acceptable
    english = validate_language(
        "The report is on the website and it is for the public.", html_language="sw"
    )
    assert english.status == LanguageStatus.LIKELY_NON_SWAHILI
    assert not english.is_acceptable
