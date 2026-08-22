import pytest
from pydantic import ValidationError

from saligiare.sandbox.base import SandboxRequest, SandboxResult, SandboxStatus
from saligiare.sandbox.fake import FakeSandbox


def make_request(**overrides: object) -> SandboxRequest:
    values: dict[str, object] = {
        "argv": ("printf", "hello"),
        "cwd": "/workspace",
        "timeout_seconds": 10,
        "env": {},
        "network_enabled": False,
    }
    values.update(overrides)
    return SandboxRequest(**values)


def test_request_uses_argument_vector_and_safe_defaults() -> None:
    request = SandboxRequest(argv=("printf", "hello"))

    assert request.argv == ("printf", "hello")
    assert request.cwd == "/workspace"
    assert request.network_enabled is False


def test_request_rejects_empty_argv_and_invalid_timeout() -> None:
    with pytest.raises(ValidationError):
        make_request(argv=())

    with pytest.raises(ValidationError):
        make_request(timeout_seconds=0)


def test_request_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        make_request(shell=True)


def test_fake_sandbox_returns_results_in_order() -> None:
    first = SandboxResult(
        status=SandboxStatus.SUCCEEDED,
        return_code=0,
        stdout="hello",
    )
    second = SandboxResult(status=SandboxStatus.TIMED_OUT)
    sandbox = FakeSandbox(results=(first, second))

    assert sandbox.execute(make_request()) == first
    assert sandbox.execute(make_request()) == second


def test_fake_sandbox_fails_when_results_are_exhausted() -> None:
    sandbox = FakeSandbox(results=())

    with pytest.raises(RuntimeError, match="no more results"):
        sandbox.execute(make_request())
