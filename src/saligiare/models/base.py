from typing import Protocol

from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import Task


class ModelAdapter(Protocol):
    def next_action(
        self,
        task: Task,
        observations: tuple[Observation, ...],
    ) -> Action | None:
        ...