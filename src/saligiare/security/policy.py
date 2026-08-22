from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from saligiare.core.action import Action
from saligiare.core.task import Task
from saligiare.security.audit import (
    AuditEvent,
    AuditEventType,
    AuditLog,
)
from saligiare.tools.registry import ToolRegistry


class PolicyDecisionStatus(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"


class PolicyDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    status: PolicyDecisionStatus
    action_id: str = Field(min_length=1)
    tool_name: str = Field(min_length=1)
    reason: str = Field(min_length=1)

    @property
    def allowed(self) -> bool:
        return self.status is PolicyDecisionStatus.ALLOWED


class PolicyGuard:
    def __init__(
        self,
        registry: ToolRegistry,
        audit_log: AuditLog | None = None,
    ) -> None:
        self._registry = registry
        self._audit_log = audit_log

    def _decision(
        self,
        action: Action,
        status: PolicyDecisionStatus,
        reason: str,
    ) -> PolicyDecision:
        decision = PolicyDecision(
            status=status,
            action_id=action.action_id,
            tool_name=action.tool_name,
            reason=reason,
        )

        if self._audit_log is not None:
            event_id = (
                f"policy-{action.action_id}-"
                f"{len(self._audit_log.events) + 1}"
            )
            self._audit_log.append(
                AuditEvent(
                    event_id=event_id,
                    event_type=AuditEventType.POLICY_DECISION,
                    action_id=action.action_id,
                    tool_name=action.tool_name,
                    decision=decision.status.value,
                    reason=decision.reason,
                ),
            )

        return decision

    def check(self, task: Task, action: Action) -> PolicyDecision:
        try:
            tool = self._registry.get(action.tool_name)
        except KeyError:
            return self._decision(
                action,
                PolicyDecisionStatus.DENIED,
                f"unknown tool: {action.tool_name}",
            )

        if action.requested_capability not in task.allowed_capabilities:
            return self._decision(
                action,
                PolicyDecisionStatus.DENIED,
                (
                    "requested capability is not allowed by task: "
                    f"{action.requested_capability}"
                ),
            )

        if tool.capability != action.requested_capability:
            return self._decision(
                action,
                PolicyDecisionStatus.DENIED,
                (
                    "action capability does not match tool capability: "
                    f"{action.requested_capability} != {tool.capability}"
                ),
            )

        if tool.capability not in task.allowed_capabilities:
            return self._decision(
                action,
                PolicyDecisionStatus.DENIED,
                (
                    "tool capability is not allowed by task: "
                    f"{tool.capability}"
                ),
            )

        return self._decision(
            action,
            PolicyDecisionStatus.ALLOWED,
            "tool and capability are allowed",
        )