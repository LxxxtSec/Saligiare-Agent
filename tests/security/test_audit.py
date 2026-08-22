import pytest
from pydantic import ValidationError

from saligiare.core.action import Action
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.security.audit import (
    AuditEvent,
    AuditEventType,
    AuditLog,
)
from saligiare.security.policy import (
    PolicyDecisionStatus,
    PolicyGuard,
)
from saligiare.tools.echo import EchoTool
from saligiare.tools.registry import ToolRegistry


def make_event(event_id: str = "event-001") -> AuditEvent:
    return AuditEvent(
        event_id=event_id,
        event_type=AuditEventType.POLICY_DECISION,
        action_id="action-001",
        tool_name="echo",
        decision="allowed",
        reason="tool and capability are allowed",
    )


def make_task() -> Task:
    return Task(
        task_id="demo-task-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-demo-target",
        scope=("local-demo-target",),
        allowed_capabilities=("echo",),
        required_approval=ApprovalLevel.NONE,
        max_steps=10,
        timeout_seconds=60,
        evaluator_id="fake-evaluator",
    )


def make_action() -> Action:
    return Action(
        action_id="action-001",
        tool_name="echo",
        arguments={"text": "hello"},
        requested_capability="echo",
        reason="测试审计",
    )


def make_guard(audit_log: AuditLog) -> PolicyGuard:
    registry = ToolRegistry()
    registry.register(EchoTool().spec)
    return PolicyGuard(registry, audit_log=audit_log)


def test_audit_log_appends_events() -> None:
    log = AuditLog()
    event = make_event()

    log.append(event)

    assert log.events == (event,)


def test_audit_log_rejects_duplicate_event_ids() -> None:
    log = AuditLog()
    log.append(make_event())

    with pytest.raises(ValueError, match="already exists"):
        log.append(make_event())


def test_audit_event_rejects_blank_reason() -> None:
    with pytest.raises(ValidationError):
        AuditEvent(
            event_id="event-001",
            event_type=AuditEventType.POLICY_DECISION,
            action_id="action-001",
            tool_name="echo",
            decision="denied",
            reason=" ",
        )


def test_policy_guard_records_decision() -> None:
    log = AuditLog()
    decision = make_guard(log).check(make_task(), make_action())

    assert decision.status is PolicyDecisionStatus.ALLOWED
    assert len(log.events) == 1
    assert log.events[0].action_id == "action-001"
    assert log.events[0].decision == "allowed"