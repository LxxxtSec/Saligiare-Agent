from pydantic import BaseModel, ConfigDict, ValidationError

from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import Task
from saligiare.models.base import ModelRequest, TextModelProvider


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
    ) -> None:
        if not prompt_version.strip():
            raise ValueError("prompt_version must not be blank")

        self._provider = provider
        self._prompt_version = prompt_version

    def next_action(
        self,
        task: Task,
        observations: tuple[Observation, ...],
    ) -> Action | None:
        request = ModelRequest(
            task=task,
            observations=observations,
            prompt_version=self._prompt_version,
        )
        raw_response = self._provider.complete(request)

        try:
            response = StructuredActionResponse.model_validate_json(raw_response)
        except (ValidationError, ValueError) as exc:
            raise ValueError("model response is not valid structured JSON") from exc

        return response.action
