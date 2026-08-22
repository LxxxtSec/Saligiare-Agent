import pytest

from saligiare.agent.state import RuntimeState
from saligiare.benchmarks.tsecbench.agent_solver import TsecbenchAgentSolver
from saligiare.benchmarks.tsecbench.official import (
    TsecbenchChallenge,
    TsecbenchStartResult,
)
from saligiare.benchmarks.tsecbench.task_factory import TsecbenchTaskFactory
from saligiare.core.action import Action
from saligiare.models.fake import FakeModel
from saligiare.security.audit import AuditLog
from saligiare.security.policy import PolicyGuard
from saligiare.tools.echo import EchoTool
from saligiare.tools.registry import ToolRegistry
from saligiare.tools.runner import ToolRunner


def make_challenge() -> TsecbenchChallenge:
    return TsecbenchChallenge(
        unique_code="challenge-001",
        description="授权测试题",
        difficulty="easy",
        level="normal",
        total_score=100,
        flag_count=1,
        correct_flag_count=0,
        is_completed=False,
        container_status="available",
    )


def make_started() -> TsecbenchStartResult:
    return TsecbenchStartResult(
        unique_code="challenge-001",
        container_addr=("10.0.0.10:8080",),
    )


def make_action() -> Action:
    return Action(
        action_id="action-001",
        tool_name="echo",
        arguments={"text": "completed"},
        requested_capability="echo",
        reason="完成合成测试",
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


class FakeFlagExtractor:
    def __init__(self, flags: tuple[str, ...]) -> None:
        self.flags = flags
        self.calls: list[tuple[str, int]] = []

    def extract(self, task, state: RuntimeState) -> tuple[str, ...]:
        self.calls.append((task.task_id, state.step_count))
        return self.flags


class FailingModel:
    def next_action(self, _task, _observations):
        raise RuntimeError("model unavailable")


def make_solver(extractor: FakeFlagExtractor) -> TsecbenchAgentSolver:
    return TsecbenchAgentSolver(
        model=FakeModel(actions=(make_action(),)),
        executor=make_executor(),
        flag_extractor=extractor,
        task_factory=TsecbenchTaskFactory(
            allowed_capabilities=("echo",),
            max_steps=2,
            timeout_seconds=30,
        ),
    )


def test_agent_solver_runs_loop_before_extracting_flags() -> None:
    extractor = FakeFlagExtractor(("flag{local-test}",))

    flags = make_solver(extractor).solve(make_challenge(), make_started())

    assert flags == ("flag{local-test}",)
    assert extractor.calls == [("tsecbench:challenge-001", 1)]


def test_agent_solver_rejects_blank_flags() -> None:
    with pytest.raises(ValueError, match="blank flag"):
        make_solver(FakeFlagExtractor(("",))).solve(
            make_challenge(),
            make_started(),
        )


def test_agent_solver_rejects_duplicate_flags() -> None:
    with pytest.raises(ValueError, match="duplicate flags"):
        make_solver(
            FakeFlagExtractor(("flag{same}", "flag{same}")),
        ).solve(make_challenge(), make_started())


def test_agent_solver_does_not_extract_after_agent_failure() -> None:
    extractor = FakeFlagExtractor(("flag{never-submitted}",))
    solver = TsecbenchAgentSolver(
        model=FailingModel(),
        executor=make_executor(),
        flag_extractor=extractor,
        task_factory=TsecbenchTaskFactory(
            allowed_capabilities=("echo",),
        ),
    )

    with pytest.raises(RuntimeError, match="did not stop normally"):
        solver.solve(make_challenge(), make_started())

    assert extractor.calls == []
