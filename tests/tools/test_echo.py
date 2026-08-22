import pytest
from pydantic import ValidationError

from saligiare.tools.base import ToolResultStatus
from saligiare.tools.echo import EchoTool


def test_echo_tool_exposes_spec() -> None:
    tool = EchoTool()

    assert tool.spec.name == "echo"
    assert tool.spec.capability == "echo"


def test_echo_tool_returns_text() -> None:
    tool = EchoTool()

    result = tool.execute({"text": "hello"})

    assert result.status is ToolResultStatus.SUCCEEDED
    assert result.data == {"text": "hello"}


def test_echo_tool_strips_outer_whitespace() -> None:
    result = EchoTool().execute({"text": "  hello  "})

    assert result.data == {"text": "hello"}


def test_echo_tool_rejects_blank_text() -> None:
    with pytest.raises(ValidationError):
        EchoTool().execute({"text": " "})


def test_echo_tool_rejects_unknown_arguments() -> None:
    with pytest.raises(ValidationError):
        EchoTool().execute(
            {
                "text": "hello",
                "run_as_root": True,
            },
        )


def test_echo_tool_rejects_oversized_text() -> None:
    with pytest.raises(ValidationError):
        EchoTool().execute({"text": "x" * 4_001})