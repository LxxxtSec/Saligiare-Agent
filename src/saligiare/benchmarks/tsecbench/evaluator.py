from saligiare.agent.state import RunStatus, RuntimeState
from saligiare.benchmarks.tsecbench.adapter import TsecbenchLocalCase
from saligiare.core.result import (
    EvaluationVerdict,
    Result,
    ResultStatus,
)


class TsecbenchEvaluator:
    def evaluate(
        self,
        case: TsecbenchLocalCase,
        state: RuntimeState,
        trace_id: str,
    ) -> Result:
        summaries = {observation.summary for observation in state.observations}
        expected = set(case.expected_observation_summaries)
        accepted = (
            state.status is RunStatus.MODEL_STOPPED
            and expected.issubset(summaries)
        )

        if accepted:
            status = ResultStatus.COMPLETED
            verdict = EvaluationVerdict.ACCEPTED
        elif state.status is RunStatus.FAILED:
            status = ResultStatus.FAILED
            verdict = EvaluationVerdict.REJECTED
        else:
            status = ResultStatus.INCOMPLETE
            verdict = EvaluationVerdict.INCONCLUSIVE

        return Result(
            task_id=case.task.task_id,
            status=status,
            candidate_refs=case.candidate_refs,
            evidence_refs=case.evidence_refs,
            evaluator_verdict=verdict,
            trace_id=trace_id,
            budget_usage={
                "steps": state.step_count,
                "max_steps": case.task.max_steps,
            },
        )
