from saligiare.benchmarks.tsecbench.official import (
    TsecbenchChallenge,
    TsecbenchStartResult,
)
from saligiare.core.task import ApprovalLevel, Task, TaskMode


class TsecbenchTaskFactory:
    """把官方题目启动结果转换为通用 Task，不执行任何远程操作。"""

    def __init__(
        self,
        allowed_capabilities: tuple[str, ...] = ("tsecbench_target",),
        max_steps: int = 100,
        timeout_seconds: int = 3_600,
    ) -> None:
        if not allowed_capabilities:
            raise ValueError("allowed_capabilities must not be empty")
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        if timeout_seconds < 1:
            raise ValueError("timeout_seconds must be positive")

        self._allowed_capabilities = allowed_capabilities
        self._max_steps = max_steps
        self._timeout_seconds = timeout_seconds

    def build(
        self,
        challenge: TsecbenchChallenge,
        started: TsecbenchStartResult,
    ) -> Task:
        if challenge.unique_code != started.unique_code:
            raise ValueError("challenge and start result do not match")
        if not started.container_addr:
            raise ValueError("started challenge has no container addresses")

        return Task(
            task_id=f"tsecbench:{challenge.unique_code}",
            mode=TaskMode.CTF_SOLVE,
            target=challenge.unique_code,
            scope=started.container_addr,
            allowed_capabilities=self._allowed_capabilities,
            required_approval=ApprovalLevel.DEDICATED_VM,
            max_steps=self._max_steps,
            timeout_seconds=self._timeout_seconds,
            evaluator_id="tsecbench-official-v1",
            metadata={
                "benchmark": "tsecbench",
                "challenge_code": challenge.unique_code,
                "difficulty": challenge.difficulty,
                "level": challenge.level,
                "flag_count": str(challenge.flag_count),
            },
        )
