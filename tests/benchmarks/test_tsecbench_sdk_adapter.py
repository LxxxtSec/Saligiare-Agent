from dataclasses import dataclass
from typing import Self

import pytest

from saligiare.benchmarks.tsecbench.sdk_adapter import TsecbenchSdkClient


@dataclass
class RawChallenge:
    unique_code: str = "challenge-001"
    description: str | None = "授权测试题"
    difficulty: str = "easy"
    level: int = 1
    total_score: int = 100
    flag_count: int = 1
    correct_flag_count: int = 0
    is_completed: bool = False
    container_status: str = "stopped"
    container_addr: list[str] | None = None

    def __post_init__(self) -> None:
        if self.container_addr is None:
            self.container_addr = []


@dataclass
class RawStart:
    unique_code: str = "challenge-001"
    container_addr: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.container_addr is None:
            self.container_addr = ["10.0.0.10:8080"]


@dataclass
class RawHint:
    unique_code: str = "challenge-001"
    hint: str | None = None


@dataclass
class RawSubmit:
    correct: bool = True
    awarded: int = 100
    cumulative_score: int = 100
    correct_flag_count: int = 1
    total_flag_count: int = 1
    matched_flag_index: int | None = 0


@dataclass
class RawClose:
    unique_code: str = "challenge-001"
    closed: bool = True


class RawSdkClient:
    def __init__(self) -> None:
        self.entered = False
        self.exited = False

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(self, *_args: object) -> None:
        self.exited = True

    def list_challenges(self) -> list[RawChallenge]:
        return [RawChallenge()]

    def start_challenge(self, _unique_code: str) -> RawStart:
        return RawStart()

    def get_hint(self, _unique_code: str) -> RawHint:
        return RawHint()

    def submit_flag(self, _unique_code: str, _flag: str) -> RawSubmit:
        return RawSubmit()

    def close_challenge(self, _unique_code: str) -> RawClose:
        return RawClose()


def test_sdk_adapter_maps_official_sdk_data_classes() -> None:
    raw_client = RawSdkClient()

    with TsecbenchSdkClient(raw_client) as client:
        challenge = client.list_challenges()[0]
        started = client.start_challenge(challenge.unique_code)
        hint = client.get_hint(challenge.unique_code)
        submitted = client.submit_flag(challenge.unique_code, "flag{test}")
        closed = client.close_challenge(challenge.unique_code)

    assert challenge.unique_code == "challenge-001"
    assert started.container_addr == ("10.0.0.10:8080",)
    assert hint.hint is None
    assert submitted.correct is True
    assert closed.closed is True
    assert raw_client.entered is True
    assert raw_client.exited is True


def test_sdk_adapter_accepts_null_description_and_rejects_invalid_flag_length() -> None:
    raw_client = RawSdkClient()
    raw_client.list_challenges = lambda: [RawChallenge(description=None)]

    with TsecbenchSdkClient(raw_client) as client:
        assert client.list_challenges()[0].description is None
        with pytest.raises(ValueError, match="between 1 and 4096"):
            client.submit_flag("challenge-001", "")
