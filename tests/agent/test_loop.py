from saligiare.agent.loop import AgentLoop
from saligiare.agent.state import RunStatus
from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.models.fake import FakeModel


def make_task(max_steps: int = 3) -> Task:
    return Task(
        task_id="demo-task-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-demo-target",
        scope=("local-demo-target",),
        allowed_capabilities=("artifact_read",),
        required_approval=ApprovalLevel.NONE,
        max_steps=max_steps,
        timeout_seconds=60,
        evaluator_id="fake-evaluator",
    )


def make_action(action_id: str, path: str) -> Action:
    return Action(
        action_id=action_id,
        tool_name="artifact_read",
        arguments={"path": path},
        requested_capability="artifact_read",
        reason="读取任务附件",
    )


class FakeExecutor:
    def run(
        self,
        task: Task,
        action: Action,
    ) -> Observation:
        return Observation(
            observation_id=f"observation-for-{action.action_id}",
            action_id=action.action_id,
            source=action.tool_name,
            status="succeeded",
            summary=f"已读取 {action.arguments['path']}",
        )


class FailingExecutor:
    def run(
        self,
        task: Task,
        action: Action,
    ) -> Observation:
        raise RuntimeError("synthetic executor failure")


def test_loop_stops_when_model_has_no_more_actions() -> None:
    model = FakeModel(
        actions=(
            make_action("action-001", "first.txt"),
            make_action("action-002", "second.txt"),
        ),
    )
    loop = AgentLoop(model=model, executor=FakeExecutor())

    state = loop.run(make_task())

    assert state.status is RunStatus.MODEL_STOPPED
    assert state.step_count == 2
    assert len(state.actions) == 2
    assert len(state.observations) == 2
    assert state.stop_reason == "model returned no more actions"


def test_loop_stops_at_maximum_step_budget() -> None:
    model = FakeModel(
        actions=(
            make_action("action-001", "first.txt"),
            make_action("action-002", "second.txt"),
            make_action("action-003", "third.txt"),
        ),
    )
    loop = AgentLoop(model=model, executor=FakeExecutor())

    state = loop.run(make_task(max_steps=2))

    assert state.status is RunStatus.MAX_STEPS_REACHED
    assert state.step_count == 2
    assert len(state.actions) == 2
    assert len(state.observations) == 2


def test_loop_stops_when_executor_fails() -> None:
    model = FakeModel(
        actions=(make_action("action-001", "first.txt"),),
    )
    loop = AgentLoop(model=model, executor=FailingExecutor())

    state = loop.run(make_task())

    assert state.status is RunStatus.FAILED
    assert state.step_count == 1
    assert len(state.actions) == 1
    assert state.observations == ()
    assert "synthetic executor failure" in (state.stop_reason or "")