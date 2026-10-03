import tempfile
import unittest
from pathlib import Path

from backend.database.repository import EventRepository
from backend.models.event import SecurityEvent


def make_event(event_id: str = "event-1") -> SecurityEvent:
    return SecurityEvent(
        id=event_id,
        timestamp="2026-10-03T10:00:00",
        agent_id="test-agent",
        tool="send_email",
        risk="AMBER",
        decision="APPROVAL_REQUIRED",
        reason="Approval needed.",
        prompt="Send a test message.",
        arguments={"to": "test@example.com"},
    )


class EventRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "events.sqlite3"
        self.repository = EventRepository(self.database_path)
        self.repository.initialize()

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_events_persist_and_round_trip_optional_fields(self) -> None:
        event = make_event()
        self.repository.create(event)

        restarted_repository = EventRepository(self.database_path)
        self.assertEqual(restarted_repository.get(event.id), event)
        self.assertEqual(restarted_repository.list_events(), [event])

    def test_decision_updates_existing_event(self) -> None:
        self.repository.create(make_event())

        approved = self.repository.decide("event-1", "APPROVE")

        self.assertIsNotNone(approved)
        assert approved is not None
        self.assertEqual(approved.decision, "APPROVED_BY_ADMIN")
        self.assertEqual(
            approved.reason,
            "Manually approved by Security Administrator on Dashboard.",
        )

    def test_missing_event_returns_none(self) -> None:
        self.assertIsNone(self.repository.decide("missing", "DENY"))


if __name__ == "__main__":
    unittest.main()