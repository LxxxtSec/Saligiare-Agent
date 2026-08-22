from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from saligiare.sandbox.base import SandboxRequest


class SandboxDecisionStatus(str, Enum):
    ALLOWED = "allowed"
    DENIED = "denied"


class SandboxDecision(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    status: SandboxDecisionStatus
    reason: str = Field(min_length=1)

    @property
    def allowed(self) -> bool:
        return self.status is SandboxDecisionStatus.ALLOWED


class SandboxPolicy(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    allowed_cwd_prefixes: tuple[str, ...] = ("/workspace",)
    max_timeout_seconds: int = Field(default=300, gt=0, le=3_600)
    network_allowed: bool = False
    max_env_entries: int = Field(default=32, ge=0, le=256)

    def check(self, request: SandboxRequest) -> SandboxDecision:
        if request.network_enabled and not self.network_allowed:
            return SandboxDecision(
                status=SandboxDecisionStatus.DENIED,
                reason="network access is disabled by sandbox policy",
            )

        if request.timeout_seconds > self.max_timeout_seconds:
            return SandboxDecision(
                status=SandboxDecisionStatus.DENIED,
                reason="request timeout exceeds sandbox policy",
            )

        if not self._cwd_allowed(request.cwd):
            return SandboxDecision(
                status=SandboxDecisionStatus.DENIED,
                reason="working directory is outside sandbox policy",
            )

        if len(request.env) > self.max_env_entries:
            return SandboxDecision(
                status=SandboxDecisionStatus.DENIED,
                reason="environment entry count exceeds sandbox policy",
            )

        return SandboxDecision(
            status=SandboxDecisionStatus.ALLOWED,
            reason="sandbox request is allowed",
        )

    def _cwd_allowed(self, cwd: str) -> bool:
        return any(
            cwd == prefix or cwd.startswith(f"{prefix.rstrip('/')}/")
            for prefix in self.allowed_cwd_prefixes
        )
