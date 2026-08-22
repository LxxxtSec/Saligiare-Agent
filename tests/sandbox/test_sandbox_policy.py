import pytest
from pydantic import ValidationError

from saligiare.sandbox.base import SandboxRequest
from saligiare.sandbox.policy import (
    SandboxDecisionStatus,
    SandboxPolicy,
)


def make_request(**overrides: object) -> SandboxRequest:
    values: dict[str, object] = {
        "argv": ("printf", "hello"),
        "cwd": "/workspace/project",
        "timeout_seconds": 30,
        "env": {},
        "network_enabled": False,
    }
    values.update(overrides)
    return SandboxRequest(**values)


def test_policy_allows_safe_request() -> None:
    decision = SandboxPolicy().check(make_request())

    assert decision.status is SandboxDecisionStatus.ALLOWED
    assert decision.allowed is True


def test_policy_denies_network_by_default() -> None:
    decision = SandboxPolicy().check(
        make_request(network_enabled=True),
    )

    assert decision.status is SandboxDecisionStatus.DENIED
    assert "network" in decision.reason


def test_policy_denies_cwd_outside_workspace() -> None:
    decision = SandboxPolicy().check(
        make_request(cwd="/tmp/outside"),
    )

    assert decision.status is SandboxDecisionStatus.DENIED
    assert "working directory" in decision.reason


def test_policy_denies_excessive_timeout() -> None:
    decision = SandboxPolicy().check(
        make_request(timeout_seconds=301),
    )

    assert decision.status is SandboxDecisionStatus.DENIED
    assert "timeout" in decision.reason


def test_policy_rejects_invalid_configuration() -> None:
    with pytest.raises(ValidationError):
        SandboxPolicy(max_timeout_seconds=0)

    with pytest.raises(ValidationError):
        SandboxPolicy(max_env_entries=-1)
