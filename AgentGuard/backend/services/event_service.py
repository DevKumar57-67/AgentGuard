from backend.database.repository import EventRepository
from backend.models.event import SecurityEvent


def list_events(repository: EventRepository) -> list[SecurityEvent]:
    return repository.list_events()


def decide_event(
    repository: EventRepository,
    event_id: str,
    action: str,
) -> SecurityEvent | None:
    return repository.decide(event_id, action)