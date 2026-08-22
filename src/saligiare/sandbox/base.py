from enum import Enum
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class SandboxStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    DENIED = "denied"


class SandboxRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    argv: tuple[str, ...] = Field(min_length=1)
    cwd: str = Field(default="/workspace", min_length=1)
    timeout_seconds: int = Field(default=30, gt=0, le=3_600)
    env: dict[str, str] = Field(default_factory=dict)
    network_enabled: bool = False


class SandboxResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    status: SandboxStatus
    return_code: int | None = None
    stdout: str = Field(default="", max_length=10_000)
    stderr: str = Field(default="", max_length=10_000)
    truncated: bool = False


class Sandbox(Protocol):
    def execute(self, request: SandboxRequest) -> SandboxResult:
        ...
