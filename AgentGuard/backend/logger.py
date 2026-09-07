import json
from datetime import datetime, timezone
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "audit.json"


def log_event(event: dict):

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    event["timestamp"] = datetime.now(timezone.utc).isoformat()

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")


def read_events() -> list[dict]:
    if not LOG_FILE.exists():
        return []

    events = []
    with LOG_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                events.append(event)

    return events