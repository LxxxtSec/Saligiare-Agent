from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field


class TsecbenchChallenge(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    unique_code: str = Field(min_length=1)
    description: str | None = None
    difficulty: str = Field(min_length=1)
    level: int = Field(ge=0)
    total_score: int = Field(ge=0)
    flag_count: int = Field(gt=0)
    correct_flag_count: int = Field(ge=0)
    is_completed: bool
    container_status: str = Field(min_length=1)
    container_addr: tuple[str, ...] = ()


class TsecbenchStartResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    unique_code: str = Field(min_length=1)
    container_addr: tuple[str, ...] = Field(min_length=1)


class TsecbenchHintResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    unique_code: str = Field(min_length=1)
    hint: str | None = None


class TsecbenchSubmitResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    correct: bool
    awarded: int = Field(ge=0)
    cumulative_score: int = Field(ge=0)
    correct_flag_count: int = Field(ge=0)
    total_flag_count: int = Field(gt=0)
    matched_flag_index: int | None = Field(default=None, ge=0)


class TsecbenchCloseResult(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    unique_code: str = Field(min_length=1)
    closed: bool


class TsecbenchClient(Protocol):
    def list_challenges(self) -> tuple[TsecbenchChallenge, ...]:
        ...

    def start_challenge(self, unique_code: str) -> TsecbenchStartResult:
        ...

    def get_hint(self, unique_code: str) -> TsecbenchHintResult:
        ...

    def submit_flag(self, unique_code: str, flag: str) -> TsecbenchSubmitResult:
        ...

    def close_challenge(self, unique_code: str) -> TsecbenchCloseResult:
        ...


class TsecbenchSolver(Protocol):
    def solve(
        self,
        challenge: TsecbenchChallenge,
        started: TsecbenchStartResult,
    ) -> tuple[str, ...]:
        ...


class TsecbenchOfficialRunner:
    """编排官方 SDK 生命周期；网络和 VPN 由注入的 client 管理。"""

    def __init__(self, client: TsecbenchClient, solver: TsecbenchSolver) -> None:
        self._client = client
        self._solver = solver

    def run(self) -> tuple[TsecbenchSubmitResult, ...]:
        submissions: list[TsecbenchSubmitResult] = []

        for challenge in self._client.list_challenges():
            if challenge.is_completed:
                continue

            started = self._client.start_challenge(challenge.unique_code)
            try:
                flags = self._solver.solve(challenge, started)
                for flag in flags:
                    submissions.append(
                        self._client.submit_flag(challenge.unique_code, flag),
                    )
            finally:
                self._client.close_challenge(challenge.unique_code)

        return tuple(submissions)
