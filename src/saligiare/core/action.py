from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Action(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    action_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    parent_observation_ids: tuple[str, ...] = ()
    requested_capability: str = Field(min_length=1)
    reason: str = Field(min_length=1)