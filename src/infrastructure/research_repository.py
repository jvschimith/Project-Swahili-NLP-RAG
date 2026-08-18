"""SQLAlchemy persistence for pilot metadata and separate research evaluation."""

from __future__ import annotations

import json
from urllib.parse import urlsplit

from sqlalchemy.orm import Session

from src.infrastructure.database.models import (
    DBCorpusArtifactReview,
    DBCorpusPilot,
    DBCorpusPilotSource,
)
from src.research.models import ArtifactReview, CorpusPilotRun, PilotSource


class SqlAlchemyResearchRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_pilot(
        self,
        pilot: CorpusPilotRun,
        *,
        software_version: str,
        git_branch: str | None,
        git_commit: str | None,
        git_dirty: bool | None,
        python_version: str,
        corpus_path: str,
        database_path: str,
    ) -> None:
        row = DBCorpusPilot(
            id=pilot.id,
            state=pilot.state.value,
            configuration_json=json.dumps(pilot.configuration.to_dict()),
            software_version=software_version,
            git_branch=git_branch,
            git_commit=git_commit,
            git_dirty=git_dirty,
            python_version=python_version,
            corpus_path=corpus_path,
            database_path=database_path,
            started_at=pilot.started_at,
            finished_at=pilot.finished_at,
            error=pilot.error,
        )
        self.session.add(row)
        for position, source in enumerate(pilot.configuration.sources):
            self.session.add(
                DBCorpusPilotSource(
                    pilot_id=pilot.id,
                    position=position,
                    name=source.name,
                    origin=_origin(source),
                    seed_url=source.seed_url,
                    category=source.category,
                    rationale=source.rationale,
                    expected_language_route=source.expected_language_route,
                    robots_status=source.robots_status,
                    static_suitability=source.static_suitability,
                    dynamic_dependence=source.dynamic_dependence,
                    candidate_availability=source.candidate_availability,
                    state="pending",
                )
            )
        self.session.commit()

    def save_pilot(self, pilot: CorpusPilotRun) -> None:
        row = self.session.get(DBCorpusPilot, pilot.id)
        if row is None:
            raise ValueError(f"Pilot not found: {pilot.id}")
        row.state = pilot.state.value
        row.finished_at = pilot.finished_at
        row.error = pilot.error
        self.session.commit()

    def associate_source_job(self, pilot_id: str, origin: str, job_id: str) -> None:
        row = self._source(pilot_id, origin)
        row.crawl_job_id = job_id
        row.state = "running"
        self.session.commit()

    def finish_source(self, pilot_id: str, origin: str, state: str = "completed") -> None:
        row = self._source(pilot_id, origin)
        row.state = state
        self.session.commit()

    def save_review(self, review: ArtifactReview) -> None:
        pilot = self.session.get(DBCorpusPilot, review.pilot_id)
        if pilot is None:
            raise ValueError(f"Pilot not found: {review.pilot_id}")
        row = (
            self.session.query(DBCorpusArtifactReview)
            .filter_by(pilot_id=review.pilot_id, artifact_id=review.artifact_id)
            .one_or_none()
        )
        values = {
            "label": review.label.value,
            "note": review.note,
            "reviewed_at": review.reviewed_at,
        }
        if row is None:
            row = DBCorpusArtifactReview(
                pilot_id=review.pilot_id, artifact_id=review.artifact_id, **values
            )
            self.session.add(row)
        else:
            for key, value in values.items():
                setattr(row, key, value)
        self.session.commit()

    def _source(self, pilot_id: str, origin: str) -> DBCorpusPilotSource:
        row = (
            self.session.query(DBCorpusPilotSource)
            .filter_by(pilot_id=pilot_id, origin=origin)
            .one_or_none()
        )
        if row is None:
            raise ValueError(f"Pilot source not found: {origin}")
        return row


def _origin(source: PilotSource) -> str:
    parsed = urlsplit(source.seed_url)
    return f"{parsed.scheme}://{parsed.netloc}"
