import pytest
from pydantic import ValidationError

from saligiare.core.task import ApprovalLevel, Task, TaskMode


def make_valid_task(**overrides: object) -> Task:
    values: dict[str, object] = {
        "task_id": "demo-task-001",
        "mode": TaskMode.CTF_SOLVE,
        "target": "local-demo-target",
        "scope": ("local-demo-target",),
        "allowed_capabilities": ("artifact_read",),
        "required_approval": ApprovalLevel.NONE,
        "max_steps": 10,
        "timeout_seconds": 60,
        "evaluator_id": "fake-evaluator",
        "metadata": {"difficulty": "easy"},
    }
    values.update(overrides)
    return Task(**values)


def test_task_accepts_valid_values() -> None:
    task = make_valid_task()

    assert task.task_id == "demo-task-001"
    assert task.mode is TaskMode.CTF_SOLVE
    assert task.max_steps == 10


def test_task_rejects_unknown_mode() -> None:
    with pytest.raises(ValidationError):
        make_valid_task(mode="not-a-real-mode")


def test_task_rejects_non_positive_budget() -> None:
    with pytest.raises(ValidationError):
        make_valid_task(max_steps=0)

    with pytest.raises(ValidationError):
        make_valid_task(timeout_seconds=-1)


def test_task_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        make_valid_task(untrusted_permission="shell")


def test_task_cannot_change_top_level_fields() -> None:
    task = make_valid_task()

    with pytest.raises(ValidationError):
        task.max_steps = 100