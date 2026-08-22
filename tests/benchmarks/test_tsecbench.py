import pytest

from saligiare.benchmarks.tsecbench.adapter import (
    TsecbenchLocalCase,
    TsecbenchTaskAdapter,
)
from saligiare.benchmarks.tsecbench.runner import TsecbenchRunner
from saligiare.core.action import Action
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.models.fake import FakeModel
from saligiare.security.audit import AuditLog
from saligiare.security.policy import PolicyGuard
from saligiare.tools.echo import EchoTool
from saligiare.tools.registry import ToolRegistry
from saligiare.tools.runner import ToolRunner


def make_task() -> Task:
    return Task(
        task_id="tsecbench-local-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-fixture",
        scope=("local-fixture",),
        allowed_capabilities=("echo",),
        required_approval=ApprovalLevel.NONE,
        max_steps=2,
        timeout_seconds=30,
        evaluator_id="tsecbench-local-v1",
    )


def make_payload() -> str:
    return TsecbenchTaskAdapter.dump_case(
        TsecbenchLocalCase(
            task=make_task(),
            expected_observation_summaries=("echo completed",),
            candidate_refs=("candidate://flag-001",),
            evidence_refs=("trace://observation-001",),
        ),
    )


def make_action() -> Action:
    return Action(
        action_id="action-001",
        tool_name="echo",
        arguments={"text": "hello"},
        requested_capability="echo",
        reason="运行本地合成工具",
    )


def make_executor() -> ToolRunner:
    registry = ToolRegistry()
    echo = EchoTool()
    registry.register(echo.spec)
    audit_log = AuditLog()
    return ToolRunner(
        policy_guard=PolicyGuard(registry, audit_log=audit_log),
        tools={"echo": echo},
        audit_log=audit_log,
    )


def test_adapter_round_trips_local_case() -> None:
    adapter = TsecbenchTaskAdapter()

    case = adapter.load_case(make_payload())

    assert case.task.task_id == "tsecbench-local-001"
    assert case.expected_observation_summaries == ("echo completed",)


def test_adapter_rejects_invalid_payload() -> None:
    with pytest.raises(ValueError, match="invalid TSECBENCH"):
        TsecbenchTaskAdapter().load_case("not-json")


def test_runner_evaluates_authorized_local_case() -> None:
    runner = TsecbenchRunner(
        model=FakeModel(actions=(make_action(),)),
        executor=make_executor(),
    )

    state, result = runner.run(make_payload(), trace_id="trace-run-001")

    assert state.step_count == 1
    assert result.task_id == "tsecbench-local-001"
    assert result.evaluator_verdict == "accepted"
    assert result.status == "completed"
    assert result.trace_id == "trace-run-001"
    assert result.budget_usage["steps"] == 1


def test_runner_rejects_failed_case() -> None:
    denied_action = make_action().model_copy(
        update={"requested_capability": "not-allowed"},
    )
    runner = TsecbenchRunner(
        model=FakeModel(actions=(denied_action,)),
        executor=make_executor(),
    )

    _state, result = runner.run(make_payload(), trace_id="trace-run-002")

    assert result.status == "failed"
    assert result.evaluator_verdict == "rejected"
