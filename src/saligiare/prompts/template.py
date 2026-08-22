import json

from pydantic import BaseModel, ConfigDict, Field

from saligiare.core.observation import Observation
from saligiare.core.task import Task

DEFAULT_SYSTEM_INSTRUCTION = (
    "You are Saligiare, an authorized security benchmark agent. "
    "Return exactly one JSON object with an 'action' field. "
    "The field must contain a validated action or null when stopping."
)


class PromptTemplate(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    version: str = Field(min_length=1)
    system_instruction: str = Field(min_length=1)

    def render(
        self,
        task: Task,
        observations: tuple[Observation, ...],
    ) -> str:
        context = {
            "prompt_version": self.version,
            "task": task.model_dump(mode="json"),
            "observations": [
                observation.model_dump(mode="json")
                for observation in observations
            ],
        }
        serialized_context = json.dumps(
            context,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        return f"{self.system_instruction}\n\nContext JSON:\n{serialized_context}"
