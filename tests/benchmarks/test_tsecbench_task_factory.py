import pytest

from saligiare.benchmarks.tsecbench.official import (
    TsecbenchChallenge,
    TsecbenchStartResult,
)
from saligiare.benchmarks.tsecbench.task_factory import TsecbenchTaskFactory
from saligiare.core.task import ApprovalLevel, TaskMode


def make_challenge() -> TsecbenchChallenge:
    return TsecbenchChallenge(
        unique_code="challenge-001",
        description="授权本地测试题",
        difficulty="medium",
        level="normal",
        total_score=200,
        flag_count=2,
        correct_flag_count=0,
        is_completed=False,
        container_status="available",
        container_addr=("10.0.0.10:8080",),
    )


def make_started(code: str = "challenge-001") -> TsecbenchStartResult:
    return TsecbenchStartResult(
        unique_code=code,
        container_addr=("10.0.0.10:8080", "10.0.0.11:9000"),
    )


def test_factory_builds_scoped_dedicated_vm_task() -> None:
    task = TsecbenchTaskFactory(
        allowed_capabilities=("tsecbench_target", "artifact_read"),
        max_steps=20,
        timeout_seconds=600,
    ).build(make_challenge(), make_started())

    assert task.task_id == "tsecbench:challenge-001"
    assert task.mode is TaskMode.CTF_SOLVE
    assert task.scope == ("10.0.0.10:8080", "10.0.0.11:9000")
    assert task.required_approval is ApprovalLevel.DEDICATED_VM
    assert task.max_steps == 20
    assert task.metadata["flag_count"] == "2"


def test_factory_rejects_mismatched_start_result() -> None:
    with pytest.raises(ValueError, match="do not match"):
        TsecbenchTaskFactory().build(make_challenge(), make_started("other"))


def test_factory_rejects_empty_addresses() -> None:
    started = TsecbenchStartResult(
        unique_code="challenge-001",
        container_addr=("10.0.0.10:8080",),
    )
    started = started.model_copy(update={"container_addr": ()})

    with pytest.raises(ValueError, match="no container addresses"):
        TsecbenchTaskFactory().build(make_challenge(), started)


def test_factory_requires_positive_budget() -> None:
    with pytest.raises(ValueError, match="max_steps"):
        TsecbenchTaskFactory(max_steps=0)
