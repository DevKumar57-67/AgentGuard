from fastapi import Request

from backend.database.repository import EventRepository


def get_event_repository(request: Request) -> EventRepository:
    return request.app.state.event_repository