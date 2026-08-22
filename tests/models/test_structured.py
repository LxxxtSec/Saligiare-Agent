import pytest

from saligiare.core.action import Action
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.models.base import ModelRequest
from saligiare.models.provider import FakeProvider
from saligiare.models.structured import StructuredActionModel


def make_task() -> Task:
    return Task(
        task_id="model-task-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-target",
        scope=("local-target",),
        allowed_capabilities=("artifact_read",),
        required_approval=ApprovalLevel.NONE,
        max_steps=3,
        timeout_seconds=60,
        evaluator_id="fake-evaluator",
    )


def action_json(action_id: str = "action-001") -> str:
    return (
        '{"action":{"action_id":"'
        + action_id
        + '","tool_name":"artifact_read","arguments":{"path":"a.txt"},'
        '"parent_observation_ids":[],"requested_capability":"artifact_read",'
        '"reason":"读取任务附件"}}'
    )


def test_structured_model_converts_json_to_action() -> None:
    provider = FakeProvider((action_json(),))
    model = StructuredActionModel(provider, prompt_version="security-v1")

    action = model.next_action(make_task(), ())

    assert isinstance(action, Action)
    assert action.action_id == "action-001"
    assert provider.requests[0].prompt_version == "security-v1"


def test_structured_model_supports_explicit_stop_response() -> None:
    model = StructuredActionModel(FakeProvider(('{"action":null}',)))

    assert model.next_action(make_task(), ()) is None


def test_structured_model_rejects_invalid_json() -> None:
    model = StructuredActionModel(FakeProvider(("not-json",)))

    with pytest.raises(ValueError, match="structured JSON"):
        model.next_action(make_task(), ())


def test_structured_model_rejects_unknown_response_fields() -> None:
    model = StructuredActionModel(
        FakeProvider(('{"action":null,"unexpected":"value"}',)),
    )

    with pytest.raises(ValueError, match="structured JSON"):
        model.next_action(make_task(), ())


def test_fake_provider_records_requests_and_fails_when_exhausted() -> None:
    provider = FakeProvider(("{\"action\":null}",))
    request = ModelRequest(task=make_task())

    assert provider.complete(request) == '{"action":null}'
    assert provider.requests == (request,)

    with pytest.raises(RuntimeError, match="exhausted"):
        provider.complete(request)
