from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class ToolCall(BaseModel):
    """
    Represents a tool request made by an AI agent.
    """

    model_config = ConfigDict(extra="forbid")

    tool: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)
    agent_id: str = Field(default="demo-agent", min_length=1)


class GuardDecision(BaseModel):
    """
    Result returned by AgentGuard after inspecting a tool call.
    """

    agent_id: str
    tool: str
    arguments: Dict[str, Any]
    risk: str
    decision: str
    reason: str