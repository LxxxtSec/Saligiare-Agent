import pytest
from pydantic import ValidationError

from saligiare.core.action import Action


def make_valid_action(**overrides: object) -> Action:
    values: dict[str, object] = {
        "action_id": "action-001",
        "tool_name": "artifact_read",
        "arguments": {"path": "challenge.txt"},
        "parent_observation_ids": ("observation-000",),
        "requested_capability": "artifact_read",
        "reason": "读取任务附件以确认文件类型",
    }
    values.update(overrides)
    return Action(**values)


def test_action_accepts_valid_values() -> None:
    action = make_valid_action()

    assert action.action_id == "action-001"
    assert action.tool_name == "artifact_read"
    assert action.arguments == {"path": "challenge.txt"}


def test_action_rejects_blank_required_strings() -> None:
    with pytest.raises(ValidationError):
        make_valid_action(action_id="")

    with pytest.raises(ValidationError):
        make_valid_action(tool_name=" ")

    with pytest.raises(ValidationError):
        make_valid_action(requested_capability="")

    with pytest.raises(ValidationError):
        make_valid_action(reason="")


def test_action_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        make_valid_action(run_as_root=True)


def test_action_is_frozen_at_the_top_level() -> None:
    action = make_valid_action()

    with pytest.raises(ValidationError):
        action.tool_name = "host_shell"


def test_action_keeps_observation_references() -> None:
    action = make_valid_action(
        parent_observation_ids=("observation-001", "observation-002"),
    )

    assert action.parent_observation_ids == (
        "observation-001",
        "observation-002",
    )