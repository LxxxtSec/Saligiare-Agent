from pydantic import ValidationError

from saligiare.core.action import Action
from saligiare.core.observation import Observation, ObservationStatus
from saligiare.core.task import Task
from saligiare.security.audit import (
    AuditEvent,
    AuditEventType,
    AuditLog,
)
from saligiare.security.policy import (
    PolicyDecisionStatus,
    PolicyGuard,
)
from saligiare.tools.base import Tool, ToolResultStatus


class ToolRunner:
    def __init__(
        self,
        policy_guard: PolicyGuard,
        tools: dict[str, Tool],
        audit_log: AuditLog | None = None,
    ) -> None:
        self._policy_guard = policy_guard
        self._tools = dict(tools)
        self._audit_log = audit_log

    def _observation(
        self,
        action: Action,
        status: ObservationStatus,
        summary: str,
    ) -> Observation:
        return Observation(
            observation_id=f"observation-for-{action.action_id}",
            action_id=action.action_id,
            source=action.tool_name,
            status=status,
            summary=summary,
        )

    def _record_execution(
        self,
        action: Action,
        status: str,
        reason: str,
    ) -> None:
        if self._audit_log is None:
            return

        event_id = (
            f"tool-{action.action_id}-"
            f"{len(self._audit_log.events) + 1}"
        )
        self._audit_log.append(
            AuditEvent(
                event_id=event_id,
                event_type=AuditEventType.TOOL_EXECUTION,
                action_id=action.action_id,
                tool_name=action.tool_name,
                decision=status,
                reason=reason,
            ),
        )

    def run(self, task: Task, action: Action) -> Observation:
        decision = self._policy_guard.check(task, action)

        if decision.status is PolicyDecisionStatus.DENIED:
            self._record_execution(
                action,
                "denied",
                decision.reason,
            )
            return self._observation(
                action,
                ObservationStatus.FAILED,
                f"policy denied: {decision.reason}",
            )

        tool = self._tools.get(action.tool_name)
        if tool is None:
            reason = f"tool implementation missing: {action.tool_name}"
            self._record_execution(action, "failed", reason)
            return self._observation(
                action,
                ObservationStatus.FAILED,
                reason,
            )

        try:
            result = tool.execute(action.arguments)
        except (ValidationError, RuntimeError, ValueError) as exc:
            reason = f"tool execution failed: {exc}"
            self._record_execution(action, "failed", reason)
            return self._observation(
                action,
                ObservationStatus.FAILED,
                reason,
            )

        status = (
            ObservationStatus.SUCCEEDED
            if result.status is ToolResultStatus.SUCCEEDED
            else ObservationStatus.FAILED
        )

        self._record_execution(
            action,
            result.status.value,
            result.summary,
        )

        return self._observation(
            action,
            status,
            result.summary,
        )