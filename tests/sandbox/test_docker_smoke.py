import os
from pathlib import Path

import pytest

from saligiare.sandbox.base import SandboxRequest, SandboxStatus
from saligiare.sandbox.docker import DockerSandbox


@pytest.mark.skipif(
    os.environ.get("SALIGIARE_DOCKER_SMOKE") != "1",
    reason="Docker smoke test requires explicit SALIGIARE_DOCKER_SMOKE=1",
)
def test_docker_sandbox_runs_busybox_printf(tmp_path: Path) -> None:
    image = os.environ.get("SALIGIARE_SANDBOX_IMAGE", "saligiare-sandbox:test")
    sandbox = DockerSandbox(image=image, workspace=tmp_path)

    result = sandbox.execute(
        SandboxRequest(
            argv=("/bin/busybox", "printf", "hello"),
            cwd="/workspace",
            timeout_seconds=10,
        ),
    )

    assert result.status is SandboxStatus.SUCCEEDED
    assert result.return_code == 0
    assert result.stdout == "hello"
