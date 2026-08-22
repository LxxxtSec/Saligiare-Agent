import pytest
from pydantic import ValidationError

from saligiare.tools.base import ToolSpec
from saligiare.tools.registry import ToolRegistry


def make_tool(
    name: str = "artifact_read",
    capability: str = "artifact_read",
) -> ToolSpec:
    return ToolSpec(
        name=name,
        capability=capability,
        description="读取任务附件",
    )


def test_registry_registers_and_finds_tool() -> None:
    registry = ToolRegistry()
    tool = make_tool()

    registry.register(tool)

    assert registry.get("artifact_read") == tool
    assert registry.names == ("artifact_read",)


def test_registry_rejects_duplicate_tool_names() -> None:
    registry = ToolRegistry()
    registry.register(make_tool())

    with pytest.raises(ValueError, match="already registered"):
        registry.register(make_tool())


def test_registry_rejects_unknown_tool() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="unknown tool"):
        registry.get("not_registered")


def test_tool_spec_rejects_blank_fields() -> None:
    with pytest.raises(ValidationError):
        make_tool(name="")

    with pytest.raises(ValidationError):
        make_tool(capability=" ")


def test_tool_spec_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ToolSpec(
            name="artifact_read",
            capability="artifact_read",
            description="读取任务附件",
            run_as_root=True,
        )