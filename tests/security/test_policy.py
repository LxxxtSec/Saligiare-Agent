import pytest
from pydantic import ValidationError

from saligiare.core.action import Action
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.security.policy import (
    PolicyDecisionStatus,
    PolicyGuard,
)
from saligiare.tools.echo import EchoTool
from saligiare.tools.registry import ToolRegistry


def make_task(*capabilities: str) -> Task:
    return Task(
        task_id="demo-task-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-demo-target",
        scope=("local-demo-target",),
        allowed_capabilities=capabilities or ("echo",),
        required_approval=ApprovalLevel.NONE,
        max_steps=10,
        timeout_seconds=60,
        evaluator_id="fake-evaluator",
    )


def make_action(
    tool_name: str = "echo",
    capability: str = "echo",
) -> Action:
    return Action(
        action_id="action-001",
        tool_name=tool_name,
        arguments={"text": "hello"},
        requested_capability=capability,
        reason="测试策略判断",
    )


def make_guard() -> PolicyGuard:
    registry = ToolRegistry()
    registry.register(EchoTool().spec)
    return PolicyGuard(registry)


def test_policy_allows_matching_tool_and_capability() -> None:
    decision = make_guard().check(
        make_task("echo"),
        make_action(),
    )

    assert decision.status is PolicyDecisionStatus.ALLOWED
    assert decision.allowed is True


def test_policy_denies_unknown_tool() -> None:
    decision = make_guard().check(
        make_task("echo"),
        make_action(tool_name="not_registered"),
    )

    assert decision.status is PolicyDecisionStatus.DENIED
    assert decision.allowed is False
    assert "unknown tool" in decision.reason


def test_policy_denies_capability_not_allowed_by_task() -> None:
    decision = make_guard().check(
        make_task("source_read"),
        make_action(),
    )

    assert decision.status is PolicyDecisionStatus.DENIED
    assert "not allowed by task" in decision.reason


def test_policy_denies_capability_mismatch() -> None:
    decision = make_guard().check(
        make_task("source_read"),
        make_action(capability="source_read"),
    )

    assert decision.status is PolicyDecisionStatus.DENIED
    assert "does not match tool capability" in decision.reason


def test_policy_decision_is_frozen() -> None:
    decision = make_guard().check(
        make_task("echo"),
        make_action(),
    )

    with pytest.raises(ValidationError):
        decision.status = PolicyDecisionStatus.DENIED