from __future__ import annotations

import json
from datetime import datetime, timezone

from src.application.services.url_analyzer import FetchResult
from src.research.models import PilotConfiguration, PilotSource
from src.research.run_corpus_pilot import run_pilot

HTML = """
<html lang="sw"><head><title>Habari</title></head><body><article>
<p>Serikali imesema wananchi watapata huduma bora na elimu katika jamii.</p>
<p>Watu wengi wameendelea kufanya kazi kwa maendeleo ya nchi na watoto.</p>
<p>Habari hii imetolewa leo baada ya mkutano wa viongozi wa eneo hilo.</p>
</article></body></html>
"""


def test_headless_pilot_runs_multiple_jobs_and_writes_manifest(tmp_path, monkeypatch):
    sources = (
        PilotSource("One", "https://one.example/sw/", "news", "one"),
        PilotSource("Two", "https://two.example/sw/", "knowledge", "two"),
    )

    def fake_fetch(_self, url, **_options):
        if url.endswith("/robots.txt"):
            return FetchResult(
                url,
                url,
                200,
                "text/plain",
                "User-agent: *\nAllow: /",
                datetime.now(timezone.utc),
            )
        return FetchResult(url, url, 200, "text/html", HTML, datetime.now(timezone.utc))

    monkeypatch.setattr("src.research.run_corpus_pilot.URLNewsAnalyzer.fetch_result", fake_fetch)
    monkeypatch.setattr(
        "src.research.run_corpus_pilot._git_metadata", lambda: ("test", "a" * 40, False)
    )
    monkeypatch.setattr(
        "src.research.run_corpus_pilot.PublicUrlSafetyAdapter.is_safe",
        lambda _self, _url: True,
    )
    database = tmp_path / "pilot.sqlite"
    corpus = tmp_path / "corpus"
    manifest = tmp_path / "pilot-manifest.json"

    pilot_id = run_pilot(
        PilotConfiguration(sources, 1, 0, 1),
        state_db=database,
        corpus_root=corpus,
        manifest_path=manifest,
    )

    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["pilot_id"] == pilot_id
    assert payload["state"] == "completed"
    assert len(payload["crawl_job_ids"]) == 2
    assert payload["metrics"]["attempted"] == 2
    assert payload["metrics"]["artifacts"] == 1  # identical text deduplicates by hash
    assert len(payload["artifact_ids"]) == 1
