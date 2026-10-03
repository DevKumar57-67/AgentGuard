from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_event_repository
from backend.database.repository import EventRepository
from backend.schemas.requests import ActionDecisionRequest
from backend.schemas.responses import ActionDecisionResponse, EventResponse
from backend.services.event_service import decide_event, list_events

router = APIRouter()


@router.get("/events", response_model=list[EventResponse], response_model_exclude_none=True)
def get_events(
    repository: EventRepository = Depends(get_event_repository),
) -> list[EventResponse]:
    return [EventResponse.model_validate(event.to_dict()) for event in list_events(repository)]


@router.post("/action", response_model=ActionDecisionResponse, response_model_exclude_none=True)
def update_action(
    request: ActionDecisionRequest,
    repository: EventRepository = Depends(get_event_repository),
) -> ActionDecisionResponse:
    event = decide_event(repository, request.event_id, request.action)
    if event is None:
        raise HTTPException(status_code=404, detail="Event ID not found")
    return ActionDecisionResponse(
        status="success",
        event=EventResponse.model_validate(event.to_dict()),
    )