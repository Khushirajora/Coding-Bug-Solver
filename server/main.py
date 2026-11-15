"""
main.py — FastAPI server exposing the CodePatrol environment as an OpenEnv-compliant API.

Endpoints:
  POST /reset          initialize or restart an episode
  POST /step           send one action, get observation + reward
  GET  /state          inspect full internal environment state
  GET  /tasks          list all available tasks with descriptions
  GET  /tasks/{id}     get description for a specific task
  GET  /health         liveness probe (used by HF Spaces + validator)
  GET  /               API info, quick-start guide, and badge overview
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .env import CodePatrolEnv
from .models import BugAction, EnvState, ResetRequest, StepResult
from .tasks import task_easy, task_hard, task_medium

# ---------------------------------------------------------------------------
# Environment singleton
# ---------------------------------------------------------------------------

env = CodePatrolEnv()


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run a silent reset on startup so /state never returns 'not initialised'."""
    env.reset(task_id="easy")
    yield


app = FastAPI(
    title="CodePatrol Triage & Review Environment",
    description=(
        "An automated security triage and code review environment for evaluating AI agents. "
        "Agents categorize bugs, audit pull requests for security flaws, and order fix backlogs. "
        "Implements the full OpenEnv interface."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _env_error(exc: Exception, context: str) -> JSONResponse:
    """Return a structured 500 response rather than crashing unhandled."""
    return JSONResponse(
        status_code=500,
        content={"error": context, "detail": str(exc)},
    )


# ---------------------------------------------------------------------------
# OpenEnv core endpoints
# ---------------------------------------------------------------------------

@app.post(
    "/reset",
    response_model=StepResult,
    summary="Reset the environment and start a new episode",
    tags=["OpenEnv"],
)
async def reset(body: ResetRequest = ResetRequest()) -> StepResult:
    """
    Initialise a fresh episode.

    - Send `{}` or omit body to default to the **easy** task.
    - Send `{"task_id": "medium"}` or `{"task_id": "hard"}` to select a task.
    """
    try:
        return env.reset(task_id=body.task_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post(
    "/step",
    response_model=StepResult,
    summary="Send one action and receive the next observation + reward",
    tags=["OpenEnv"],
)
async def step(action: BugAction) -> StepResult:
    """
    Advance the environment by one step.

    The `message` field must be a JSON string encoding the action.
    """
    try:
        return env.step(action)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get(
    "/state",
    response_model=EnvState,
    summary="Return the full internal environment state",
    tags=["OpenEnv"],
)
async def state() -> EnvState:
    """
    Returns the complete internal state of the environment.
    Intended for diagnostics, logging, and evaluation scoring.
    """
    try:
        return env.get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Discovery endpoints
# ---------------------------------------------------------------------------

@app.get(
    "/tasks",
    summary="List all available tasks with descriptions and scoring info",
    tags=["Discovery"],
)
async def list_tasks() -> dict[str, Any]:
    """Return metadata for all three tasks: easy, medium, and hard."""
    return {
        "tasks": [
            task_easy.describe(),
            task_medium.describe(),
            task_hard.describe(),
        ]
    }


@app.get(
    "/tasks/{task_id}",
    summary="Get description and schema for a specific task",
    tags=["Discovery"],
)
async def get_task(task_id: str) -> dict[str, Any]:
    """Return metadata for a single task by ID (easy / medium / hard)."""
    mapping = {
        "easy": task_easy.describe,
        "medium": task_medium.describe,
        "hard": task_hard.describe,
    }
    if task_id not in mapping:
        raise HTTPException(
            status_code=404,
            detail=f"Task '{task_id}' not found. Valid tasks: easy, medium, hard",
        )
    return mapping[task_id]()


# ---------------------------------------------------------------------------
# Health + info
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    summary="Liveness probe",
    tags=["System"],
)
async def health() -> dict[str, str]:
    """Returns status ok for container and cloud health probes."""
    return {"status": "ok"}


@app.get(
    "/",
    summary="API overview and quick-start",
    tags=["System"],
)
async def root() -> dict[str, Any]:
    """Quick-start guide, task overview, and severity badges."""
    return {
        "name": "CodePatrol Triage & Review Platform",
        "version": "1.0.0",
        "description": (
            "Automated incident triage and security auditing environment. "
            "Evaluates AI agents on defect severity classification, team routing, "
            "code review vulnerability checks, and backlog prioritization."
        ),
        "severity_badges": {
            "critical": "🔴 CRITICAL",
            "high": "🟠 HIGH",
            "medium": "🟡 MEDIUM",
            "low": "🟢 LOW",
        },
        "quickstart": [
            "1. POST /reset                    — start easy task",
            "2. POST /reset {'task_id': 'medium'} — start medium task",
            "3. POST /step  {'message': '<json>'} — submit triage action",
            "4. GET  /state                    — inspect current episode state",
            "5. GET  /tasks                    — inspect schemas and guidelines",
        ],
        "endpoints": {
            "POST /reset": "Start a new episode",
            "POST /step": "Send action, get observation + reward",
            "GET  /state": "Full internal state",
            "GET  /tasks": "All task descriptions",
            "GET  /tasks/{id}": "Single task description",
            "GET  /health": "Liveness probe",
        },
        "docs": "/docs",
    }