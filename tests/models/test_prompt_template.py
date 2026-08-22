from datetime import UTC, datetime

from saligiare.core.observation import Observation
from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.prompts.template import PromptTemplate


def make_task() -> Task:
    return Task(
        task_id="prompt-task-001",
        mode=TaskMode.CTF_SOLVE,
        target="local-target",
        scope=("local-target",),
        allowed_capabilities=("artifact_read",),
        required_approval=ApprovalLevel.NONE,
        max_steps=3,
        timeout_seconds=60,
        evaluator_id="fake-evaluator",
    )


def test_prompt_template_renders_version_task_and_observations() -> None:
    template = PromptTemplate(
        version="security-v2",
        system_instruction="Return a JSON action.",
    )
    observation = Observation(
        observation_id="observation-001",
        action_id="action-001",
        source="artifact_read",
        status="succeeded",
        summary="读取完成",
        created_at=datetime(2026, 8, 22, tzinfo=UTC),
    )

    prompt = template.render(make_task(), (observation,))

    assert prompt.startswith("Return a JSON action.\n\nContext JSON:")
    assert '"prompt_version":"security-v2"' in prompt
    assert '"task_id":"prompt-task-001"' in prompt
    assert '"observation_id":"observation-001"' in prompt


def test_prompt_template_render_is_deterministic() -> None:
    template = PromptTemplate(
        version="security-v1",
        system_instruction="Return JSON.",
    )

    first = template.render(make_task(), ())
    second = template.render(make_task(), ())

    assert first == second
