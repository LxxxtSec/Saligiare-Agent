from typing import Protocol

from saligiare.agent.state import RuntimeState
from saligiare.core.result import Result
from saligiare.core.task import Task


class BenchmarkTaskAdapter(Protocol):
    def load(self, payload: str) -> Task:
        ...


class BenchmarkEvaluator(Protocol):
    def evaluate(self, task: Task, state: RuntimeState, trace_id: str) -> Result:
        ...
