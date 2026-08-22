from pydantic import BaseModel, ConfigDict, Field


class ToolSpec(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    name: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    description: str = Field(min_length=1)