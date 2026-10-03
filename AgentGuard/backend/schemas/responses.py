from typing import Any

from pydantic import BaseModel


class EventResponse(BaseModel):
    id: str
    timestamp: str
    agent_id: str
    tool: str
    risk: str
    decision: str
    reason: str
    prompt: str | None = None
    arguments: dict[str, Any] | None = None


class GuardDecision(BaseModel):
    agent_id: str
    tool: str
    arguments: dict[str, Any]
    risk: str
    decision: str
    reason: str


class ActionDecisionResponse(BaseModel):
    status: str
    event: EventResponse