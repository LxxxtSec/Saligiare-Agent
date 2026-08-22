from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class ResultStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    INCOMPLETE = "incomplete"


class EvaluationVerdict(str, Enum):
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    INCONCLUSIVE = "inconclusive"


class Result(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    task_id: str = Field(min_length=1)
    status: ResultStatus
    candidate_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    evaluator_verdict: EvaluationVerdict | None = None
    trace_id: str = Field(min_length=1)
    budget_usage: dict[str, int] = Field(default_factory=dict)