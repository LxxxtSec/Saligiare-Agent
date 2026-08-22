from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from saligiare.tools.base import ToolResult, ToolResultStatus, ToolSpec


class EchoArguments(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    text: str = Field(min_length=1, max_length=4_000)


class EchoTool:
    spec = ToolSpec(
        name="echo",
        capability="echo",
        description="返回调用者提供的文本，不访问外部资源",
    )

    def execute(self, arguments: dict[str, Any]) -> ToolResult:
        parsed = EchoArguments.model_validate(arguments)

        return ToolResult(
            status=ToolResultStatus.SUCCEEDED,
            summary="echo completed",
            data={"text": parsed.text},
        )