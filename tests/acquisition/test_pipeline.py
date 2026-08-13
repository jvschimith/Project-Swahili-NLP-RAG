from datetime import datetime, timezone
from pathlib import Path

from src.acquisition.pipeline import AcquisitionPipeline
from src.acquisition.storage import CorpusStore

FIXTURES = Path(__file__).parents[1] / "fixtures" / "acquisition"
NOW = datetime(2026, 8, 12, 12, tzinfo=timezone.utc)


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_end_to_end_storage_manifest_and_same_url_idempotence(tmp_path):
    pipeline = AcquisitionPipeline(CorpusStore(tmp_path / "corpus"))
    first = pipeline.process_html(
        "https://habari.example/elimu?utm_source=x", fixture("semantic_sw.html"), retrieved_at=NOW
    )
    second = pipeline.process_html(
        "https://habari.example/elimu?utm_source=y", fixture("semantic_sw.html"), retrieved_at=NOW
    )
    assert first.status == "stored"
    assert first.document is not None
    assert first.document.canonical_url == "https://habari.example/elimu"
    assert first.document.provenance["acquisition_version"] == "web-corpus-v1"
    assert second.status == "duplicate"
    assert second.duplicate_reason == "canonical_url"
    assert len(pipeline.store.list_manifest()) == 1


def test_same_content_at_different_url_deduplicates_by_hash(tmp_path):
    pipeline = AcquisitionPipeline(CorpusStore(tmp_path))
    html = fixture("semantic_sw.html").replace(
        '<link rel="canonical" href="https://habari.example/elimu?utm_source=feed">', ""
    )
    assert (
        pipeline.process_html("https://habari.example/one", html, retrieved_at=NOW).status
        == "stored"
    )
    duplicate = pipeline.process_html("https://habari.example/two", html, retrieved_at=NOW)
    assert duplicate.duplicate_reason == "content_hash"


def test_changed_content_same_canonical_url_is_not_silently_overwritten(tmp_path):
    pipeline = AcquisitionPipeline(CorpusStore(tmp_path))
    html = fixture("semantic_sw.html")
    pipeline.process_html("https://habari.example/elimu", html, retrieved_at=NOW)
    changed = pipeline.process_html(
        "https://habari.example/elimu", html.replace("ufanisi", "mafanikio"), retrieved_at=NOW
    )
    assert changed.status == "duplicate"
    assert changed.duplicate_reason == "canonical_url"


def test_non_swahili_and_dynamic_pages_are_not_stored(tmp_path):
    pipeline = AcquisitionPipeline(CorpusStore(tmp_path))
    rejected = pipeline.process_html(
        "https://example.org/english", fixture("english_fake_sw.html"), retrieved_at=NOW
    )
    dynamic = pipeline.process_html(
        "https://example.org/app", "<html>" + "<script></script>" * 12 + "</html>", retrieved_at=NOW
    )
    assert rejected.status == "language_rejected"
    assert dynamic.status == "unsupported"
    assert pipeline.store.list_manifest() == []
