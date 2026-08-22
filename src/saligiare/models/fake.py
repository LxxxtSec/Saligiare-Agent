from saligiare.core.action import Action
from saligiare.core.observation import Observation
from saligiare.core.task import Task


class FakeModel:
    def __init__(self, actions: tuple[Action, ...]) -> None:
        self._actions = tuple(actions)
        self._index = 0

    def next_action(
        self,
        _task: Task,
        _observations: tuple[Observation, ...],
    ) -> Action | None:
        if self._index >= len(self._actions):
            return None

        action = self._actions[self._index]
        self._index += 1
        return action