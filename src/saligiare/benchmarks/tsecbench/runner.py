from pathlib import Path

from saligiare.agent.loop import ActionExecutor, AgentLoop
from saligiare.agent.state import RuntimeState
from saligiare.benchmarks.tsecbench.adapter import TsecbenchTaskAdapter
from saligiare.benchmarks.tsecbench.evaluator import TsecbenchEvaluator
from saligiare.core.result import Result
from saligiare.models.base import ModelAdapter


class TsecbenchRunner:
    def __init__(
        self,
        model: ModelAdapter,
        executor: ActionExecutor,
        adapter: TsecbenchTaskAdapter | None = None,
        evaluator: TsecbenchEvaluator | None = None,
    ) -> None:
        self._model = model
        self._executor = executor
        self._adapter = adapter or TsecbenchTaskAdapter()
        self._evaluator = evaluator or TsecbenchEvaluator()

    def run(self, payload: str, trace_id: str) -> tuple[RuntimeState, Result]:
        case = self._adapter.load_case(payload)
        state = AgentLoop(
            model=self._model,
            executor=self._executor,
        ).run(case.task)
        result = self._evaluator.evaluate(case, state, trace_id)
        return state, result

    def run_file(
        self,
        input_path: Path,
        output_path: Path,
        trace_id: str,
    ) -> Result:
        case = self._adapter.load_path(input_path)
        state = AgentLoop(
            model=self._model,
            executor=self._executor,
        ).run(case.task)
        result = self._evaluator.evaluate(case, state, trace_id)

        try:
            output_path.write_text(
                result.model_dump_json() + "\n",
                encoding="utf-8",
            )
        except OSError as exc:
            raise ValueError(
                f"unable to write TSECBENCH local result: {output_path}"
            ) from exc

        return result
from pathlib import Path
