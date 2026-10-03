import os
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.config.settings import PROJECT_ROOT, Settings


class SettingsTests(unittest.TestCase):
    def test_environment_overrides_database_and_cors(self) -> None:
        with patch.dict(
            os.environ,
            {
                "AGENTGUARD_DATABASE_PATH": "data/test.sqlite3",
                "AGENTGUARD_CORS_ORIGINS": "https://console.example, http://localhost:5173",
                "AGENTGUARD_APP_TITLE": "Test Gateway",
                "AGENTGUARD_VERSION": "2.0.0",
            },
        ):
            settings = Settings.from_env()

        self.assertEqual(settings.database_path, PROJECT_ROOT / "data" / "test.sqlite3")
        self.assertEqual(
            settings.cors_origins,
            ("https://console.example", "http://localhost:5173"),
        )
        self.assertEqual(settings.app_title, "Test Gateway")
        self.assertEqual(settings.version, "2.0.0")

    def test_absolute_database_path_is_preserved(self) -> None:
        database_path = Path(os.environ.get("TEMP", "/tmp")) / "agentguard-test.sqlite3"
        with patch.dict(os.environ, {"AGENTGUARD_DATABASE_PATH": str(database_path)}):
            settings = Settings.from_env()
        self.assertEqual(settings.database_path, database_path)


if __name__ == "__main__":
    unittest.main()