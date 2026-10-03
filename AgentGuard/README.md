# AgentGuard

AgentGuard is a runtime security gateway for AI agent tool calls. It evaluates requests before execution, blocks destructive or injection-like requests, routes sensitive actions for human approval, and records decisions in SQLite. The dashboard is a React + TypeScript app backed by a FastAPI API.

## Features

- Deterministic risk tiers: `GREEN` allows, `AMBER` requires approval, and `RED` blocks.
- Independent prompt-injection detection for destructive commands and instruction overrides.
- Human-in-the-loop approve/deny decisions.
- SQLite-backed event history that persists across backend restarts.
- Interactive playground, agent activity, policy outcomes, and audit views.
- Agent simulator using the `/guard` interception endpoint.

## Architecture

```text
AgentGuard/
├── backend/
│   ├── api/                 # FastAPI route handlers and dependencies
│   ├── auth/                # Reserved; authentication is not enabled
│   ├── config/              # Environment-backed application settings
│   ├── core/                # Risk engine and prompt-injection detector
│   ├── database/            # SQLite connections and event repository
│   ├── models/              # Domain records
│   ├── schemas/             # Pydantic request and response models
│   ├── services/            # Policy, interception, and event use cases
│   ├── guard.py             # Legacy inspection entry point
│   ├── main.py              # FastAPI app factory and startup
│   └── policy_engine.py     # Legacy policy import compatibility
├── frontend/
│   └── src/                 # React + TypeScript dashboard
├── logs/                    # Legacy JSONL audit output
├── runtime/                 # Default SQLite database location
├── simulator/               # CLI tool-call simulator
└── tests/                   # Standard-library unittest suite
```

The Render Blueprint is at the Git repository root, one directory above this project folder: `../render.yaml`.

## Requirements

- Python 3.10 or newer
- Node.js 20 or newer and npm

## Local Development

From the cloned repository root, enter the project directory:

```bash
cd AgentGuard
```

Create and activate a Python virtual environment, then install the backend requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate with `source .venv/bin/activate` instead.

Start the backend from the `AgentGuard` project directory:

```bash
python -m uvicorn backend.main:app --reload
```

In another terminal, start the dashboard:

```bash
cd AgentGuard/frontend
npm ci
npm run dev
```

The dashboard is available at `http://localhost:5173`; the API is at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs`.

To exercise the simulator, run `python simulator/agent.py` from the `AgentGuard` project directory while the backend is running.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Gateway health and version |
| `POST` | `/evaluate` | Evaluate a tool and prompt; returns a recorded event |
| `POST` | `/guard` | Evaluate a tool call with arguments; returns the simulator decision |
| `GET` | `/events` | List recorded events, newest first |
| `POST` | `/action` | Approve or deny a recorded event |

Example evaluation request:

```json
{
  "agent_id": "demo-agent",
  "tool": "send_email",
  "prompt": "Send the project update to the client"
}
```

Example approval request:

```json
{
  "event_id": "<event-id>",
  "action": "APPROVE"
}
```

`action` accepts `APPROVE` or `DENY`. Decisions are recorded as `APPROVED_BY_ADMIN` or `DENIED_BY_ADMIN` in the event history.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `AGENTGUARD_DATABASE_PATH` | `runtime/agentguard.db` | SQLite database file |
| `AGENTGUARD_CORS_ORIGINS` | `*` | Comma-separated allowed browser origins |
| `AGENTGUARD_APP_TITLE` | `AgentGuard Security Gateway` | FastAPI app title |
| `AGENTGUARD_VERSION` | `0.1.0` | Version returned by `GET /` |
| `VITE_API_URL` | `http://127.0.0.1:8000` | Backend URL embedded in the frontend build |

Use an absolute path for `AGENTGUARD_DATABASE_PATH` in deployment environments. Authentication is not currently implemented; do not expose the API as a protected production service without adding an authentication layer.

## Tests and Frontend Checks

Run the backend tests from the project directory:

```bash
python -m unittest discover -s tests -v
```

Run frontend checks from `AgentGuard/frontend`:

```bash
npm run lint
npm run typecheck
npm run build
```

## Deploy to Render

The [Render Blueprint](../render.yaml) deploys the backend as a Python web service and the dashboard as a static site. In Render, create a new Blueprint from the repository and select `render.yaml`.

The Blueprint configures the backend root as `AgentGuard/` and the frontend root as `AgentGuard/frontend/`. It builds the UI with the API service URL, sets the API CORS origin to the generated dashboard URL, and rewrites static-site routes to `index.html` for the React app.

SQLite is stored on a 1 GB persistent disk mounted at `/var/data`. Persistent disks require a paid Render web-service plan, configured here as `0.5c-512mb`; the static dashboard can use Render's free static hosting. If you use a custom dashboard domain, update `AGENTGUARD_CORS_ORIGINS` on the API service to that exact HTTPS origin.