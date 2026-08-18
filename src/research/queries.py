"""Bounded read models consumed by the CLI, reports, and temporary research UI."""

from __future__ import annotations

import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import cast

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.infrastructure.database.models import (
    DBCorpusArtifactReview,
    DBCorpusPilot,
    DBCorpusPilotSource,
    DBCrawlFrontier,
    DBCrawlJob,
)
from src.research.models import ArtifactReview, ReviewLabel, deterministic_sample

ELIGIBILITY_SKIP_REASONS = {
    "unsupported_resource_kind",
    "competing_language_path",
    "external_origin",
    "depth_limit",
    "unsafe_url",
}


class CorpusResearchQueryService:
    """One narrow query surface over operational, corpus, and evaluation stores."""

    def __init__(self, session: Session, corpus_root: Path):
        self.session = session
        self.corpus_root = corpus_root.resolve()

    def latest_pilot_id(self) -> str | None:
        row = self.session.query(DBCorpusPilot.id).order_by(desc(DBCorpusPilot.started_at)).first()
        return str(row[0]) if row else None

    def experiment(self, pilot_id: str) -> dict[str, object] | None:
        row = self.session.get(DBCorpusPilot, pilot_id)
        if row is None:
            return None
        return {
            "pilot_id": row.id,
            "state": row.state,
            "started_at": _iso(row.started_at),
            "finished_at": _iso(row.finished_at),
            "configuration": json.loads(row.configuration_json),
            "software_version": row.software_version,
            "git_branch": row.git_branch,
            "git_commit": row.git_commit,
            "git_dirty_at_start": row.git_dirty,
            "python_version": row.python_version,
            "database_path": row.database_path,
            "corpus_path": row.corpus_path,
            "error": row.error,
        }

    def overview(self, pilot_id: str) -> dict[str, object] | None:
        experiment = self.experiment(pilot_id)
        if experiment is None:
            return None
        sources = self.source_comparison(pilot_id)
        artifacts = self.artifacts(pilot_id, limit=200)
        lengths = [int(str(item["text_length"])) for item in artifacts]
        totals: Counter[str] = Counter()
        for source in sources:
            for key in (
                "discovered",
                "eligible",
                "skipped",
                "attempted",
                "accepted",
                "rejected",
                "artifacts",
                "duplicates",
                "robots_exclusions",
                "frontier_remaining",
            ):
                totals[key] += int(str(source[key]))
        attempted = totals["attempted"]
        discovered = totals["discovered"]
        return {
            "pilot_id": pilot_id,
            "state": experiment["state"],
            "sources": len(sources),
            **totals,
            "acceptance_rate": totals["accepted"] / attempted if attempted else 0.0,
            "artifact_yield_per_attempt": totals["artifacts"] / attempted if attempted else 0.0,
            "artifacts_per_discovered": totals["artifacts"] / discovered if discovered else 0.0,
            "total_normalized_characters": sum(lengths),
            "average_artifact_length": statistics.mean(lengths) if lengths else 0.0,
            "median_artifact_length": statistics.median(lengths) if lengths else 0.0,
            "minimum_artifact_length": min(lengths, default=0),
            "maximum_artifact_length": max(lengths, default=0),
        }

    def source_comparison(self, pilot_id: str) -> list[dict[str, object]]:
        sources = (
            self.session.query(DBCorpusPilotSource)
            .filter_by(pilot_id=pilot_id)
            .order_by(DBCorpusPilotSource.position)
            .all()
        )
        manifest = self._manifest()
        output: list[dict[str, object]] = []
        for source in sources:
            entries = self._entries(source.crawl_job_id)
            states = Counter(entry.state for entry in entries)
            skip_reasons = Counter(entry.skip_reason for entry in entries if entry.skip_reason)
            failures = Counter(
                entry.acquisition_reason for entry in entries if entry.state == "failed"
            )
            source_artifacts = [
                item for item in manifest if item.get("domain") == _host(source.origin)
            ]
            lengths = [self._artifact_length(str(item["document_id"])) for item in source_artifacts]
            attempted = states["completed"] + states["failed"]
            eligible = sum(entry.skip_reason not in ELIGIBILITY_SKIP_REASONS for entry in entries)
            output.append(
                {
                    "name": source.name,
                    "origin": source.origin,
                    "category": source.category,
                    "seed_url": source.seed_url,
                    "rationale": source.rationale,
                    "robots_status": source.robots_status,
                    "state": source.state,
                    "crawl_job_id": source.crawl_job_id,
                    "discovered": len(entries),
                    "eligible": eligible,
                    "skipped": states["skipped"],
                    "attempted": attempted,
                    "accepted": states["completed"],
                    "rejected": states["failed"],
                    "artifacts": sum(entry.artifact_created for entry in entries),
                    "duplicates": sum(
                        bool(entry.duplicate_reason) or entry.skip_reason == "duplicate"
                        for entry in entries
                    ),
                    "robots_exclusions": sum(
                        reason.startswith("robots_") for reason in skip_reasons.elements()
                    ),
                    "frontier_remaining": states["queued"] + states["processing"],
                    "acceptance_rate": states["completed"] / attempted if attempted else 0.0,
                    "artifact_yield": (
                        sum(entry.artifact_created for entry in entries) / attempted
                        if attempted
                        else 0.0
                    ),
                    "total_characters": sum(lengths),
                    "average_length": statistics.mean(lengths) if lengths else 0.0,
                    "main_rejection_reason": failures.most_common(1)[0][0] if failures else None,
                    "termination_reason": self._termination(source.crawl_job_id),
                }
            )
        total_artifacts = sum(int(str(item["artifacts"])) for item in output)
        for item in output:
            item["artifact_contribution"] = (
                int(str(item["artifacts"])) / total_artifacts if total_artifacts else 0.0
            )
        return output

    def current_activity(self, pilot_id: str) -> dict[str, object] | None:
        source = (
            self.session.query(DBCorpusPilotSource)
            .filter_by(pilot_id=pilot_id)
            .order_by(
                (DBCorpusPilotSource.state == "running").desc(),
                DBCorpusPilotSource.position.desc(),
            )
            .first()
        )
        if source is None or source.crawl_job_id is None:
            return None
        entry = (
            self.session.query(DBCrawlFrontier)
            .filter_by(job_id=source.crawl_job_id)
            .order_by(
                (DBCrawlFrontier.state == "processing").desc(),
                DBCrawlFrontier.updated_at.desc(),
                DBCrawlFrontier.id.desc(),
            )
            .first()
        )
        if entry is None:
            return None
        job = self.session.get(DBCrawlJob, source.crawl_job_id)
        experiment = self.session.get(DBCorpusPilot, pilot_id)
        config = json.loads(experiment.configuration_json) if experiment else {}
        details = dict(json.loads(entry.acquisition_details_json or "[]"))
        return {
            "source": source.name,
            "crawl_job_id": source.crawl_job_id,
            "url": entry.canonical_url,
            "final_url": entry.final_url,
            "depth": entry.depth,
            "priority": _priority_name(entry.priority),
            "candidate_evidence": json.loads(entry.candidate_evidence_json),
            "resource_kind": entry.resource_kind,
            "state": entry.state,
            "skip_reason": entry.skip_reason,
            "attempts": entry.attempts,
            "robots_decision": "not exposed",
            "safety_decision": "not exposed",
            "rate_policy_seconds": config.get("min_delay_seconds", "not exposed"),
            "page_budget_consumed": job.pages_attempted if job else "not exposed",
            "page_budget_limit": job.max_pages if job else "not exposed",
            "acquisition_stage": entry.acquisition_stage,
            "acquisition_reason": entry.acquisition_reason,
            "artifact_id": entry.artifact_id,
            "duplicate_reason": entry.duplicate_reason,
            **details,
        }

    def frontier(
        self,
        pilot_id: str,
        *,
        origin: str | None = None,
        state: str | None = None,
        priority: int | None = None,
        resource_kind: str | None = None,
        depth: int | None = None,
        skip_reason: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, object]]:
        job_ids = [
            item[0]
            for item in self.session.query(DBCorpusPilotSource.crawl_job_id)
            .filter_by(pilot_id=pilot_id)
            .filter(DBCorpusPilotSource.crawl_job_id.is_not(None))
            .all()
        ]
        if not job_ids:
            return []
        query = self.session.query(DBCrawlFrontier).filter(DBCrawlFrontier.job_id.in_(job_ids))
        for field, value in (
            (DBCrawlFrontier.origin, origin),
            (DBCrawlFrontier.state, state),
            (DBCrawlFrontier.priority, priority),
            (DBCrawlFrontier.resource_kind, resource_kind),
            (DBCrawlFrontier.depth, depth),
            (DBCrawlFrontier.skip_reason, skip_reason),
        ):
            if value is not None:
                query = query.filter(field == value)
        rows = (
            query.order_by(DBCrawlFrontier.updated_at.desc()).offset(offset).limit(min(limit, 200))
        )
        return [self._frontier_row(row) for row in rows]

    def artifacts(self, pilot_id: str, *, limit: int = 100) -> list[dict[str, object]]:
        artifact_ids = {
            item[0]
            for item in self.session.query(DBCrawlFrontier.artifact_id)
            .join(
                DBCorpusPilotSource,
                DBCorpusPilotSource.crawl_job_id == DBCrawlFrontier.job_id,
            )
            .filter(DBCorpusPilotSource.pilot_id == pilot_id)
            .filter(DBCrawlFrontier.artifact_created.is_(True))
            .all()
        }
        output = []
        for record in self._manifest():
            if record.get("document_id") in artifact_ids:
                output.append(
                    {**record, "text_length": self._artifact_length(str(record["document_id"]))}
                )
        return output[: min(limit, 200)]

    def artifact(self, pilot_id: str, artifact_id: str) -> dict[str, object] | None:
        if artifact_id not in {str(item["document_id"]) for item in self.artifacts(pilot_id)}:
            return None
        path = self._document_path(artifact_id)
        if path is None:
            return None
        payload = cast(dict[str, object], json.loads(path.read_text(encoding="utf-8")))
        entry = (
            self.session.query(DBCrawlFrontier)
            .filter_by(artifact_id=artifact_id)
            .order_by(DBCrawlFrontier.updated_at.desc())
            .first()
        )
        payload["storage_path"] = str(path.relative_to(self.corpus_root))
        payload["crawl_job_id"] = entry.job_id if entry else None
        payload["parent_url"] = entry.parent_url if entry else None
        return payload

    def rejection_analysis(self, pilot_id: str) -> dict[str, dict[str, int]]:
        rows = self._pilot_entries(pilot_id)
        pre = Counter(str(row.skip_reason) for row in rows if row.skip_reason)
        post = Counter(
            str(row.acquisition_reason)
            for row in rows
            if row.state == "failed" and row.acquisition_reason
        )
        return {"pre_acquisition_skips": dict(pre), "post_acquisition_rejections": dict(post)}

    def save_review(
        self, pilot_id: str, artifact_id: str, label: str, note: str | None = None
    ) -> ArtifactReview:
        if self.artifact(pilot_id, artifact_id) is None:
            raise ValueError(f"Artifact not found in pilot: {artifact_id}")
        review = ArtifactReview.create(pilot_id, artifact_id, ReviewLabel(label), note)
        from src.infrastructure.research_repository import SqlAlchemyResearchRepository

        SqlAlchemyResearchRepository(self.session).save_review(review)
        return review

    def reviews(self, pilot_id: str) -> list[dict[str, object]]:
        rows = (
            self.session.query(DBCorpusArtifactReview)
            .filter_by(pilot_id=pilot_id)
            .order_by(DBCorpusArtifactReview.artifact_id)
            .all()
        )
        return [
            {
                "artifact_id": row.artifact_id,
                "label": row.label,
                "note": row.note,
                "reviewed_at": _iso(row.reviewed_at),
            }
            for row in rows
        ]

    def review_summary(self, pilot_id: str) -> dict[str, object]:
        labels = Counter(str(item["label"]) for item in self.reviews(pilot_id))
        reviewed = sum(labels.values())
        proportions = {
            label.value: labels[label.value] / reviewed if reviewed else 0.0
            for label in ReviewLabel
        }
        return {
            "reviewed": reviewed,
            "labels": dict(labels),
            "proportions": proportions,
            "good_or_acceptable_proportion": (
                (labels[ReviewLabel.GOOD_ARTICLE.value] + labels[ReviewLabel.ACCEPTABLE.value])
                / reviewed
                if reviewed
                else 0.0
            ),
        }

    def sample(self, pilot_id: str, *, per_source: int = 3) -> list[str]:
        return deterministic_sample(self.artifacts(pilot_id, limit=200), per_source=per_source)

    def manifest(self, pilot_id: str) -> dict[str, object]:
        experiment = self.experiment(pilot_id)
        if experiment is None:
            raise ValueError(f"Pilot not found: {pilot_id}")
        overview = self.overview(pilot_id)
        sources = self.source_comparison(pilot_id)
        return {
            **experiment,
            "metrics": overview,
            "sources": sources,
            "crawl_job_ids": [item["crawl_job_id"] for item in sources],
            "artifact_ids": [item["document_id"] for item in self.artifacts(pilot_id, limit=200)],
            "manual_review_sample_ids": self.sample(pilot_id),
            "reviews": self.review_summary(pilot_id),
        }

    def _entries(self, job_id: str | None) -> list[DBCrawlFrontier]:
        if job_id is None:
            return []
        return cast(
            list[DBCrawlFrontier],
            self.session.query(DBCrawlFrontier).filter_by(job_id=job_id).all(),
        )

    def _pilot_entries(self, pilot_id: str) -> list[DBCrawlFrontier]:
        job_ids = [
            item[0]
            for item in self.session.query(DBCorpusPilotSource.crawl_job_id)
            .filter_by(pilot_id=pilot_id)
            .filter(DBCorpusPilotSource.crawl_job_id.is_not(None))
            .all()
        ]
        if not job_ids:
            return []
        return cast(
            list[DBCrawlFrontier],
            self.session.query(DBCrawlFrontier).filter(DBCrawlFrontier.job_id.in_(job_ids)).all(),
        )

    def _termination(self, job_id: str | None) -> str | None:
        if job_id is None:
            return None
        from src.infrastructure.database.models import DBCrawlJob

        row = self.session.get(DBCrawlJob, job_id)
        return row.termination_reason if row else None

    def _manifest(self) -> list[dict[str, object]]:
        path = self.corpus_root / "manifest.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]

    def _document_path(self, artifact_id: str) -> Path | None:
        path = (self.corpus_root / "documents" / f"{artifact_id}.json").resolve()
        if self.corpus_root not in path.parents or not path.exists():
            return None
        return path

    def _artifact_length(self, artifact_id: str) -> int:
        path = self._document_path(artifact_id)
        if path is None:
            return 0
        return len(str(json.loads(path.read_text(encoding="utf-8")).get("normalized_text", "")))

    @staticmethod
    def _frontier_row(row: DBCrawlFrontier) -> dict[str, object]:
        return {
            "id": row.id,
            "job_id": row.job_id,
            "url": row.canonical_url,
            "origin": row.origin,
            "depth": row.depth,
            "priority": _priority_name(row.priority),
            "priority_value": row.priority,
            "resource_kind": row.resource_kind,
            "state": row.state,
            "candidate_evidence": json.loads(row.candidate_evidence_json),
            "parent_url": row.parent_url,
            "attempts": row.attempts,
            "skip_reason": row.skip_reason,
            "acquisition_stage": row.acquisition_stage,
            "acquisition_reason": row.acquisition_reason,
            "artifact_id": row.artifact_id,
            "duplicate_reason": row.duplicate_reason,
            "final_url": row.final_url,
            "acquisition_details": dict(json.loads(row.acquisition_details_json or "[]")),
        }


def _host(origin: str) -> str:
    from urllib.parse import urlsplit

    return urlsplit(origin).hostname or ""


def _priority_name(value: int) -> str:
    return {10: "LOW", 50: "NORMAL", 90: "HIGH"}.get(value, str(value))


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()
