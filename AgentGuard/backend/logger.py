import json
from datetime import datetime, timezone
from pathlib import Path


LOG_FILE = Path("logs/audit.json")


def log_event(event: dict):

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    event["timestamp"] = datetime.now(timezone.utc).isoformat()

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event) + "\n")