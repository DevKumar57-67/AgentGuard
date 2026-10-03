# AgentGuard: Autonomous AI Agent Runtime Security & Action Gateway

**Problem Statement ID:** `[CC-GFG-01]`  
**Track:** Agentic AI & AI Security  
**Hackathon:** Career Catalyst Club x GeeksforGeeks 4-Hour Software Hackathon  

---

## 📌 Problem Summary

As autonomous AI agents are increasingly deployed across enterprise workflows, their tool-calling capabilities (e.g., executing shell commands, sending emails, or modifying databases) expose critical security vulnerabilities. Prompt injections or reasoning loops can lead to catastrophic unauthorized actions—such as dropping database tables or leaking credentials.

**AgentGuard** acts as an automated runtime security proxy and firewall middleware sitting between the AI Agent and host system tools. It intercepts tool calls before execution, evaluates them against policy rules and prompt injection heuristics, and categorizes them into clear risk tiers—incorporating real-time Human-in-the-Loop (HITL) authorization for sensitive operations.

---

## 🏗️ Solution Architecture Overview

AgentGuard uses a decoupled architecture to evaluate and guard AI agent execution in real time:

+------------------+         1. Tool-Call Payload        +-------------------------+
|  Autonomous AI   | ----------------------------------x | AgentGuard Interceptor  |
|      Agent       |                                     |    (FastAPI Backend)    |
+------------------+                                     +-------------------------+
|
2. Policy & Regex Engine
|
+--------------------------+--------------------------+
|                                                     |
🟢 GREEN (ALLOW)                                      🟡 AMBER / 🔴 RED
|                                                     |
Executes Tool & Logs                             Pauses / Blocks Execution
|
3. Real-Time Admin Alert
v
+------------------------+
|  SecOps Dashboard UI   |
|   (React + TypeScript) |
+------------------------+

### Key Components
1. **API (`backend/api/`):** FastAPI routes for evaluation, guard interception, audit events, approvals, and health status.
2. **Security Core (`backend/core/` and `backend/services/policy_service.py`):** Deterministic tool risk assessment, independent prompt injection detection, and policy orchestration:
   - 🟢 **GREEN (ALLOW):** Low-risk read actions (e.g., `search_web`).
   - 🟡 **AMBER (APPROVAL_REQUIRED):** Sensitive state-changing actions (e.g., `send_email`).
   - 🔴 **RED (BLOCK):** Destructive system calls (e.g., `execute_shell`, `drop_database_table`) or detected prompt injections.
3. **Persistence (`backend/database/`):** SQLite connection and repository layer for durable security events and approval decisions.
4. **Schemas and Services (`backend/schemas/`, `backend/models/`, `backend/services/`):** Pydantic API contracts, domain records, and application use cases separated from route handlers.
5. **Configuration (`backend/config/`):** Environment-driven application, CORS, and database settings. Authentication is not enabled.
6. **Dashboard (`frontend/src/`):** Responsive React + TypeScript interface for audit events, agent activity, policy outcomes, test interceptions, and human approvals.
7. **Agent Simulator (`simulator/agent.py`):** CLI utility for simulating tool execution requests[cite: 1].

---

## 📁 Repository Structure

```text
AgentGuard/
├── backend/
│   ├── api/                   # Route handlers and dependencies
│   ├── auth/                  # Reserved; authentication is not enabled
│   ├── config/                # Environment-backed settings
│   ├── core/                  # Risk engine and prompt detector
│   ├── database/              # SQLite connections and event repository
│   ├── models/                # Domain records
│   ├── schemas/               # Pydantic request/response models
│   ├── services/              # Policy, interception, and event use cases
│   ├── guard.py               # Legacy inspection entry point
│   ├── main.py                # FastAPI application factory
│   └── policy_engine.py       # Legacy policy import compatibility
├── frontend/
│   ├── src/                   # React + TypeScript dashboard
│   ├── package.json           # Frontend scripts and dependencies
│   └── vite.config.ts         # Vite development/build configuration
├── simulator/
│   └── agent.py               # Test Agent Tool-Call Generator
├── logs/                      # Event Audit Storage
├── requirements.txt           # Project Dependencies
├── .gitignore
└── README.md                  # Documentation


# Clone the repository
git clone [https://github.com/DevKumar57-67/AgentGuard.git](https://github.com/DevKumar57-67/AgentGuard.git)
cd AgentGuard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# On Linux/macOS:
source venv/bin/activate


#Required Installations
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

#Running the Project
#Terminal 1
python -m uvicorn backend.main:app --reload


#Terminal 2 (from the frontend directory)
cd frontend
npm install
npm run dev

#Terminal 3
python simulator/agent.py

# Backend tests
python -m unittest discover -s tests -v

# Optional backend environment variables:
# AGENTGUARD_DATABASE_PATH, AGENTGUARD_CORS_ORIGINS, AGENTGUARD_APP_TITLE, AGENTGUARD_VERSION


#Tech Stack
📚 Tech Stack & Libraries Utilized
Core Frameworks & Libraries
Python 3.10+ – Core programming language[cite: 1].

FastAPI – High-performance asynchronous API framework for JSON payload interception[cite: 1].

Uvicorn – ASGI web server implementation.

React + TypeScript – Responsive, typed SecOps dashboard client.

Vite – Frontend development server and production bundler.

Pydantic – Data validation and schema enforcement for incoming payloads[cite: 1].

Pandas – Structured tabular processing for security audit logging.

Requests – HTTP library for inter-service communication.

re (Regex) – Regular expression engine for prompt injection and threat pattern detection[cite: 1].

#Submission Requirements

#Github Url-https://github.com/DevKumar57-67/AgentGuard
