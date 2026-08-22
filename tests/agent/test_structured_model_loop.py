from saligiare.agent.loop import AgentLoop
from saligiare.agent.state import RunStatus
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.models.provider import FakeProvider
from saligiare.models.structured import StructuredActionModel
from saligiare.security.audit import AuditLog
from saligiare.security.policy import PolicyGuard
from saligiare.tools.echo import EchoTool
from saligiare.tools.registry import ToolRegistry
from saligiare.tools.runner import ToolRunner


def make_task() -> Task:
    return Task(
        task_id="v1-task-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-demo-target",
        scope=("local-demo-target",),
        allowed_capabilities=("echo",),
        required_approval=ApprovalLevel.NONE,
        max_steps=2,
        timeout_seconds=30,
        evaluator_id="fake-evaluator",
    )


def make_runner(audit_log: AuditLog) -> ToolRunner:
    registry = ToolRegistry()
    echo = EchoTool()
    registry.register(echo.spec)
    return ToolRunner(
        policy_guard=PolicyGuard(registry, audit_log=audit_log),
        tools={"echo": echo},
        audit_log=audit_log,
    )


def test_v1_structured_model_runs_through_policy_and_tool() -> None:
    provider = FakeProvider(
        (
            (
                '{"action":{"action_id":"action-001","tool_name":"echo",'
                '"arguments":{"text":"hello v1"},"parent_observation_ids":[],'
                '"requested_capability":"echo","reason":"验证本地 Echo 工具"}}'
            ),
            '{"action":null}',
        ),
    )
    audit_log = AuditLog()
    loop = AgentLoop(
        model=StructuredActionModel(provider, prompt_version="v1"),
        executor=make_runner(audit_log),
    )

    state = loop.run(make_task())

    assert state.status is RunStatus.MODEL_STOPPED
    assert state.step_count == 1
    assert state.observations[0].summary == "echo completed"
    assert provider.requests[0].prompt_version == "v1"
    assert len(audit_log.events) == 2


def test_v1_structured_model_failure_stops_agent_safely() -> None:
    provider = FakeProvider(("not-json",))
    loop = AgentLoop(
        model=StructuredActionModel(provider),
        executor=make_runner(AuditLog()),
    )

    state = loop.run(make_task())

    assert state.status is RunStatus.FAILED
    assert state.step_count == 0
    assert state.stop_reason == "model failure: model response is not valid structured JSON"
