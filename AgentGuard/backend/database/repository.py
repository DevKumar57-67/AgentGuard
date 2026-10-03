import json
from pathlib import Path
from typing import Any

from backend.database.connection import connect
from backend.models.event import SecurityEvent


class EventRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS security_events (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    tool TEXT NOT NULL,
                    prompt TEXT,
                    arguments_json TEXT,
                    risk TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reason TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_security_events_timestamp "
                "ON security_events(timestamp DESC)"
            )

    def create(self, event: SecurityEvent) -> SecurityEvent:
        with connect(self.database_path) as connection:
            connection.execute(
                """
                INSERT INTO security_events
                    (id, timestamp, agent_id, tool, prompt, arguments_json, risk, decision, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.id,
                    event.timestamp,
                    event.agent_id,
                    event.tool,
                    event.prompt,
                    json.dumps(event.arguments) if event.arguments is not None else None,
                    event.risk,
                    event.decision,
                    event.reason,
                ),
            )
        return event

    def list_events(self) -> list[SecurityEvent]:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                "SELECT * FROM security_events ORDER BY timestamp DESC, rowid DESC"
            ).fetchall()
        return [self._from_row(row) for row in rows]

    def get(self, event_id: str) -> SecurityEvent | None:
        with connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT * FROM security_events WHERE id = ?", (event_id,)
            ).fetchone()
        return self._from_row(row) if row is not None else None

    def decide(self, event_id: str, action: str) -> SecurityEvent | None:
        with connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT * FROM security_events WHERE id = ?", (event_id,)
            ).fetchone()
            if row is None:
                return None

            decisions = {
                "APPROVE": (
                    "APPROVED_BY_ADMIN",
                    "Manually approved by Security Administrator on Dashboard.",
                ),
                "DENY": (
                    "DENIED_BY_ADMIN",
                    "Manually rejected by Security Administrator on Dashboard.",
                ),
            }
            update = decisions.get(action)
            if update is not None:
                connection.execute(
                    "UPDATE security_events SET decision = ?, reason = ? WHERE id = ?",
                    (*update, event_id),
                )
                row = connection.execute(
                    "SELECT * FROM security_events WHERE id = ?", (event_id,)
                ).fetchone()
        return self._from_row(row)

    @staticmethod
    def _from_row(row: Any) -> SecurityEvent:
        arguments_json = row["arguments_json"]
        return SecurityEvent(
            id=row["id"],
            timestamp=row["timestamp"],
            agent_id=row["agent_id"],
            tool=row["tool"],
            risk=row["risk"],
            decision=row["decision"],
            reason=row["reason"],
            prompt=row["prompt"],
            arguments=json.loads(arguments_json) if arguments_json is not None else None,
        )