import pytest

from saligiare.core.task import ApprovalLevel, Task, TaskMode
from saligiare.models.base import ModelRequest
from saligiare.models.retry import (
    PermanentProviderError,
    ProviderError,
    RetryingProvider,
    TransientProviderError,
)


def make_request() -> ModelRequest:
    return ModelRequest(
        task=Task(
            task_id="retry-task-001",
            mode=TaskMode.CTF_SOLVE,
            target="local-target",
            scope=("local-target",),
            allowed_capabilities=("artifact_read",),
            required_approval=ApprovalLevel.NONE,
            max_steps=2,
            timeout_seconds=30,
            evaluator_id="fake-evaluator",
        ),
    )


class SequenceProvider:
    def __init__(self, outcomes: list[object]) -> None:
        self._outcomes = outcomes
        self.calls = 0

    def complete(self, _request: ModelRequest) -> str:
        outcome = self._outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, BaseException):
            raise outcome
        return str(outcome)


def test_retrying_provider_retries_transient_error_then_succeeds() -> None:
    provider = SequenceProvider(
        [TransientProviderError("temporarily unavailable"), '{"action":null}'],
    )

    result = RetryingProvider(provider).complete(make_request())

    assert result == '{"action":null}'
    assert provider.calls == 2


def test_retrying_provider_stops_after_max_attempts() -> None:
    provider = SequenceProvider(
        [
            TransientProviderError("one"),
            TransientProviderError("two"),
            TransientProviderError("three"),
        ],
    )

    with pytest.raises(TransientProviderError, match="three"):
        RetryingProvider(provider, max_attempts=3).complete(make_request())

    assert provider.calls == 3


def test_retrying_provider_does_not_retry_permanent_error() -> None:
    provider = SequenceProvider([PermanentProviderError("invalid api key")])

    with pytest.raises(PermanentProviderError, match="invalid api key"):
        RetryingProvider(provider).complete(make_request())

    assert provider.calls == 1


def test_retrying_provider_does_not_retry_unclassified_error() -> None:
    provider = SequenceProvider([RuntimeError("unexpected")])

    with pytest.raises(RuntimeError, match="unexpected"):
        RetryingProvider(provider).complete(make_request())

    assert provider.calls == 1


def test_retrying_provider_requires_positive_attempt_limit() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        RetryingProvider(SequenceProvider([]), max_attempts=0)


def test_provider_error_is_a_runtime_error() -> None:
    assert issubclass(ProviderError, RuntimeError)
