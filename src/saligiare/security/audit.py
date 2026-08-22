from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AuditEventType(str, Enum):
    POLICY_DECISION = "policy_decision"
    TOOL_EXECUTION = "tool_execution"
    MODEL_ACTION = "model_action"


class AuditEvent(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    event_id: str = Field(min_length=1)
    event_type: AuditEventType
    action_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    decision: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
    )


class AuditLog:
    def __init__(self) -> None:
        self._events: dict[str, AuditEvent] = {}

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events.values())

    def append(self, event: AuditEvent) -> None:
        if event.event_id in self._events:
            raise ValueError(f"audit event already exists: {event.event_id}")

        self._events[event.event_id] = event