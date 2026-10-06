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
    assert rejected.observation.stage.value == "language_validation"
    assert rejected.observation.reason.value == "likely_non_swahili"
    assert rejected.observation.html_language == "sw"
    assert rejected.observation.language_evidence_score is not None
    assert rejected.observation.extracted_character_count > 0
    assert dynamic.observation.stage.value == "static_extraction"
    assert dynamic.observation.reason.value == "dynamic_browser_required"
    assert dynamic.observation.dynamic_signal is True
    assert dynamic.observation.paragraph_count == 0
    assert pipeline.store.list_manifest() == []


def test_insufficient_static_content_and_duplicates_have_structured_observations(tmp_path):
    pipeline = AcquisitionPipeline(CorpusStore(tmp_path))
    insufficient = pipeline.process_html(
        "https://example.org/short", "<html><main><p>Too short.</p></main></html>", retrieved_at=NOW
    )
    first = pipeline.process_html(
        "https://habari.example/elimu", fixture("semantic_sw.html"), retrieved_at=NOW
    )
    duplicate = pipeline.process_html(
        "https://habari.example/elimu", fixture("semantic_sw.html"), retrieved_at=NOW
    )

    assert insufficient.observation.reason.value == "insufficient_static_content"
    assert insufficient.observation.main_container is True
    assert first.observation.reason.value == "accepted"
    assert duplicate.observation.stage.value == "deduplication"
    assert duplicate.observation.reason.value == "duplicate_canonical_url"


def test_unsafe_declared_canonical_falls_back_to_final_public_url(tmp_path):
    html = fixture("semantic_sw.html").replace(
        "https://habari.example/elimu?utm_source=feed", "file:///etc/passwd"
    )
    result = AcquisitionPipeline(CorpusStore(tmp_path)).process_html(
        "https://habari.example/original", html, retrieved_at=NOW
    )

    assert result.document is not None
    assert result.document.canonical_url == "https://habari.example/original"
