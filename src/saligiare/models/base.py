from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import Task


class ModelRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    task: Task
    observations: tuple[Observation, ...] = ()
    prompt_version: str = Field(default="v1", min_length=1)
    prompt: str = Field(default="", max_length=100_000)


class TextModelProvider(Protocol):
    def complete(self, request: ModelRequest) -> str:
        ...


class ModelAdapter(Protocol):
    def next_action(
        self,
        task: Task,
        observations: tuple[Observation, ...],
    ) -> Action | None:
        ...
