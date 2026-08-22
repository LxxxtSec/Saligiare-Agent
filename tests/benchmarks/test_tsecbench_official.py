from dataclasses import dataclass, field

from saligiare.benchmarks.tsecbench.official import (
    TsecbenchChallenge,
    TsecbenchCloseResult,
    TsecbenchHintResult,
    TsecbenchOfficialRunner,
    TsecbenchStartResult,
    TsecbenchSubmitResult,
)


def make_challenge(code: str, completed: bool = False) -> TsecbenchChallenge:
    return TsecbenchChallenge(
        unique_code=code,
        description="本地授权测试题",
        difficulty="easy",
        level="normal",
        total_score=100,
        flag_count=1,
        correct_flag_count=1 if completed else 0,
        is_completed=completed,
        container_status="stopped",
    )


@dataclass
class FakeOfficialClient:
    challenges: tuple[TsecbenchChallenge, ...]
    started: list[str] = field(default_factory=list)
    submitted: list[tuple[str, str]] = field(default_factory=list)
    closed: list[str] = field(default_factory=list)

    def list_challenges(self) -> tuple[TsecbenchChallenge, ...]:
        return self.challenges

    def start_challenge(self, unique_code: str) -> TsecbenchStartResult:
        self.started.append(unique_code)
        return TsecbenchStartResult(
            unique_code=unique_code,
            container_addr=("10.0.0.10:8080",),
        )

    def get_hint(self, unique_code: str) -> TsecbenchHintResult:
        return TsecbenchHintResult(unique_code=unique_code, hint=None)

    def submit_flag(self, unique_code: str, flag: str) -> TsecbenchSubmitResult:
        self.submitted.append((unique_code, flag))
        return TsecbenchSubmitResult(
            correct=True,
            awarded=100,
            cumulative_score=100,
            correct_flag_count=1,
            total_flag_count=1,
            matched_flag_index=0,
        )

    def close_challenge(self, unique_code: str) -> TsecbenchCloseResult:
        self.closed.append(unique_code)
        return TsecbenchCloseResult(unique_code=unique_code, closed=True)


class FakeSolver:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def solve(
        self,
        challenge: TsecbenchChallenge,
        started: TsecbenchStartResult,
    ) -> tuple[str, ...]:
        self.calls.append((challenge.unique_code, started.container_addr))
        return ("flag{authorized-local-test}",)


def test_official_runner_follows_sdk_lifecycle_and_skips_completed() -> None:
    client = FakeOfficialClient(
        challenges=(make_challenge("todo-001"), make_challenge("done-001", True)),
    )
    solver = FakeSolver()

    results = TsecbenchOfficialRunner(client, solver).run()

    assert len(results) == 1
    assert client.started == ["todo-001"]
    assert client.submitted == [("todo-001", "flag{authorized-local-test}")]
    assert client.closed == ["todo-001"]
    assert solver.calls == [("todo-001", ("10.0.0.10:8080",))]


def test_official_runner_closes_container_when_solver_fails() -> None:
    client = FakeOfficialClient(challenges=(make_challenge("fail-001"),))

    class FailingSolver:
        def solve(
            self,
            _challenge: TsecbenchChallenge,
            _started: TsecbenchStartResult,
        ) -> tuple[str, ...]:
            raise RuntimeError("solver failed")

    try:
        TsecbenchOfficialRunner(client, FailingSolver()).run()
    except RuntimeError as exc:
        assert str(exc) == "solver failed"
    else:
        raise AssertionError("expected solver failure")

    assert client.closed == ["fail-001"]
