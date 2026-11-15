"""
task_easy.py — CodePatrol Metadata and Specification for the Easy Task.

Single bug classification: Evaluates the agent's ability to ingest
a single defect report and assign the accurate severity tier.
"""

from __future__ import annotations

TASK_ID = "easy"
TASK_NAME = "CodePatrol: Single Bug Severity Triage"
DIFFICULTY = "easy"
MAX_STEPS = 3
SUCCESS_THRESHOLD = 0.6

DESCRIPTION = (
    "Analyze and triage the severity tier of a single incoming issue. "
    "Select from the standard severity tiers: critical, high, medium, low. "
    "Full credit is awarded for exact matches, with partial credit for adjacent tiers."
)

ACTION_SCHEMA = {
    "action": "classify",
    "severity": "critical | high | medium | low",
}

SEVERITY_BADGES = {
    "critical": "🔴 CRITICAL",
    "high": "🟠 HIGH",
    "medium": "🟡 MEDIUM",
    "low": "🟢 LOW",
}

SCORING = {
    "severity_exact": 1.0,
    "severity_adjacent": 0.5,
    "severity_wrong": 0.0,
    "skip_penalty": -0.2,
    "invalid_penalty": -0.3,
}

TIPS = [
    "Check for crash traces, data corruption, or auth failures — these indicate critical severity (🔴).",
    "Performance bottlenecks and significant service degradation map to high severity (🟠).",
    "Isolated UI bugs and boundary edge-cases typically indicate medium severity (🟡).",
    "Typographical errors and minor styling defects indicate low severity (🟢).",
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
        "action_schema": ACTION_SCHEMA,
        "severity_badges": SEVERITY_BADGES,
        "scoring": SCORING,
        "tips": TIPS,
    }