"""Static article extraction, normalization, language validation and URLs."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import ClassVar
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from bs4 import BeautifulSoup, Tag

from .inspector import PageInspectionResult
from .models import (
    ExtractionResult,
    ExtractionStrategy,
    LanguageStatus,
    LanguageValidationResult,
)

TRACKING_PARAMETERS = {"fbclid", "gclid", "mc_cid", "mc_eid"}
SWAHILI_FUNCTION_WORDS = {
    "ama",
    "ambayo",
    "bila",
    "cha",
    "hii",
    "hivyo",
    "huyo",
    "ili",
    "katika",
    "kwa",
    "lakini",
    "na",
    "ni",
    "pia",
    "sana",
    "wa",
    "wakati",
    "ya",
    "yake",
    "yenye",
    "za",
    "zaidi",
}
ENGLISH_FUNCTION_WORDS = {
    "and",
    "are",
    "as",
    "at",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "with",
}


def canonicalize_url(url: str) -> str:
    """Normalize URL identity without deleting content-bearing parameters."""
    parsed = urlsplit(url)
    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Canonical URL must be an absolute HTTP(S) URL")
    if parsed.username or parsed.password:
        raise ValueError("Canonical URL must not contain credentials")
    hostname = (parsed.hostname or "").lower().rstrip(".")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Canonical URL contains an invalid port") from exc
    netloc = hostname
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{hostname}:{port}"
    query = urlencode(
        sorted(
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if not key.lower().startswith("utm_") and key.lower() not in TRACKING_PARAMETERS
        )
    )
    return urlunsplit((scheme, netloc, parsed.path or "/", query, ""))


def normalize_text(text: str) -> str:
    """Normalize safely while retaining case, punctuation and paragraphs."""
    text = unicodedata.normalize("NFC", text).replace("\u200b", "").replace("\ufeff", "")
    paragraphs: list[str] = []
    seen: set[str] = set()
    for paragraph in re.split(r"\n\s*\n|\r?\n", text):
        cleaned = re.sub(r"[ \t]+", " ", paragraph).strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            paragraphs.append(cleaned)
    return "\n\n".join(paragraphs)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def validate_language(
    text: str, *, html_language: str | None = None, metadata_language: str | None = None
) -> LanguageValidationResult:
    """Return a documented heuristic score, not a calibrated probability."""
    tokens = re.findall(r"[^\W\d_]+", text.lower(), flags=re.UNICODE)
    sw_count = sum(token in SWAHILI_FUNCTION_WORDS for token in tokens)
    en_count = sum(token in ENGLISH_FUNCTION_WORDS for token in tokens)
    declared_sw = any(
        value and value.lower().split("-")[0] == "sw"
        for value in (html_language, metadata_language)
    )
    evidence = [f"swahili_function_words={sw_count}", f"english_function_words={en_count}"]
    if declared_sw:
        evidence.append("swahili_language_metadata")
    lexical_total = sw_count + en_count
    sw_ratio = sw_count / lexical_total if lexical_total else 0.0
    density = sw_count / max(len(tokens), 1)
    score = min(1.0, (0.15 if declared_sw else 0.0) + sw_ratio * 0.55 + density * 3)
    language: str | None
    if sw_count >= 4 and sw_ratio >= 0.65:
        status = LanguageStatus.LIKELY_SWAHILI
        acceptable = True
        language = "sw"
    elif sw_count >= 4 and en_count >= 4:
        status = LanguageStatus.MULTILINGUAL
        acceptable = sw_ratio >= 0.45
        language = "sw" if acceptable else None
    elif en_count >= 4 and sw_count < 3:
        status = LanguageStatus.LIKELY_NON_SWAHILI
        acceptable = False
        language = "en"
    else:
        status = LanguageStatus.UNCERTAIN
        acceptable = False
        language = None
    return LanguageValidationResult(language, round(score, 3), tuple(evidence), status, acceptable)


class StaticArticleExtractor:
    """Choose and execute a deterministic structure-first extraction strategy."""

    ARTICLE_TYPES: ClassVar[set[str]] = {
        "Article",
        "NewsArticle",
        "ReportageNewsArticle",
        "BlogPosting",
    }

    @classmethod
    def extract(cls, html: str, inspection: PageInspectionResult) -> ExtractionResult:
        soup = BeautifulSoup(html, "html.parser")
        structured = cls._structured_article(soup)
        if structured and structured.get("articleBody"):
            return ExtractionResult(
                ExtractionStrategy.JSON_LD_ARTICLE,
                str(structured["articleBody"]),
                cls._string(structured.get("headline") or structured.get("name")),
                cls._author(structured.get("author")),
                cls._string(structured.get("datePublished")),
                {
                    "json_ld_type": structured.get("@type"),
                    "in_language": structured.get("inLanguage"),
                },
            )
        article = soup.find("article")
        if article and len(article.find_all("p")) >= 2:
            return cls._from_container(
                article, ExtractionStrategy.SEMANTIC_ARTICLE, inspection.title
            )
        main = soup.find("main")
        if main and len(main.find_all("p")) >= 2:
            return cls._from_container(main, ExtractionStrategy.MAIN_CONTENT, inspection.title)
        paragraphs = cls._paragraph_texts(soup)
        if len(paragraphs) >= 2:
            return ExtractionResult(
                ExtractionStrategy.GENERIC_PARAGRAPH, "\n\n".join(paragraphs), inspection.title
            )
        strategy = (
            ExtractionStrategy.DYNAMIC_BROWSER_REQUIRED
            if inspection.likely_dynamic
            else ExtractionStrategy.UNSUPPORTED
        )
        return ExtractionResult(strategy, "", inspection.title)

    @classmethod
    def _from_container(
        cls, container: Tag, strategy: ExtractionStrategy, title: str | None
    ) -> ExtractionResult:
        return ExtractionResult(strategy, "\n\n".join(cls._paragraph_texts(container)), title)

    @staticmethod
    def _paragraph_texts(container: BeautifulSoup | Tag) -> list[str]:
        output: list[str] = []
        seen: set[str] = set()
        for node in container.find_all("p"):
            text = node.get_text(" ", strip=True)
            if len(text) >= 20 and text not in seen:
                output.append(text)
                seen.add(text)
        return output

    @classmethod
    def _structured_article(cls, soup: BeautifulSoup) -> dict[str, object] | None:
        candidates: list[dict[str, object]] = []
        for element in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                cls._collect_objects(json.loads(element.string or element.get_text()), candidates)
            except (TypeError, json.JSONDecodeError):
                continue
        return next((item for item in candidates if cls._types(item) & cls.ARTICLE_TYPES), None)

    @classmethod
    def _collect_objects(cls, value: object, output: list[dict[str, object]]) -> None:
        if isinstance(value, dict):
            output.append(value)
            for child in value.values():
                cls._collect_objects(child, output)
        elif isinstance(value, list):
            for child in value:
                cls._collect_objects(child, output)

    @staticmethod
    def _types(value: dict[str, object]) -> set[str]:
        item = value.get("@type")
        if isinstance(item, str):
            return {item}
        return (
            {entry for entry in item if isinstance(entry, str)} if isinstance(item, list) else set()
        )

    @staticmethod
    def _string(value: object) -> str | None:
        return value.strip() if isinstance(value, str) and value.strip() else None

    @classmethod
    def _author(cls, value: object) -> str | None:
        if isinstance(value, str):
            return cls._string(value)
        if isinstance(value, dict):
            return cls._string(value.get("name"))
        if isinstance(value, list):
            names = [name for item in value if (name := cls._author(item))]
            return ", ".join(names) or None
        return None
