from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import Task


class RunStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    MAX_STEPS_REACHED = "max_steps_reached"
    MODEL_STOPPED = "model_stopped"
    POLICY_REJECTED = "policy_rejected"


class RuntimeState(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    task: Task
    status: RunStatus = RunStatus.CREATED
    step_count: int = Field(default=0, ge=0)
    actions: tuple[Action, ...] = ()
    observations: tuple[Observation, ...] = ()
    stop_reason: str | None = None

    @property
    def can_take_step(self) -> bool:
        return (
            self.status is RunStatus.RUNNING
            and self.step_count < self.task.max_steps
        )

    def start(self) -> "RuntimeState":
        if self.status is not RunStatus.CREATED:
            raise ValueError("state is not created")

        return RuntimeState(
            task=self.task,
            status=RunStatus.RUNNING,
            step_count=self.step_count,
            actions=self.actions,
            observations=self.observations,
            stop_reason=self.stop_reason,
        )

    def record_action(self, action: Action) -> "RuntimeState":
        if self.status is not RunStatus.RUNNING:
            raise ValueError("state is not running")

        if self.step_count >= self.task.max_steps:
            raise ValueError("maximum step budget reached")

        return RuntimeState(
            task=self.task,
            status=self.status,
            step_count=self.step_count + 1,
            actions=self.actions + (action,),
            observations=self.observations,
            stop_reason=self.stop_reason,
        )

    def record_observation(self, observation: Observation) -> "RuntimeState":
        if self.status is not RunStatus.RUNNING:
            raise ValueError("state is not running")

        return RuntimeState(
            task=self.task,
            status=self.status,
            step_count=self.step_count,
            actions=self.actions,
            observations=self.observations + (observation,),
            stop_reason=self.stop_reason,
        )

    def stop(self, status: RunStatus, reason: str) -> "RuntimeState":
        if self.status is not RunStatus.RUNNING:
            raise ValueError("state is not running")

        if status in {RunStatus.CREATED, RunStatus.RUNNING}:
            raise ValueError("stop status must be terminal")

        clean_reason = reason.strip()
        if not clean_reason:
            raise ValueError("stop reason must not be blank")

        return RuntimeState(
            task=self.task,
            status=status,
            step_count=self.step_count,
            actions=self.actions,
            observations=self.observations,
            stop_reason=clean_reason,
        )