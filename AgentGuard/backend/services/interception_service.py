import json
import uuid
from datetime import datetime

from backend.database.repository import EventRepository
from backend.models.event import SecurityEvent
from backend.schemas.requests import EvaluationRequest, ToolCall
from backend.schemas.responses import GuardDecision
from backend.services.policy_service import evaluate_policy


def evaluate_interception(
    repository: EventRepository,
    request: EvaluationRequest,
) -> SecurityEvent:
    return _record_interception(
        repository,
        agent_id=request.agent_id,
        tool=request.tool,
        prompt=request.prompt,
    )


def inspect_tool_call(repository: EventRepository, tool_call: ToolCall) -> GuardDecision:
    prompt = json.dumps(tool_call.arguments, ensure_ascii=False, default=str)
    event = _record_interception(
        repository,
        agent_id=tool_call.agent_id,
        tool=tool_call.tool,
        prompt=prompt,
        arguments=tool_call.arguments,
    )
    return GuardDecision(
        agent_id=event.agent_id,
        tool=event.tool,
        arguments=tool_call.arguments,
        risk=event.risk,
        decision=event.decision,
        reason=event.reason,
    )


def _record_interception(
    repository: EventRepository,
    *,
    agent_id: str,
    tool: str,
    prompt: str,
    arguments: dict | None = None,
) -> SecurityEvent:
    evaluation = evaluate_policy(tool, prompt)
    event = SecurityEvent(
        id=str(uuid.uuid4())[:8],
        timestamp=datetime.now().isoformat(),
        agent_id=agent_id,
        tool=tool,
        prompt=prompt,
        arguments=arguments,
        risk=evaluation["risk"],
        decision=evaluation["decision"],
        reason=evaluation["reason"],
    )
    return repository.create(event)