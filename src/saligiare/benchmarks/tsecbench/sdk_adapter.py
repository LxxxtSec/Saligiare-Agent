import os
from collections.abc import Mapping
from types import TracebackType
from typing import Any, Self

from saligiare.benchmarks.tsecbench.official import (
    TsecbenchChallenge,
    TsecbenchClient,
    TsecbenchCloseResult,
    TsecbenchHintResult,
    TsecbenchStartResult,
    TsecbenchSubmitResult,
)


def _fields(raw: object, names: tuple[str, ...]) -> dict[str, Any]:
    if isinstance(raw, Mapping):
        return {name: raw[name] for name in names}

    return {name: getattr(raw, name) for name in names}


class TsecbenchSdkClient(TsecbenchClient):
    """把官方同步 SDK 客户端映射到 Saligiare 的严格协议模型。"""

    def __init__(self, sdk_client: object) -> None:
        self._sdk_client = sdk_client

    def __enter__(self) -> Self:
        enter = getattr(self._sdk_client, "__enter__", None)
        if enter is not None:
            enter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        exit_method = getattr(self._sdk_client, "__exit__", None)
        if exit_method is not None:
            exit_method(exc_type, exc_value, traceback)

    def list_challenges(self) -> tuple[TsecbenchChallenge, ...]:
        raw_items = self._sdk_client.list_challenges()
        names = (
            "unique_code",
            "description",
            "difficulty",
            "level",
            "total_score",
            "flag_count",
            "correct_flag_count",
            "is_completed",
            "container_status",
            "container_addr",
        )
        return tuple(
            TsecbenchChallenge.model_validate(_fields(item, names))
            for item in raw_items
        )

    def start_challenge(self, unique_code: str) -> TsecbenchStartResult:
        raw = self._sdk_client.start_challenge(unique_code)
        return TsecbenchStartResult.model_validate(
            _fields(raw, ("unique_code", "container_addr")),
        )

    def get_hint(self, unique_code: str) -> TsecbenchHintResult:
        raw = self._sdk_client.get_hint(unique_code)
        return TsecbenchHintResult.model_validate(
            _fields(raw, ("unique_code", "hint")),
        )

    def submit_flag(self, unique_code: str, flag: str) -> TsecbenchSubmitResult:
        raw = self._sdk_client.submit_flag(unique_code, flag)
        names = (
            "correct",
            "awarded",
            "cumulative_score",
            "correct_flag_count",
            "total_flag_count",
            "matched_flag_index",
        )
        return TsecbenchSubmitResult.model_validate(_fields(raw, names))

    def close_challenge(self, unique_code: str) -> TsecbenchCloseResult:
        raw = self._sdk_client.close_challenge(unique_code)
        return TsecbenchCloseResult.model_validate(
            _fields(raw, ("unique_code", "closed")),
        )


def create_sdk_client_from_environment() -> TsecbenchSdkClient:
    token = os.environ.get("BENCHMARK_TOKEN", "").strip()
    base_url = os.environ.get("BENCHMARK_BASE_URL", "").strip()
    if not token or not base_url:
        raise ValueError(
            "BENCHMARK_TOKEN and BENCHMARK_BASE_URL must be set locally"
        )

    try:
        from tsec_benchmark import TSecBenchmark
    except ImportError as exc:
        raise RuntimeError(
            "install the official SDK with: python -m pip install tsec-benchmark"
        ) from exc

    return TsecbenchSdkClient(
        TSecBenchmark(base_url=base_url, token=token),
    )
