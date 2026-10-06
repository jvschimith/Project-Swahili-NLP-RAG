"""Evidence-based inspection of static HTML before article extraction."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from typing import ClassVar
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


@dataclass(frozen=True)
class PageInspectionResult:
    """Observable page signals and a heuristic extraction recommendation."""

    url: str
    canonical_url: str | None
    html_language: str | None
    title: str | None
    json_ld_types: list[str] = field(default_factory=list)
    open_graph: dict[str, str] = field(default_factory=dict)
    has_article: bool = False
    has_main: bool = False
    paragraph_count: int = 0
    article_paragraph_count: int = 0
    link_count: int = 0
    feed_urls: list[str] = field(default_factory=list)
    possible_sitemap_urls: list[str] = field(default_factory=list)
    script_count: int = 0
    likely_dynamic: bool = False
    recommended_strategy: str = "generic_static"
    explanation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


class PageInspector:
    """Inspect supplied HTML without performing network access."""

    ARTICLE_TYPES: ClassVar[set[str]] = {
        "Article",
        "NewsArticle",
        "ReportageNewsArticle",
        "BlogPosting",
    }

    @classmethod
    def inspect_html(cls, url: str, html: str) -> PageInspectionResult:
        soup = BeautifulSoup(html, "html.parser")
        canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
        canonical_href = cls._attribute(canonical, "href")
        canonical_url = urljoin(url, canonical_href) if canonical_href else None
        html_language = cls._attribute(soup.html, "lang")
        title = soup.title.get_text(" ", strip=True) if soup.title else None

        json_ld_types: set[str] = set()
        for element in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                payload = json.loads(element.string or element.get_text())
            except (TypeError, json.JSONDecodeError):
                continue
            cls._collect_json_ld_types(payload, json_ld_types)

        open_graph = {}
        for meta in soup.find_all("meta"):
            prop = cls._attribute(meta, "property") or cls._attribute(meta, "name")
            content = cls._attribute(meta, "content")
            if prop and prop.startswith("og:") and content:
                open_graph[prop] = content.strip()

        article = soup.find("article")
        main = soup.find("main")
        paragraphs = soup.find_all("p")
        article_paragraphs = article.find_all("p") if article else []
        links = soup.find_all("a", href=True)
        feeds: list[str] = []
        for link in soup.find_all("link", href=True):
            href = cls._attribute(link, "href")
            content_type = cls._attribute(link, "type")
            if href and content_type and content_type.lower() in {
                "application/rss+xml",
                "application/atom+xml",
            }:
                feeds.append(urljoin(url, href))
        sitemap_urls: list[str] = []
        for link in soup.find_all("a", href=True):
            href = cls._attribute(link, "href")
            if href and "sitemap" in href.lower():
                sitemap_urls.append(urljoin(url, href))
        scripts = soup.find_all("script")
        body_text = soup.get_text(" ", strip=True)
        likely_dynamic = len(scripts) >= 12 and len(body_text) < 500 and len(paragraphs) < 3

        strategy, explanation = cls._recommend(
            json_ld_types=json_ld_types,
            has_article=article is not None,
            article_paragraph_count=len(article_paragraphs),
            paragraph_count=len(paragraphs),
            likely_dynamic=likely_dynamic,
        )
        return PageInspectionResult(
            url=url,
            canonical_url=canonical_url,
            html_language=html_language.lower() if html_language else None,
            title=title,
            json_ld_types=sorted(json_ld_types),
            open_graph=open_graph,
            has_article=article is not None,
            has_main=main is not None,
            paragraph_count=len(paragraphs),
            article_paragraph_count=len(article_paragraphs),
            link_count=len(links),
            feed_urls=feeds,
            possible_sitemap_urls=sitemap_urls,
            script_count=len(scripts),
            likely_dynamic=likely_dynamic,
            recommended_strategy=strategy,
            explanation=explanation,
        )

    @staticmethod
    def _attribute(element: object, name: str) -> str | None:
        if not isinstance(element, Tag):
            return None
        value = element.get(name)
        return value if isinstance(value, str) else None

    @classmethod
    def _collect_json_ld_types(cls, value, output: set[str]) -> None:
        if isinstance(value, dict):
            type_value = value.get("@type")
            if isinstance(type_value, str):
                output.add(type_value)
            elif isinstance(type_value, list):
                output.update(item for item in type_value if isinstance(item, str))
            for child in value.values():
                cls._collect_json_ld_types(child, output)
        elif isinstance(value, list):
            for child in value:
                cls._collect_json_ld_types(child, output)

    @classmethod
    def _recommend(
        cls,
        *,
        json_ld_types: set[str],
        has_article: bool,
        article_paragraph_count: int,
        paragraph_count: int,
        likely_dynamic: bool,
    ) -> tuple[str, str]:
        if cls.ARTICLE_TYPES.intersection(json_ld_types):
            return (
                "structured_data_then_article",
                "Article JSON-LD is present; validate it against semantic HTML.",
            )
        if has_article and article_paragraph_count >= 2:
            return (
                "semantic_article",
                "An <article> container contains multiple paragraphs.",
            )
        if paragraph_count >= 3:
            return (
                "generic_static",
                "Static HTML contains a usable paragraph structure but no strong article container.",
            )
        if likely_dynamic:
            return (
                "rendered_dom_fallback",
                "Script-heavy HTML has little static text; inspect public data requests before rendering.",
            )
        return (
            "insufficient_static_evidence",
            "The supplied HTML does not contain enough article evidence.",
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a public page's static extraction signals"
    )
    parser.add_argument("url")
    args = parser.parse_args()

    from src.application.services.url_analyzer import URLNewsAnalyzer

    fetched = URLNewsAnalyzer().fetch_result(args.url)
    if fetched is None:
        parser.error("page could not be fetched under the public URL policy")
    print(
        json.dumps(
            {
                "requested_url": fetched.requested_url,
                "final_url": fetched.final_url,
                "status_code": fetched.status_code,
                "content_type": fetched.content_type,
                "retrieved_at": fetched.retrieved_at.isoformat(),
                "inspection": PageInspector.inspect_html(fetched.final_url, fetched.html).to_dict(),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
