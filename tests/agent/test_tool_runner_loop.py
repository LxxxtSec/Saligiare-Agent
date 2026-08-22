from saligiare.agent.loop import AgentLoop
from saligiare.agent.state import RunStatus
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
        task_id="demo-task-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-demo-target",
        scope=("local-demo-target",),
        allowed_capabilities=("echo",),
        required_approval=ApprovalLevel.NONE,
        max_steps=3,
        timeout_seconds=60,
        evaluator_id="fake-evaluator",
    )


def make_action() -> Action:
    return Action(
        action_id="action-001",
        tool_name="echo",
        arguments={"text": "hello"},
        requested_capability="echo",
        reason="执行合成 Echo 工具",
    )


def make_runner(audit_log: AuditLog) -> ToolRunner:
    registry = ToolRegistry()
    echo = EchoTool()
    registry.register(echo.spec)

    return ToolRunner(
        policy_guard=PolicyGuard(
            registry,
            audit_log=audit_log,
        ),
        tools={"echo": echo},
        audit_log=audit_log,
    )


def test_agent_loop_runs_echo_tool_runner() -> None:
    audit_log = AuditLog()
    model = FakeModel(actions=(make_action(),))
    loop = AgentLoop(
        model=model,
        executor=make_runner(audit_log),
    )

    state = loop.run(make_task())

    assert state.status is RunStatus.MODEL_STOPPED
    assert state.step_count == 1
    assert len(state.actions) == 1
    assert len(state.observations) == 1
    assert state.observations[0].summary == "echo completed"
    assert len(audit_log.events) == 2