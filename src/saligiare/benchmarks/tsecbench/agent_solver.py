from typing import Protocol

from saligiare.agent.loop import ActionExecutor, AgentLoop
from saligiare.agent.state import RunStatus, RuntimeState
from saligiare.benchmarks.tsecbench.official import (
    TsecbenchChallenge,
    TsecbenchSolver,
    TsecbenchStartResult,
)
from saligiare.benchmarks.tsecbench.task_factory import TsecbenchTaskFactory
from saligiare.core.task import Task
from saligiare.models.base import ModelAdapter


class TsecbenchFlagExtractor(Protocol):
    def extract(self, task: Task, state: RuntimeState) -> tuple[str, ...]:
        ...


class TsecbenchAgentSolver(TsecbenchSolver):
    """使用 Saligiare AgentLoop 解题，并要求显式注入 flag 提取器。"""

    def __init__(
        self,
        model: ModelAdapter,
        executor: ActionExecutor,
        flag_extractor: TsecbenchFlagExtractor,
        task_factory: TsecbenchTaskFactory | None = None,
    ) -> None:
        self._model = model
        self._executor = executor
        self._flag_extractor = flag_extractor
        self._task_factory = task_factory or TsecbenchTaskFactory()

    def solve(
        self,
        challenge: TsecbenchChallenge,
        started: TsecbenchStartResult,
    ) -> tuple[str, ...]:
        task = self._task_factory.build(challenge, started)
        state = AgentLoop(
            model=self._model,
            executor=self._executor,
        ).run(task)

        if state.status is not RunStatus.MODEL_STOPPED:
            raise RuntimeError(
                f"agent did not stop normally: {state.status.value}"
            )

        flags = self._flag_extractor.extract(task, state)
        cleaned_flags = tuple(flag.strip() for flag in flags)
        if any(not flag for flag in cleaned_flags):
            raise ValueError("flag extractor returned a blank flag")
        if len(set(cleaned_flags)) != len(cleaned_flags):
            raise ValueError("flag extractor returned duplicate flags")

        return cleaned_flags
