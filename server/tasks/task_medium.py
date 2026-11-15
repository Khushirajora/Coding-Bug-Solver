"""
task_medium.py — CodePatrol Metadata and Specification for the Medium Task.

Multi-Queue Triage: Evaluates the agent's ability to classify
severity tiers and route a queue of 5 bug reports to the appropriate
engineering teams.
"""

from __future__ import annotations

TASK_ID = "medium"
TASK_NAME = "CodePatrol: Multi-Team Bug Queue Triage"
DIFFICULTY = "medium"
MAX_STEPS = 15
SUCCESS_THRESHOLD = 0.5

DESCRIPTION = (
    "Process an active triage queue of 5 incoming bug reports through CodePatrol. "
    "For each bug, determine its severity tier (critical/high/medium/low) AND route "
    "it to the correct engineering squad (frontend/backend/infra/security). "
    "You have a budget of 15 steps for the 5 queue items."
)

SEVERITY_BADGES = {
    "critical": "🔴 CRITICAL",
    "high": "🟠 HIGH",
    "medium": "🟡 MEDIUM",
    "low": "🟢 LOW",
}

ACTION_SCHEMA = {
    "action": "triage",
    "severity": "critical | high | medium | low",
    "team": "frontend | backend | infra | security",
    "comment": "<optional notes, not scored in medium mode>",
}

SCORING = {
    "severity_weight": 0.50,
    "team_weight": 0.50,
    "severity_exact": 1.0,
    "severity_adjacent": 0.5,
    "severity_wrong": 0.0,
    "team_exact": 1.0,
    "team_wrong": 0.0,
    "skip_penalty": -0.2,
    "invalid_penalty": -0.3,
}

TIPS = [
    "frontend squad: UI controls, rendering, charts, and browser/client compatibility.",
    "backend squad: Core APIs, ORM/database bottlenecks, and business logic exceptions.",
    "infra squad: Kubernetes events, pod memory/OOM kills, deployments, and cluster health.",
    "security squad: Authentication, credential rotation, rate limiting, and exploit attempts.",
    "Severity and squad routing are distinct: UI/frontend bugs can still be high or critical.",
]


def describe() -> dict:
    """Return task metadata dictionary for the CodePatrol /tasks endpoint."""
    return {
        "task_id": TASK_ID,
        "name": TASK_NAME,
        "difficulty": DIFFICULTY,
        "max_steps": MAX_STEPS,
        "success_threshold": SUCCESS_THRESHOLD,
        "description": DESCRIPTION,
        "severity_badges": SEVERITY_BADGES,
        "action_schema": ACTION_SCHEMA,
        "scoring": SCORING,
        "tips": TIPS,
    }