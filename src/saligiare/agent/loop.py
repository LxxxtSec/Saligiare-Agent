from typing import Protocol

from saligiare.agent.state import RunStatus, RuntimeState
from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import Task
from saligiare.models.base import ModelAdapter


class ActionExecutor(Protocol):
    def execute(self, action: Action) -> Observation:
        ...


class AgentLoop:
    def __init__(
        self,
        model: ModelAdapter,
        executor: ActionExecutor,
    ) -> None:
        self._model = model
        self._executor = executor

    def run(self, task: Task) -> RuntimeState:
        state = RuntimeState(task=task).start()

        while state.can_take_step:
            try:
                action = self._model.next_action(
                    task,
                    state.observations,
                )
            except (RuntimeError, ValueError) as exc:
                return state.stop(
                    RunStatus.FAILED,
                    f"model failure: {exc}",
                )

            if action is None:
                return state.stop(
                    RunStatus.MODEL_STOPPED,
                    "model returned no more actions",
                )

            try:
                state = state.record_action(action)
                observation = self._executor.execute(action)
            except (RuntimeError, ValueError) as exc:
                return state.stop(
                    RunStatus.FAILED,
                    str(exc),
                )

            state = state.record_observation(observation)

        return state.stop(
            RunStatus.MAX_STEPS_REACHED,
            "maximum step budget reached",
        )