from pydantic import BaseModel, ConfigDict, ValidationError

from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import Task
from saligiare.models.base import ModelRequest, TextModelProvider
from saligiare.prompts.template import (
    DEFAULT_SYSTEM_INSTRUCTION,
    PromptTemplate,
)


class StructuredActionResponse(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    action: Action | None = None


class StructuredActionModel:
    def __init__(
        self,
        provider: TextModelProvider,
        prompt_version: str = "v1",
        prompt_template: PromptTemplate | None = None,
    ) -> None:
        if not prompt_version.strip():
            raise ValueError("prompt_version must not be blank")

        self._provider = provider
        self._prompt_template = prompt_template or PromptTemplate(
            version=prompt_version,
            system_instruction=DEFAULT_SYSTEM_INSTRUCTION,
        )

    def next_action(
        self,
        task: Task,
        observations: tuple[Observation, ...],
    ) -> Action | None:
        request = ModelRequest(
            task=task,
            observations=observations,
            prompt_version=self._prompt_template.version,
            prompt=self._prompt_template.render(task, observations),
        )
        raw_response = self._provider.complete(request)

        try:
            response = StructuredActionResponse.model_validate_json(raw_response)
        except (ValidationError, ValueError) as exc:
            raise ValueError("model response is not valid structured JSON") from exc

        return response.action
