import pytest

from saligiare.agent.state import RunStatus, RuntimeState
from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import ApprovalLevel, Task, TaskMode


def make_task(max_steps: int = 2) -> Task:
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


def make_action(action_id: str) -> Action:
    return Action(
        action_id=action_id,
        tool_name="artifact_read",
        arguments={"path": "challenge.txt"},
        requested_capability="artifact_read",
        reason="读取任务附件",
    )


def make_observation(observation_id: str, action_id: str) -> Observation:
    return Observation(
        observation_id=observation_id,
        action_id=action_id,
        source="artifact_read",
        status="succeeded",
        summary="读取成功",
    )


def test_state_starts_as_created() -> None:
    state = RuntimeState(task=make_task())

    assert state.status is RunStatus.CREATED
    assert state.step_count == 0
    assert state.can_take_step is False


def test_state_can_start_and_record_action() -> None:
    state = RuntimeState(task=make_task()).start()
    action = make_action("action-001")

    state = state.record_action(action)

    assert state.status is RunStatus.RUNNING
    assert state.step_count == 1
    assert state.actions == (action,)
    assert state.can_take_step is True


def test_state_records_observation() -> None:
    state = RuntimeState(task=make_task()).start()
    action = make_action("action-001")
    observation = make_observation("observation-001", action.action_id)

    state = state.record_action(action)
    state = state.record_observation(observation)

    assert state.observations == (observation,)


def test_state_respects_max_steps() -> None:
    state = RuntimeState(task=make_task(max_steps=1)).start()
    state = state.record_action(make_action("action-001"))

    assert state.step_count == 1
    assert state.can_take_step is False

    with pytest.raises(ValueError, match="maximum step budget"):
        state.record_action(make_action("action-002"))


def test_stopped_state_cannot_record_more_data() -> None:
    state = RuntimeState(task=make_task()).start()
    state = state.stop(RunStatus.COMPLETED, "任务完成")

    with pytest.raises(ValueError, match="not running"):
        state.record_action(make_action("action-001"))

    with pytest.raises(ValueError, match="not running"):
        state.record_observation(
            make_observation("observation-001", "action-001"),
        )
