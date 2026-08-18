from __future__ import annotations

from src.research.queries import CorpusResearchQueryService


def test_summary_source_frontier_and_rejections_are_separated(research_state):
    session, pilot, corpus, _, _ = research_state
    query = CorpusResearchQueryService(session, corpus)

    overview = query.overview(pilot.id)
    sources = query.source_comparison(pilot.id)
    frontier = query.frontier(pilot.id, state="completed")
    rejection = query.rejection_analysis(pilot.id)

    assert overview["sources"] == 2
    assert overview["attempted"] == 2
    assert overview["accepted"] == 1
    assert overview["rejected"] == 1
    assert overview["artifacts"] == 1
    assert sources[0]["main_rejection_reason"] == "insufficient_static_content"
    assert sum(float(source["artifact_contribution"]) for source in sources) == 1.0
    assert frontier[0]["priority"] == "HIGH"
    assert rejection["pre_acquisition_skips"] == {"competing_language_path": 1}
    assert rejection["post_acquisition_rejections"] == {"insufficient_static_content": 1}


def test_artifact_lookup_review_update_and_manifest_leave_corpus_immutable(research_state):
    session, pilot, corpus, _, _ = research_state
    query = CorpusResearchQueryService(session, corpus)
    document_path = corpus / "documents" / "artifact-one.json"
    before = document_path.read_bytes()

    artifact = query.artifact(pilot.id, "artifact-one")
    query.save_review(pilot.id, "artifact-one", "good_article", "Clean Swahili prose.")
    query.save_review(pilot.id, "artifact-one", "acceptable", "Minor boilerplate.")
    manifest = query.manifest(pilot.id)

    assert artifact["document_id"] == "artifact-one"
    assert artifact["crawl_job_id"] == pilot.crawl_job_ids[0]
    assert query.review_summary(pilot.id)["labels"] == {"acceptable": 1}
    assert manifest["artifact_ids"] == ["artifact-one"]
    assert manifest["manual_review_sample_ids"] == ["artifact-one"]
    assert document_path.read_bytes() == before


def test_missing_pilot_and_artifact_are_safe(research_state):
    session, _, corpus, _, _ = research_state
    query = CorpusResearchQueryService(session, corpus)

    assert query.overview("missing") is None
    assert query.artifact("missing", "missing") is None
    assert query.frontier("missing") == []
