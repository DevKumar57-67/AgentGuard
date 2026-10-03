from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class SecurityEvent:
    id: str
    timestamp: str
    agent_id: str
    tool: str
    risk: str
    decision: str
    reason: str
    prompt: str | None = None
    arguments: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        event: dict[str, Any] = {
            "id": self.id,
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "tool": self.tool,
            "risk": self.risk,
            "decision": self.decision,
            "reason": self.reason,
        }
        if self.prompt is not None:
            event["prompt"] = self.prompt
        if self.arguments is not None:
            event["arguments"] = self.arguments
        return event