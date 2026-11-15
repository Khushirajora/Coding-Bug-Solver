"""
task_hard.py — CodePatrol Metadata and Specification for the Hard Task.

End-to-End Security Triage & Code Review Pipeline: Evaluates the agent's
ability to triage 8 bugs, audit 3 pull requests for vulnerabilities,
and output an optimal incident-response fix queue.
"""

from __future__ import annotations

TASK_ID = "hard"
TASK_NAME = "CodePatrol: End-to-End Security Triage & Code Review Pipeline"
DIFFICULTY = "hard"
MAX_STEPS = 25
SUCCESS_THRESHOLD = 0.4

DESCRIPTION = (
    "Process a combined queue of 8 bug reports and 3 pull requests through CodePatrol. "
    "For bugs: assign severity tier, route to engineering teams, provide technical commentary, "
    "and flag security vulnerabilities. "
    "For pull requests: issue review verdicts (approve/request_changes/comment), audit for security "
    "flaws (such as injection vulnerabilities or credential mishandling), and provide actionable comments. "
    "Finally, submit a sorted priority fix queue ordering all items by risk."
)

SEVERITY_BADGES = {
    "critical": "🔴 CRITICAL",
    "high": "🟠 HIGH",
    "medium": "🟡 MEDIUM",
    "low": "🟢 LOW",
}

BUG_ACTION_SCHEMA = {
    "action": "triage",
    "severity": "critical | high | medium | low",
    "team": "frontend | backend | infra | security",
    "comment": "<technical assessment — include root causes and key security terms>",
    "security_issue": "true | false",
}

PR_ACTION_SCHEMA = {
    "action": "review_pr",
    "verdict": "approve | request_changes | comment",
    "comment": "<code review feedback — highlight syntax, logic, or security hazards>",
    "security_issue": "true | false",
}

PRIORITIZE_ACTION_SCHEMA = {
    "action": "prioritize",
    "order": ["BUG-XXX", "PR-XXX", "..."],
}

SCORING = {
    "bug": {
        "severity_weight": 0.30,
        "team_weight": 0.25,
        "comment_weight": 0.25,
        "security_weight": 0.20,
    },
    "pr": {
        "verdict_weight": 0.40,
        "security_weight": 0.40,
        "comment_weight": 0.20,
    },
    "prioritization": {
        "rank_accuracy_weight": 0.70,
        "coverage_weight": 0.30,
    },
    "penalties": {
        "skip": -0.2,
        "invalid": -0.3,
        "repeat": -0.1,
        "false_negative_security": 0.0,
        "false_positive_security": 0.3,
    },
}

TIPS = [
    "Carefully inspect pull request diffs for injection vectors (e.g., raw SQL with f-strings) and secret leaks.",
    "SQL injection or credential exposure must trigger request_changes with security_issue=true.",
    "Priority queue ordering: 🔴 Critical security bugs > 🔴 Critical crashes > 🟠 High-severity production outages > "
    "🟠 High-severity infra bottlenecks > 🔴 Compromised PRs > 🟡 Medium issues > 🟢 Low/cosmetic defects.",
    "Missing a genuine vulnerability (false negative) carries a severe penalty.",
    "Budget roughly 2 steps per item across the 25 allowed steps.",
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
        "bug_action_schema": BUG_ACTION_SCHEMA,
        "pr_action_schema": PR_ACTION_SCHEMA,
        "prioritize_schema": PRIORITIZE_ACTION_SCHEMA,
        "scoring": SCORING,
        "tips": TIPS,
    }