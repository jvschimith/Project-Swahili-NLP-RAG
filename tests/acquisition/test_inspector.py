"""Static fixture tests for page-inspection evidence."""

from src.acquisition.inspector import PageInspector

ARTICLE_HTML = """
<html lang="sw"><head>
  <title>Habari ya Elimu</title>
  <link rel="canonical" href="/habari/elimu">
  <link rel="alternate" type="application/rss+xml" href="/rss.xml">
  <meta property="og:title" content="Habari ya Elimu">
  <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"NewsArticle","headline":"Habari ya Elimu"}
  </script>
</head><body><main><article>
  <p>Wanafunzi wanasoma darasani leo.</p>
  <p>Walimu wameandaa vitabu vipya.</p>
</article><a href="/sitemap.xml">Sitemap</a></main></body></html>
"""


def test_inspector_reports_structured_and_semantic_article_signals():
    result = PageInspector.inspect_html("https://example.org/original", ARTICLE_HTML)

    assert result.canonical_url == "https://example.org/habari/elimu"
    assert result.html_language == "sw"
    assert result.title == "Habari ya Elimu"
    assert result.json_ld_types == ["NewsArticle"]
    assert result.open_graph["og:title"] == "Habari ya Elimu"
    assert result.has_article is True
    assert result.article_paragraph_count == 2
    assert result.feed_urls == ["https://example.org/rss.xml"]
    assert result.possible_sitemap_urls == ["https://example.org/sitemap.xml"]
    assert result.recommended_strategy == "structured_data_then_article"


def test_inspector_ignores_malformed_json_ld():
    result = PageInspector.inspect_html(
        "https://example.org/",
        "<html><script type='application/ld+json'>{broken</script><p>One</p></html>",
    )

    assert result.json_ld_types == []
    assert result.recommended_strategy == "insufficient_static_evidence"


def test_inspector_marks_script_heavy_text_light_page_as_dynamic_fallback():
    scripts = "".join("<script src='/app.js'></script>" for _ in range(12))
    result = PageInspector.inspect_html(
        "https://example.org/app", f"<html><body>{scripts}</body></html>"
    )

    assert result.likely_dynamic is True
    assert result.recommended_strategy == "rendered_dom_fallback"
