from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from saligiare.core.action import Action
from saligiare.core.task import Task
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
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def check(self, task: Task, action: Action) -> PolicyDecision:
        try:
            tool = self._registry.get(action.tool_name)
        except KeyError:
            return PolicyDecision(
                status=PolicyDecisionStatus.DENIED,
                action_id=action.action_id,
                tool_name=action.tool_name,
                reason=f"unknown tool: {action.tool_name}",
            )

        if action.requested_capability not in task.allowed_capabilities:
            return PolicyDecision(
                status=PolicyDecisionStatus.DENIED,
                action_id=action.action_id,
                tool_name=action.tool_name,
                reason=(
                    "requested capability is not allowed by task: "
                    f"{action.requested_capability}"
                ),
            )

        if tool.capability != action.requested_capability:
            return PolicyDecision(
                status=PolicyDecisionStatus.DENIED,
                action_id=action.action_id,
                tool_name=action.tool_name,
                reason=(
                    "action capability does not match tool capability: "
                    f"{action.requested_capability} != {tool.capability}"
                ),
            )

        if tool.capability not in task.allowed_capabilities:
            return PolicyDecision(
                status=PolicyDecisionStatus.DENIED,
                action_id=action.action_id,
                tool_name=action.tool_name,
                reason=(
                    "tool capability is not allowed by task: "
                    f"{tool.capability}"
                ),
            )

        return PolicyDecision(
            status=PolicyDecisionStatus.ALLOWED,
            action_id=action.action_id,
            tool_name=action.tool_name,
            reason="tool and capability are allowed",
        )