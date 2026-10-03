from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/")
def read_root(request: Request) -> dict[str, str]:
    settings = request.app.state.settings
    return {"name": "AgentGuard", "status": "running", "version": settings.version}