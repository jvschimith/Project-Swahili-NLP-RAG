from pathlib import Path

import pytest

from src.acquisition.discovery import discover_feed_urls, discover_sitemap_urls

FIXTURES = Path(__file__).parents[1] / "fixtures" / "acquisition"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_feed_discovery_is_bounded_and_domain_filtered():
    found = discover_feed_urls(
        "https://habari.example/feed",
        fixture("feed.xml"),
        max_urls=5,
        allowed_domains={"habari.example"},
    )
    assert [item.url for item in found] == ["https://habari.example/elimu"]
    assert found[0].title == "Elimu"


def test_sitemap_discovery_obeys_limit():
    found = discover_sitemap_urls(
        "https://habari.example/sitemap.xml", fixture("sitemap.xml"), max_urls=2
    )
    assert [item.url for item in found] == [
        "https://habari.example/elimu",
        "https://habari.example/afya",
    ]


@pytest.mark.parametrize("xml", ["<rss><broken>", "<!DOCTYPE rss><rss />"])
def test_discovery_rejects_malformed_or_declared_xml(xml):
    with pytest.raises(ValueError):
        discover_feed_urls("https://habari.example/feed", xml)
