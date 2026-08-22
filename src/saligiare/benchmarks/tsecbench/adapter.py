import json

from pydantic import BaseModel, ConfigDict, ValidationError

from saligiare.core.task import Task


class TsecbenchLocalCase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    task: Task
    expected_observation_summaries: tuple[str, ...] = ()
    candidate_refs: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()


class TsecbenchTaskAdapter:
    """解析 Saligiare 的本地夹具格式，不绑定线上平台实现。"""

    def load_case(self, payload: str) -> TsecbenchLocalCase:
        try:
            return TsecbenchLocalCase.model_validate_json(payload)
        except (ValidationError, ValueError) as exc:
            raise ValueError("invalid TSECBENCH local case JSON") from exc

    def load(self, payload: str) -> Task:
        return self.load_case(payload).task

    @staticmethod
    def dump_case(case: TsecbenchLocalCase) -> str:
        return json.dumps(
            case.model_dump(mode="json"),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
