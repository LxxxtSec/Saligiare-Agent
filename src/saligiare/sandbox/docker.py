import subprocess
from pathlib import Path

from saligiare.sandbox.base import (
    SandboxRequest,
    SandboxResult,
    SandboxStatus,
)
from saligiare.sandbox.policy import SandboxPolicy


class DockerSandbox:
    def __init__(
        self,
        image: str,
        workspace: Path,
        policy: SandboxPolicy | None = None,
        docker_binary: str = "docker",
    ) -> None:
        if not image.strip():
            raise ValueError("docker image must not be blank")

        self._image = image
        self._workspace = workspace
        self._policy = policy or SandboxPolicy()
        self._docker_binary = docker_binary

    def build_command(self, request: SandboxRequest) -> tuple[str, ...]:
        decision = self._policy.check(request)
        if not decision.allowed:
            raise PermissionError(decision.reason)

        network = "bridge" if request.network_enabled else "none"

        return (
            self._docker_binary,
            "run",
            "--rm",
            "--network",
            network,
            "--read-only",
            "--cap-drop",
            "ALL",
            "--security-opt",
            "no-new-privileges",
            "--pids-limit",
            "128",
            "--memory",
            "512m",
            "--cpus",
            "1.0",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=64m",
            "--mount",
            f"type=bind,src={self._workspace},dst=/workspace,rw",
            "--workdir",
            request.cwd,
            self._image,
            *request.argv,
        )

    def execute(self, request: SandboxRequest) -> SandboxResult:
        command = self.build_command(request)

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                check=False,
                text=True,
                timeout=request.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            stdout, _ = self._limit_output(exc.stdout)
            stderr, _ = self._limit_output(exc.stderr)
            return SandboxResult(
                status=SandboxStatus.TIMED_OUT,
                stdout=stdout,
                stderr=stderr,
                truncated=True,
            )

        stdout, stdout_truncated = self._limit_output(completed.stdout)
        stderr, stderr_truncated = self._limit_output(completed.stderr)

        return SandboxResult(
            status=(
                SandboxStatus.SUCCEEDED
                if completed.returncode == 0
                else SandboxStatus.FAILED
            ),
            return_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            truncated=stdout_truncated or stderr_truncated,
        )

    @staticmethod
    def _limit_output(value: str | bytes | None) -> tuple[str, bool]:
        if value is None:
            return "", False

        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")

        limit = 10_000
        return value[:limit], len(value) > limit
