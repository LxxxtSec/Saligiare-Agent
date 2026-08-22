from pathlib import Path

import pytest

from saligiare.sandbox.base import SandboxRequest
from saligiare.sandbox.docker import DockerSandbox
from saligiare.sandbox.policy import SandboxPolicy


def make_request(**overrides: object) -> SandboxRequest:
    values: dict[str, object] = {
        "argv": ("printf", "hello"),
        "cwd": "/workspace",
        "timeout_seconds": 30,
        "network_enabled": False,
    }
    values.update(overrides)
    return SandboxRequest(**values)


def make_sandbox() -> DockerSandbox:
    return DockerSandbox(
        image="saligiare-test:latest",
        workspace=Path("/tmp/saligiare-workspace"),
    )


def test_docker_command_has_isolation_defaults() -> None:
    command = make_sandbox().build_command(make_request())

    assert command[:4] == (
        "docker",
        "run",
        "--rm",
        "--network",
    )
    assert "none" in command
    assert "--read-only" in command
    assert "--cap-drop" in command
    assert "ALL" in command
    assert "no-new-privileges" in command
    assert "--pids-limit" in command
    assert "--memory" in command
    assert "--cpus" in command
    assert "printf" in command
    assert "hello" in command


def test_docker_command_uses_argument_vector() -> None:
    command = make_sandbox().build_command(
        make_request(argv=("sh", "-c", "printf hello")),
    )

    assert command[-4:] == (
        "saligiare-test:latest",
        "sh",
        "-c",
        "printf hello",
    )


def test_docker_command_rejects_network_by_default() -> None:
    with pytest.raises(PermissionError, match="network"):
        make_sandbox().build_command(
            make_request(network_enabled=True),
        )


def test_docker_command_can_use_explicit_network_policy() -> None:
    sandbox = DockerSandbox(
        image="saligiare-test:latest",
        workspace=Path("/tmp/saligiare-workspace"),
        policy=SandboxPolicy(network_allowed=True),
    )

    command = sandbox.build_command(
        make_request(network_enabled=True),
    )

    assert "bridge" in command


def test_docker_sandbox_rejects_blank_image() -> None:
    with pytest.raises(ValueError, match="image"):
        DockerSandbox(
            image=" ",
            workspace=Path("/tmp/saligiare-workspace"),
        )
