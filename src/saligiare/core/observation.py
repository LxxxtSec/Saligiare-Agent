from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ObservationStatus(str, Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


class Observation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    observation_id: str = Field(min_length=1)
    action_id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    status: ObservationStatus
    summary: str = Field(min_length=1, max_length=4_000)
    raw_ref: str | None = None
    truncated: bool = False
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )