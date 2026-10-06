"""Streamlit Corpus Research Console over persisted application read models."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import streamlit as st
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session

from src.infrastructure.database.connection import _enable_sqlite_foreign_keys
from src.research.models import ReviewLabel
from src.research.queries import CorpusResearchQueryService

DEFAULT_DB = Path("data/corpus-pilot/pilot.sqlite")
DEFAULT_CORPUS = Path("data/corpus-pilot/corpus")
VIEWS = (
    "Overview & Current Activity",
    "Frontier & Candidate Inspector",
    "Acquisition Inspector",
    "Corpus & Provenance Explorer",
    "Source Comparison",
    "Rejection Analysis",
    "Quality Review",
    "Experiment Metadata",
)


def build_query_service(
    state_db: Path, corpus_root: Path
) -> tuple[CorpusResearchQueryService, Session]:
    engine = create_engine(f"sqlite:///{state_db}")
    event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    session = Session(engine)
    return CorpusResearchQueryService(session, corpus_root), session


def pipeline_steps(activity: dict[str, object] | None) -> list[tuple[str, str]]:
    names = (
        "DISCOVERED",
        "ELIGIBILITY",
        "QUEUED",
        "ROBOTS",
        "SAFETY",
        "RATE",
        "FETCH",
        "INSPECT",
        "EXTRACT",
        "LANGUAGE",
        "DEDUP",
        "STORE",
    )
    if activity is None:
        return [(name, "pending") for name in names]
    state = str(activity.get("state", ""))
    terminal = str(activity.get("acquisition_stage") or "").upper()
    reached = {
        "STATIC_EXTRACTION": "EXTRACT",
        "LANGUAGE_VALIDATION": "LANGUAGE",
        "DEDUPLICATION": "DEDUP",
        "STORAGE": "STORE",
    }.get(terminal, "FETCH" if _as_int(activity.get("attempts", 0)) else "QUEUED")
    position = names.index(reached)
    if state == "skipped":
        position = names.index("ROBOTS")
    return [
        (name, "current" if index == position else "complete" if index < position else "pending")
        for index, name in enumerate(names)
    ]


def main() -> None:
    st.set_page_config(page_title="Corpus Research Console", layout="wide")
    st.title("Swahili Linguistic Intelligence")
    st.subheader("Corpus Research Console")
    st.warning("RESEARCH / INTERNAL INTERFACE — not the intended production frontend")
    state_db = Path(os.environ.get("CORPUS_PILOT_DB", str(DEFAULT_DB)))
    corpus_root = Path(os.environ.get("CORPUS_PILOT_ROOT", str(DEFAULT_CORPUS)))
    st.sidebar.caption("Headless CLI owns crawling; this console polls persisted checkpoints.")
    st.sidebar.button("Refresh persisted state")
    view = st.sidebar.radio("View", VIEWS)
    if not state_db.exists():
        st.info("No pilot database found. Start the headless pilot CLI first.")
        return
    query, session = build_query_service(state_db, corpus_root)
    try:
        pilot_id = query.latest_pilot_id()
        if pilot_id is None:
            st.info("No pilot experiment has been recorded yet.")
            return
        if view == VIEWS[0]:
            render_overview(query, pilot_id)
        elif view == VIEWS[1]:
            render_frontier(query, pilot_id)
        elif view == VIEWS[2]:
            render_acquisition(query, pilot_id)
        elif view == VIEWS[3]:
            render_corpus(query, pilot_id)
        elif view == VIEWS[4]:
            render_sources(query, pilot_id)
        elif view == VIEWS[5]:
            render_rejections(query, pilot_id)
        elif view == VIEWS[6]:
            render_reviews(query, pilot_id)
        else:
            render_experiment(query, pilot_id)
    finally:
        session.close()


def render_overview(query: CorpusResearchQueryService, pilot_id: str) -> None:
    summary = query.overview(pilot_id)
    if summary is None:
        st.info("Pilot not found.")
        return
    st.header("Overview")
    st.status(f"Pilot status: {str(summary['state']).upper()}", expanded=False)
    keys = (
        ("Sources", "sources"),
        ("URLs discovered", "discovered"),
        ("Eligible", "eligible"),
        ("Attempted", "attempted"),
        ("Accepted", "accepted"),
        ("Rejected", "rejected"),
        ("Artifacts", "artifacts"),
        ("Duplicates", "duplicates"),
        ("Robots exclusions", "robots_exclusions"),
        ("Frontier remaining", "frontier_remaining"),
    )
    columns = st.columns(5)
    for index, (label, key) in enumerate(keys):
        columns[index % 5].metric(label, str(summary[key]))
    st.caption("Operational acquisition measures; not linguistic accuracy.")
    rates = st.columns(3)
    rates[0].metric("Acceptance rate", f"{_as_float(summary['acceptance_rate']):.1%}")
    rates[1].metric(
        "Artifact yield / attempt", f"{_as_float(summary['artifact_yield_per_attempt']):.1%}"
    )
    rates[2].metric(
        "Artifacts / discovered", f"{_as_float(summary['artifacts_per_discovered']):.2%}"
    )
    activity = query.current_activity(pilot_id)
    st.header("Current Activity")
    if activity is None:
        st.info("No crawl activity is exposed yet.")
    else:
        st.json(activity, expanded=False)
    st.subheader("Page lifecycle")
    st.write(
        " → ".join(
            f"**{name}**" if status == "current" else name
            for name, status in pipeline_steps(activity)
        )
    )
    artifacts = query.artifacts(pilot_id, limit=200)
    if artifacts:
        growth = [
            {"retrieved_at": item["retrieved_at"], "artifacts": index}
            for index, item in enumerate(
                sorted(artifacts, key=lambda row: str(row["retrieved_at"])), 1
            )
        ]
        st.subheader("Corpus growth")
        st.line_chart(growth, x="retrieved_at", y="artifacts")


def render_frontier(query: CorpusResearchQueryService, pilot_id: str) -> None:
    st.header("Frontier Explorer")
    sources = query.source_comparison(pilot_id)
    origin = st.selectbox("Origin", [None] + [str(item["origin"]) for item in sources])
    state = st.selectbox("State", [None, "queued", "processing", "completed", "failed", "skipped"])
    priority_name = st.selectbox("Priority", [None, "HIGH", "NORMAL", "LOW"])
    kind = st.selectbox(
        "Resource kind",
        [None, "article", "section", "video", "audio", "unsupported_file", "unknown"],
    )
    depth = st.selectbox("Depth", [None, 0, 1, 2])
    rows = query.frontier(
        pilot_id,
        origin=origin,
        state=state,
        priority=(
            {"HIGH": 90, "NORMAL": 50, "LOW": 10}[priority_name]
            if priority_name is not None
            else None
        ),
        resource_kind=kind,
        depth=depth,
        limit=100,
    )
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.header("Candidate Inspector")
    if not rows:
        st.info("No frontier entries match the bounded filters.")
        return
    selected = st.selectbox("URL", [str(row["url"]) for row in rows])
    row = next(item for item in rows if item["url"] == selected)
    eligible = row["skip_reason"] not in {
        "competing_language_path",
        "unsupported_resource_kind",
        "external_origin",
        "depth_limit",
        "unsafe_url",
    }
    st.write(f"Eligibility: **{'YES' if eligible else 'NO'}**")
    st.write(
        f"Priority: **{row['priority']}** · Resource kind: **{str(row['resource_kind']).upper()}**"
    )
    st.write("Evidence:", row["candidate_evidence"] or ["neutral URL path"])
    st.write("Skip/policy reason:", row["skip_reason"] or "none")


def render_acquisition(query: CorpusResearchQueryService, pilot_id: str) -> None:
    st.header("Acquisition Inspector")
    rows = [
        row
        for row in query.frontier(pilot_id, limit=200)
        if _as_int(row["attempts"]) > 0
    ]
    if not rows:
        st.info("No attempted acquisitions are exposed yet.")
        return
    selected = st.selectbox("Attempted URL", [str(row["url"]) for row in rows])
    row = next(item for item in rows if item["url"] == selected)
    details = dict(cast(Mapping[str, object], row["acquisition_details"]))
    st.json(
        {
            "stage": row["acquisition_stage"] or "not exposed",
            "reason": row["acquisition_reason"] or "not exposed",
            "final_url": row["final_url"] or "not exposed",
            "artifact_id": row["artifact_id"] or "none",
            "duplicate_reason": row["duplicate_reason"] or "none",
            **details,
        }
    )


def render_corpus(query: CorpusResearchQueryService, pilot_id: str) -> None:
    st.header("Corpus Artifact Explorer")
    artifacts = query.artifacts(pilot_id, limit=100)
    st.dataframe(artifacts, use_container_width=True, hide_index=True)
    if not artifacts:
        st.info("No new artifacts belong to this pilot.")
        return
    artifact_id = st.selectbox("Artifact", [str(item["document_id"]) for item in artifacts])
    artifact = query.artifact(pilot_id, artifact_id)
    if artifact is None:
        st.warning("Artifact metadata exists but its immutable document is unavailable.")
        return
    st.subheader("Provenance")
    st.json(
        {
            "document_id": artifact.get("document_id"),
            "requested_url": artifact.get("original_url"),
            "final_url": artifact.get("final_url"),
            "canonical_url": artifact.get("canonical_url"),
            "source_domain": artifact.get("source_domain"),
            "retrieved_at": artifact.get("retrieved_at"),
            "extraction_method": artifact.get("extraction_method"),
            "acquisition_version": dict(
                cast(Mapping[str, object], artifact.get("provenance", {}))
            ).get("acquisition_version"),
            "sha256": artifact.get("content_hash"),
            "relative_corpus_path": artifact.get("storage_path"),
            "crawl_job_id": artifact.get("crawl_job_id"),
            "parent_discovery_url": artifact.get("parent_url"),
        }
    )
    st.text_area(
        "Extracted text (read-only)",
        str(artifact.get("normalized_text", ""))[:12000],
        height=360,
        disabled=True,
    )


def render_sources(query: CorpusResearchQueryService, pilot_id: str) -> None:
    st.header("Source Comparison")
    rows = query.source_comparison(pilot_id)
    st.dataframe(rows, use_container_width=True, hide_index=True)
    if rows:
        st.bar_chart(rows, x="name", y="artifacts")


def render_rejections(query: CorpusResearchQueryService, pilot_id: str) -> None:
    st.header("Rejection Analysis")
    analysis = query.rejection_analysis(pilot_id)
    st.subheader("PRE-ACQUISITION SKIPS")
    st.json(analysis["pre_acquisition_skips"])
    st.subheader("POST-ACQUISITION REJECTIONS")
    st.json(analysis["post_acquisition_rejections"])


def render_reviews(query: CorpusResearchQueryService, pilot_id: str) -> None:
    st.header("Quality Review")
    artifacts = query.artifacts(pilot_id, limit=100)
    if not artifacts:
        st.info("No pilot artifact is available for review.")
        return
    st.caption("Deterministic suggested sample: " + ", ".join(query.sample(pilot_id)))
    artifact_id = st.selectbox("Artifact ID", [str(item["document_id"]) for item in artifacts])
    label = st.selectbox("Review label", [item.value for item in ReviewLabel])
    note = st.text_area("Optional bounded note", max_chars=1000)
    if st.button("Save separate research review"):
        query.save_review(pilot_id, artifact_id, label, note)
        st.success("Review stored separately; corpus JSON was not modified.")
    st.json(query.review_summary(pilot_id))
    st.dataframe(query.reviews(pilot_id), use_container_width=True, hide_index=True)


def render_experiment(query: CorpusResearchQueryService, pilot_id: str) -> None:
    st.header("Experiment Metadata")
    experiment = query.experiment(pilot_id)
    st.json(experiment or {"status": "missing pilot"})
    st.caption(
        "Paths are local experiment locations. Environment variables and secrets are never shown."
    )


def _as_int(value: object) -> int:
    return int(str(value))


def _as_float(value: object) -> float:
    return float(str(value))


if __name__ == "__main__":
    main()
