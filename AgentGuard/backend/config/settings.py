import os
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class Settings:
    app_title: str = "AgentGuard Security Gateway"
    version: str = "0.1.0"
    database_path: Path = PROJECT_ROOT / "runtime" / "agentguard.db"
    cors_origins: tuple[str, ...] = ("*",)

    @classmethod
    def from_env(cls) -> "Settings":
        database_path = Path(
            os.getenv("AGENTGUARD_DATABASE_PATH", str(PROJECT_ROOT / "runtime" / "agentguard.db"))
        ).expanduser()
        if not database_path.is_absolute():
            database_path = PROJECT_ROOT / database_path

        cors_origins = tuple(
            origin.strip()
            for origin in os.getenv("AGENTGUARD_CORS_ORIGINS", "*").split(",")
            if origin.strip()
        )
        return cls(
            app_title=os.getenv("AGENTGUARD_APP_TITLE", "AgentGuard Security Gateway"),
            version=os.getenv("AGENTGUARD_VERSION", "0.1.0"),
            database_path=database_path,
            cors_origins=cors_origins or ("*",),
        )


def get_settings() -> Settings:
    return Settings.from_env()