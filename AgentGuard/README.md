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
1. **Interceptor Middleware (`backend/main.py`):** Asynchronous FastAPI REST API intercepting JSON tool-call payloads.
2. **Policy Engine & Regex Scanner (`backend/policy_engine.py`):** Rule evaluation engine enforcing risk tiers:
   - 🟢 **GREEN (ALLOW):** Low-risk read actions (e.g., `search_web`).
   - 🟡 **AMBER (APPROVAL_REQUIRED):** Sensitive state-changing actions (e.g., `send_email`).
   - 🔴 **RED (BLOCK):** Destructive system calls (e.g., `execute_shell`, `drop_database_table`) or detected prompt injections.
3. **Interactive & SecOps Dashboard (`frontend/src/`):** A responsive React + TypeScript interface providing a live audit dashboard, agent activity, an interactive policy playground, and a Human-in-the-Loop approval queue.
4. **Agent Simulator (`simulator/agent.py`):** CLI utility for simulating tool execution requests[cite: 1].

---

## 📁 Repository Structure

```text
AgentGuard/
├── backend/
│   ├── __init__.py
│   ├── guard.py
│   ├── logger.py
│   ├── main.py                # FastAPI Interceptor Gateway
│   ├── models.py              # Pydantic Schemas
│   └── policy_engine.py       # Policy Rules & Injection Heuristics
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
