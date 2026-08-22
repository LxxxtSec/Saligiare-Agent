from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ToolResultStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ToolSpec(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    name: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    description: str = Field(min_length=1)


class ToolResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    status: ToolResultStatus
    summary: str = Field(min_length=1, max_length=4_000)
    data: dict[str, Any] = Field(default_factory=dict)