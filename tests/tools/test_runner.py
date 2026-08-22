from saligiare.core.action import Action
from saligiare.core.observation import ObservationStatus
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.security.audit import AuditLog
from saligiare.security.policy import PolicyGuard
from saligiare.tools.echo import EchoTool
from saligiare.tools.registry import ToolRegistry
from saligiare.tools.runner import ToolRunner


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
    capability: str = "echo",
    text: str = "hello",
) -> Action:
    return Action(
        action_id="action-001",
        tool_name="echo",
        arguments={"text": text},
        requested_capability=capability,
        reason="测试工具执行",
    )


def make_runner(
    audit_log: AuditLog | None = None,
) -> ToolRunner:
    registry = ToolRegistry()
    echo = EchoTool()
    registry.register(echo.spec)

    return ToolRunner(
        policy_guard=PolicyGuard(registry, audit_log=audit_log),
        tools={"echo": echo},
        audit_log=audit_log,
    )


def test_runner_executes_allowed_tool() -> None:
    observation = make_runner().run(
        make_task("echo"),
        make_action(),
    )

    assert observation.status is ObservationStatus.SUCCEEDED
    assert observation.action_id == "action-001"
    assert observation.source == "echo"
    assert "echo completed" in observation.summary


def test_runner_does_not_execute_denied_tool() -> None:
    log = AuditLog()
    observation = make_runner(log).run(
        make_task("source_read"),
        make_action(),
    )

    assert observation.status is ObservationStatus.FAILED
    assert "policy denied" in observation.summary
    assert len(log.events) == 2
    assert log.events[0].decision == "denied"
    assert log.events[1].decision == "denied"


def test_runner_converts_tool_validation_error_to_observation() -> None:
    observation = make_runner().run(
        make_task("echo"),
        make_action(text=" "),
    )

    assert observation.status is ObservationStatus.FAILED
    assert "tool execution failed" in observation.summary


def test_runner_records_successful_execution() -> None:
    log = AuditLog()

    observation = make_runner(log).run(
        make_task("echo"),
        make_action(),
    )

    assert observation.status is ObservationStatus.SUCCEEDED
    assert len(log.events) == 2
    assert log.events[0].decision == "allowed"
    assert log.events[1].decision == "succeeded"