from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvaluationRequest(BaseModel):
    agent_id: str = "demo-agent"
    tool: str
    prompt: str = ""


class ActionDecisionRequest(BaseModel):
    event_id: str
    action: str


class ToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool: str = Field(..., min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)
    agent_id: str = Field(default="demo-agent", min_length=1)