import pytest
from pydantic import ValidationError

from saligiare.core.result import (
    EvaluationVerdict,
    Result,
    ResultStatus,
)


def make_valid_result(**overrides: object) -> Result:
    values: dict[str, object] = {
        "task_id": "demo-task-001",
        "status": ResultStatus.COMPLETED,
        "candidate_refs": ("candidate-001",),
        "evidence_refs": ("evidence-001",),
        "evaluator_verdict": EvaluationVerdict.INCONCLUSIVE,
        "trace_id": "run-001",
        "budget_usage": {
            "steps": 2,
            "tokens": 100,
        },
    }
    values.update(overrides)
    return Result(**values)


def test_result_accepts_valid_values() -> None:
    result = make_valid_result()

    assert result.task_id == "demo-task-001"
    assert result.status is ResultStatus.COMPLETED
    assert result.evaluator_verdict is EvaluationVerdict.INCONCLUSIVE
    assert result.budget_usage["steps"] == 2


def test_result_has_inconclusive_verdict_by_default() -> None:
    result = make_valid_result(evaluator_verdict=None)

    assert result.evaluator_verdict is None


def test_result_rejects_unknown_status_and_verdict() -> None:
    with pytest.raises(ValidationError):
        make_valid_result(status="running")

    with pytest.raises(ValidationError):
        make_valid_result(evaluator_verdict="maybe")


def test_result_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        make_valid_result(solved=True)


def test_result_is_frozen_at_the_top_level() -> None:
    result = make_valid_result()

    with pytest.raises(ValidationError):
        result.status = ResultStatus.FAILED