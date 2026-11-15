"""
grader_easy.py — CodePatrol Grader for Task: easy

Task goal   : Classify the severity of a single bug report.
Agent action: {"action": "classify", "severity": "critical|high|medium|low"}
Scoring     : severity accuracy only (1.0 = exact, 0.5 = adjacent, 0.0 = wrong)
Max reward  : 1.0 per item
"""

from __future__ import annotations

from ..models import BugReport, RewardBreakdown

_SEVERITY_ORDER = ["critical", "high", "medium", "low"]

_SEVERITY_BADGES = {
    "critical": "🔴 CRITICAL",
    "high": "🟠 HIGH",
    "medium": "🟡 MEDIUM",
    "low": "🟢 LOW",
}


def _score_severity(agent: str, truth: str) -> float:
    if agent not in _SEVERITY_ORDER or truth not in _SEVERITY_ORDER:
        return 0.0
    dist = abs(_SEVERITY_ORDER.index(agent) - _SEVERITY_ORDER.index(truth))
    if dist == 0:
        return 1.0
    if dist == 1:
        return 0.5
    return 0.0


def grade(action: dict, bug: BugReport) -> tuple[float, RewardBreakdown, str]:
    agent_severity = str(action.get("severity", "")).strip().lower()
    true_severity  = bug.ground_truth.severity.value

    sev_score = _score_severity(agent_severity, true_severity)
    reward    = sev_score
    breakdown = RewardBreakdown(severity_score=sev_score)

    badge = _SEVERITY_BADGES.get(true_severity, "⚪ UNKNOWN")

    if sev_score == 1.0:
        feedback = (
            f"✓ Correct! [{badge}] '{bug.id}' severity is '{true_severity}'. Full marks."
        )
    elif sev_score == 0.5:
        agent_badge = _SEVERITY_BADGES.get(agent_severity, "⚪")
        feedback = (
            f"~ Close. You said {agent_badge} '{agent_severity}' but correct is  {badge} '{true_severity}'. "
            f"Adjacent severity — partial credit (0.5)."
        )
    else:
        if agent_severity not in _SEVERITY_ORDER:
            feedback = (
                f"✗ Unrecognised severity '{agent_severity}'. "
                f"Must be one of: critical, high, medium, low. "
                f"Correct answer was {badge} '{true_severity}'."
            )
        else: 
            agent_badge = _SEVERITY_BADGES.get(agent_severity, "⚪")
            feedback = (
                f"✗ Wrong. You said {agent_badge} '{agent_severity}', "f" correct is {badge}  '{true_severity}'. No credit."
            )

    return reward, breakdown, feedback