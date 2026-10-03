from fastapi import APIRouter, Depends

from backend.api.dependencies import get_event_repository
from backend.database.repository import EventRepository
from backend.schemas.requests import EvaluationRequest, ToolCall
from backend.schemas.responses import EventResponse, GuardDecision
from backend.services.interception_service import evaluate_interception, inspect_tool_call

router = APIRouter()


@router.post("/evaluate", response_model=EventResponse, response_model_exclude_none=True)
def evaluate_event(
    request: EvaluationRequest,
    repository: EventRepository = Depends(get_event_repository),
) -> EventResponse:
    event = evaluate_interception(repository, request)
    return EventResponse.model_validate(event.to_dict())


@router.post("/guard", response_model=GuardDecision)
def guard_tool_call(
    tool_call: ToolCall,
    repository: EventRepository = Depends(get_event_repository),
) -> GuardDecision:
    return inspect_tool_call(repository, tool_call)