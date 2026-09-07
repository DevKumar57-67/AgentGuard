from fastapi import FastAPI
from .models import ToolCall
from .guard import inspect_tool_call


app = FastAPI(
    title="AgentGuard",
    description="Security gateway for AI agent tool calls.",
    version="0.1.0"
)


@app.get("/")
def root():

    return {
        "name": "AgentGuard",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


@app.post("/guard")
def guard(tool_call: ToolCall):

    return inspect_tool_call(tool_call)