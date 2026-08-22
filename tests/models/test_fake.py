from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.models.fake import FakeModel


def make_task() -> Task:
    return Task(
        task_id="demo-task-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-demo-target",
        scope=("local-demo-target",),
        allowed_capabilities=("artifact_read",),
        required_approval=ApprovalLevel.NONE,
        max_steps=3,
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


def test_fake_model_returns_actions_in_order() -> None:
    first = make_action("action-001", "first.txt")
    second = make_action("action-002", "second.txt")
    model = FakeModel(actions=(first, second))

    assert model.next_action(make_task(), ()) == first
    assert model.next_action(make_task(), ()) == second


def test_fake_model_returns_none_when_actions_are_exhausted() -> None:
    model = FakeModel(actions=(make_action("action-001", "only.txt"),))

    assert model.next_action(make_task(), ()) is not None
    assert model.next_action(make_task(), ()) is None


def test_fake_model_accepts_observations_without_changing_order() -> None:
    first = make_action("action-001", "first.txt")
    second = make_action("action-002", "second.txt")
    model = FakeModel(actions=(first, second))

    observation = Observation(
        observation_id="observation-001",
        action_id="action-001",
        source="artifact_read",
        status="succeeded",
        summary="读取成功",
    )

    assert model.next_action(make_task(), (observation,)) == first
    assert model.next_action(make_task(), (observation,)) == second