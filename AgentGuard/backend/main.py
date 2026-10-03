from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.router import api_router
from backend.config.settings import Settings, get_settings
from backend.database.repository import EventRepository


def create_app(settings: Settings | None = None) -> FastAPI:
    app_settings = settings or get_settings()
    repository = EventRepository(app_settings.database_path)
    repository.initialize()

    application = FastAPI(title=app_settings.app_title)
    application.state.settings = app_settings
    application.state.event_repository = repository
    application.add_middleware(
        CORSMiddleware,
        allow_origins=list(app_settings.cors_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router)
    return application


app = create_app()