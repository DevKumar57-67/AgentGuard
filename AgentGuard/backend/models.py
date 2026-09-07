from typing import Any, Dict
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    tool: str = Field(..., min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)
    agent_id: str = "demo-agent"


class GuardDecision(BaseModel):
    tool: str
    risk: str
    decision: str
    reason: str