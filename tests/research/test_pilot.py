from __future__ import annotations

import pytest

from src.research.models import (
    CorpusPilotRun,
    PilotConfiguration,
    PilotSource,
    PilotState,
    deterministic_sample,
)


def sources(count=2):
    return tuple(
        PilotSource(str(index), f"https://{index}.example/sw/", "news", "bounded source")
        for index in range(count)
    )


def test_pilot_configuration_snapshot_and_multi_job_lifecycle():
    configuration = PilotConfiguration(sources(), 10, 1, 2)
    pilot = CorpusPilotRun.create(configuration)

    pilot.start()
    pilot.associate_job("job-one")
    pilot.associate_job("job-two")
    pilot.associate_job("job-two")
    pilot.complete()

    assert pilot.state == PilotState.COMPLETED
    assert pilot.crawl_job_ids == ["job-one", "job-two"]
    assert configuration.to_dict()["expected_language"] == "sw"
    assert configuration.to_dict()["candidate_policy_version"] == "candidate-quality-v1"
    assert pilot.finished_at is not None


def test_pilot_interruption_failure_and_budget_bounds():
    pilot = CorpusPilotRun.create(PilotConfiguration(sources(), 2, 0, 1))
    pilot.start()
    pilot.interrupt()
    assert pilot.state == PilotState.INTERRUPTED

    failed = CorpusPilotRun.create(PilotConfiguration(sources(), 2, 0, 1))
    failed.fail("network fixture failed")
    assert failed.state == PilotState.FAILED
    with pytest.raises(ValueError):
        PilotConfiguration(sources(8), 20, 1, 1)


def test_deterministic_sample_balances_sources_and_short_artifacts():
    artifacts = [
        {"document_id": "b", "domain": "one", "text_length": 100},
        {"document_id": "a", "domain": "one", "text_length": 20},
        {"document_id": "d", "domain": "two", "text_length": 200},
        {"document_id": "c", "domain": "two", "text_length": 10},
    ]

    first = deterministic_sample(artifacts, per_source=1, weak_limit=2)
    second = deterministic_sample(list(reversed(artifacts)), per_source=1, weak_limit=2)

    assert first == second == ["a", "c"]
