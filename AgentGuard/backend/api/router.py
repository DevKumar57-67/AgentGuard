from fastapi import APIRouter

from backend.api.events import router as events_router
from backend.api.health import router as health_router
from backend.api.interceptions import router as interceptions_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(events_router)
api_router.include_router(interceptions_router)