from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from saligiare.core.observation import Observation, ObservationStatus


def make_valid_observation(**overrides: object) -> Observation:
    values: dict[str, object] = {
        "observation_id": "observation-001",
        "action_id": "action-001",
        "source": "artifact_read",
        "status": ObservationStatus.SUCCEEDED,
        "summary": "读取到一个 ELF 文件",
        "raw_ref": "trace://run-001/observation-001",
        "truncated": False,
        "created_at": datetime(2026, 8, 22, tzinfo=UTC),
    }
    values.update(overrides)
    return Observation(**values)


def test_observation_accepts_valid_values() -> None:
    observation = make_valid_observation()

    assert observation.observation_id == "observation-001"
    assert observation.action_id == "action-001"
    assert observation.status is ObservationStatus.SUCCEEDED
    assert observation.truncated is False


def test_observation_rejects_unknown_status() -> None:
    with pytest.raises(ValidationError):
        make_valid_observation(status="unknown")


def test_observation_rejects_blank_required_strings() -> None:
    with pytest.raises(ValidationError):
        make_valid_observation(observation_id="")

    with pytest.raises(ValidationError):
        make_valid_observation(action_id=" ")

    with pytest.raises(ValidationError):
        make_valid_observation(source="")

    with pytest.raises(ValidationError):
        make_valid_observation(summary="")


def test_observation_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        make_valid_observation(is_verified=True)


def test_observation_is_frozen_at_the_top_level() -> None:
    observation = make_valid_observation()

    with pytest.raises(ValidationError):
        observation.status = ObservationStatus.FAILED