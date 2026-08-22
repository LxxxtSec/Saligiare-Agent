from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskMode(str, Enum):
    CTF_SOLVE = "ctf_solve"
    VULN_REPRODUCE = "vuln_reproduce"
    SOURCE_AUDIT = "source_audit"
    EXPLOIT_VALIDATE = "exploit_validate"
    SRC_ASSESS = "src_assess"


class ApprovalLevel(str, Enum):
    NONE = "none"
    LOCAL_SANDBOX = "local_sandbox"
    DEDICATED_VM = "dedicated_vm"
    HUMAN_APPROVAL = "human_approval"


class Task(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    task_id: str = Field(min_length=1)
    mode: TaskMode
    target: str = Field(min_length=1)
    scope: tuple[str, ...] = Field(min_length=1)
    allowed_capabilities: tuple[str, ...] = Field(min_length=1)
    required_approval: ApprovalLevel
    max_steps: int = Field(gt=0, le=100_000)
    timeout_seconds: int = Field(gt=0, le=86_400)
    evaluator_id: str = Field(min_length=1)
    metadata: dict[str, str] = Field(default_factory=dict)