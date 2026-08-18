from __future__ import annotations

from src.research_ui.corpus_pilot import VIEWS, build_query_service, pipeline_steps


def test_console_import_views_and_pipeline_projection(research_state):
    _, pilot, corpus, database, _ = research_state
    query, session = build_query_service(database, corpus)
    try:
        activity = query.current_activity(pilot.id)
        steps = pipeline_steps(activity)
    finally:
        session.close()

    assert "Overview & Current Activity" in VIEWS
    assert "Quality Review" in VIEWS
    assert any(status == "current" for _, status in steps)
    assert steps[-1][0] == "STORE"
