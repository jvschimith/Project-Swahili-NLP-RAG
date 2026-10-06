"""Bounded offline parsing of RSS/Atom and XML sitemap discovery documents."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from .content import canonicalize_url

MAX_DISCOVERY_BYTES = 2 * 1024 * 1024


@dataclass(frozen=True)
class DiscoveredURL:
    url: str
    source_url: str
    kind: str
    title: str | None = None
    published_at: str | None = None


def _allowed(url: str, allowed_domains: set[str] | None) -> bool:
    return allowed_domains is None or (urlsplit(url).hostname or "").lower() in allowed_domains


def discover_page_urls(
    seed_url: str,
    html: str,
    *,
    max_urls: int,
    allowed_domains: set[str],
) -> list[DiscoveredURL]:
    """Find bounded HTTP(S) link candidates from one static seed page.

    This function performs no recursive fetching. Requiring an explicit domain
    allowlist prevents a seed page from silently expanding crawl scope.
    """
    if max_urls < 1:
        raise ValueError("max_urls must be positive")
    normalized_domains = {domain.lower().rstrip(".") for domain in allowed_domains if domain}
    if not normalized_domains:
        raise ValueError("allowed_domains must contain at least one domain")

    results: list[DiscoveredURL] = []
    seen: set[str] = set()
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.find_all("a", href=True):
        href = link.get("href")
        if not isinstance(href, str):
            continue
        target = urljoin(seed_url, href)
        parsed = urlsplit(target)
        if parsed.scheme.lower() not in {"http", "https"} or parsed.username or parsed.password:
            continue
        target = canonicalize_url(target)
        if target in seen or not _allowed(target, normalized_domains):
            continue
        seen.add(target)
        title = link.get_text(" ", strip=True) or None
        results.append(DiscoveredURL(target, seed_url, "page_link", title))
        if len(results) >= max_urls:
            break
    return results


def _parse_xml(xml: str) -> ElementTree.Element:
    """Parse bounded XML while refusing document-type/entity declarations."""
    if len(xml.encode("utf-8")) > MAX_DISCOVERY_BYTES:
        raise ValueError("Discovery XML exceeds the size limit")
    lowered = xml.lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        raise ValueError("XML document declarations are not supported")
    try:
        return ElementTree.fromstring(xml)
    except ElementTree.ParseError as exc:
        raise ValueError("Malformed discovery XML") from exc


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child_text(element: ElementTree.Element, names: set[str]) -> str | None:
    child = next((item for item in element if _local_name(item.tag) in names), None)
    return child.text.strip() if child is not None and child.text else None


def discover_feed_urls(
    feed_url: str, xml: str, *, max_urls: int = 50, allowed_domains: set[str] | None = None
) -> list[DiscoveredURL]:
    """Parse bounded RSS/Atom candidates; final pages still require inspection."""
    root = _parse_xml(xml)
    results: list[DiscoveredURL] = []
    entries = (item for item in root.iter() if _local_name(item.tag) in {"item", "entry"})
    for entry in entries:
        link = next((item for item in entry if _local_name(item.tag) == "link"), None)
        href = link.get("href") if link is not None else None
        target = href or (link.text.strip() if link is not None and link.text else "")
        if not target:
            continue
        target = urljoin(feed_url, target)
        if not _allowed(target, allowed_domains):
            continue
        results.append(
            DiscoveredURL(
                target,
                feed_url,
                "feed",
                _child_text(entry, {"title"}),
                _child_text(entry, {"pubDate", "published", "updated"}),
            )
        )
        if len(results) >= max_urls:
            break
    return results


def discover_sitemap_urls(
    sitemap_url: str, xml: str, *, max_urls: int = 100, allowed_domains: set[str] | None = None
) -> list[DiscoveredURL]:
    """Parse URL entries and bounded child-sitemap pointers without recursion."""
    root = _parse_xml(xml)
    kind = "sitemap" if _local_name(root.tag) == "urlset" else "sitemap_index"
    results = []
    for location in (item for item in root.iter() if _local_name(item.tag) == "loc"):
        target = urljoin(sitemap_url, (location.text or "").strip())
        if target and _allowed(target, allowed_domains):
            results.append(DiscoveredURL(target, sitemap_url, kind))
        if len(results) >= max_urls:
            break
    return results
