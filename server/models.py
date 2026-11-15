"""
models.py — Core Pydantic schemas and data contracts for CodePatrol.

Covers:
  - Severity tiers & visual security badges
  - BugReport / PullRequest data models
  - BugObservation & BugAction OpenEnv contracts
  - RewardBreakdown, StepResult, & EnvState telemetry
  - SecurityScorecard differentiator model
"""

from __future__ import annotations

from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums & CodePatrol Tiers
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CodePatrolBadge(str, Enum):
    CRITICAL = "🔴 CRITICAL"
    HIGH = "🟠 HIGH"
    MEDIUM = "🟡 MEDIUM"
    LOW = "🟢 LOW"


class Team(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    INFRA = "infra"
    SECURITY = "security"


class PRVerdict(str, Enum):
    APPROVE = "approve"
    REQUEST_CHANGES = "request_changes"
    COMMENT = "comment"


class ItemType(str, Enum):
    BUG_REPORT = "bug_report"
    PULL_REQUEST = "pull_request"


class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# ---------------------------------------------------------------------------
# Key Differentiator: Security Scorecard Model
# ---------------------------------------------------------------------------

class SecurityScorecard(BaseModel):
    """Automated security assessment scorecard with visual indicators."""
    severity_score: float = Field(ge=0.0, le=10.0, description="CVSS-style score (0.0 to 10.0)")
    badge: str = Field(description="Visual severity badge with emoji")
    tier: str = Field(description="CodePatrol Risk Tier")
    blast_radius: str = Field(description="Scope of potential system or data impact")
    recommended_action: str = Field(default="", description="Immediate operational remediation")


# ---------------------------------------------------------------------------
# Data models — stored in data/bug_reports.json
# ---------------------------------------------------------------------------

class GroundTruthBug(BaseModel):
    """Expected triage ground truth (hidden from the agent during evaluation)."""
    severity: Severity
    team: Team
    keywords: list[str] = Field(default_factory=list)


class GroundTruthPR(BaseModel):
    """Expected code review ground truth (hidden from the agent during evaluation)."""
    verdict: PRVerdict
    has_security_issue: bool = False
    security_issue_type: str | None = None
    review_keywords: list[str] = Field(default_factory=list)
    quality_score: float = Field(ge=0.0, le=1.0, default=0.5)


class BugReport(BaseModel):
    """A single defect or vulnerability report in the CodePatrol queue."""
    id: str
    title: str
    body: str
    labels: list[str] = Field(default_factory=list)
    reporter: str
    created_at: str
    ground_truth: GroundTruthBug

    def to_agent_view(self) -> dict[str, Any]:
        """Returns only public item metadata, stripping ground truth."""
        return {
            "id": self.id,
            "type": ItemType.BUG_REPORT,
            "title": self.title,
            "body": self.body,
            "labels": self.labels,
            "reporter": self.reporter,
            "created_at": self.created_at,
        }


class PullRequest(BaseModel):
    """A pull request submitted for code and security review."""
    id: str
    title: str
    body: str
    labels: list[str] = Field(default_factory=list)
    author: str
    base_branch: str
    files_changed: int
    additions: int
    deletions: int
    ground_truth: GroundTruthPR

    def to_agent_view(self) -> dict[str, Any]:
        """Returns only public item metadata, stripping ground truth."""
        return {
            "id": self.id,
            "type": ItemType.PULL_REQUEST,
            "title": self.title,
            "body": self.body,
            "labels": self.labels,
            "author": self.author,
            "base_branch": self.base_branch,
            "files_changed": self.files_changed,
            "additions": self.additions,
            "deletions": self.deletions,
        }


# ---------------------------------------------------------------------------
# Observation — what the agent receives each step
# ---------------------------------------------------------------------------

class BugObservation(BaseModel):
    """Full observation returned by reset() and step()."""
    task_id: str
    episode_id: str
    item_index: int = Field(ge=0)
    total_items: int = Field(ge=1)
    item_type: ItemType
    item_id: str
    title: str
    body: str
    labels: list[str] = Field(default_factory=list)
    reporter: str = ""
    available_actions: list[str] = Field(default_factory=list)
    step_number: int = Field(ge=1)
    max_steps: int = Field(ge=1)
    current_score: float = Field(ge=0.0, le=1.0, default=0.0)
    feedback: str = ""
    echoed_message: str = ""


# ---------------------------------------------------------------------------
# Action — what the agent sends
# ---------------------------------------------------------------------------

class BugAction(BaseModel):
    """Action payload submitted by the agent."""
    message: str = Field(
        description="JSON string containing the action name and parameters."
    )


# ---------------------------------------------------------------------------
# Reward — telemetry returned with each step
# ---------------------------------------------------------------------------

class RewardBreakdown(BaseModel):
    """Itemized scoring metrics for an individual step."""
    severity_score: float = Field(
        ge=0.0, le=1.0, default=0.0, description="Severity accuracy (0.0 wrong / 0.5 adjacent / 1.0 exact)"
    )
    team_score: float = Field(
        ge=0.0, le=1.0, default=0.0, description="Engineering squad assignment accuracy"
    )
    comment_score: float = Field(
        ge=0.0, le=1.0, default=0.0, description="Comment relevance and keyword coverage"
    )
    security_score: float = Field(
        ge=0.0, le=1.0, default=0.0, description="Vulnerability detection precision"
    )
    efficiency_bonus: float = Field(
        ge=0.0, le=0.2, default=0.0, description="Bonus for resolving in fewer steps"
    )
    skip_penalty: float = Field(
        ge=-1.0, le=0.0, default=0.0, description="Penalty for skipping queue items"
    )
    invalid_penalty: float = Field(
        ge=-1.0, le=0.0, default=0.0, description="Penalty for malformed JSON or unpermitted actions"
    )
    repeat_penalty: float = Field(
        ge=-1.0, le=0.0, default=0.0, description="Penalty for redundant duplicate actions"
    )


class BugReward(BaseModel):
    """Reward telemetry wrapper."""
    value: float = Field(description="Net step reward")
    breakdown: RewardBreakdown = Field(description="Itemized component scores")
    partial_credit: float = Field(ge=0.0, le=1.0, description="Cumulative progress [0.0, 1.0]")


# ---------------------------------------------------------------------------
# StepResult — return envelope for POST /step and POST /reset
# ---------------------------------------------------------------------------

class StepResult(BaseModel):
    """Standard OpenEnv step result container."""
    observation: BugObservation
    reward: float = Field(default=0.0)
    done: bool = Field(default=False)
    info: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# EnvState — full state returned by GET /state
# ---------------------------------------------------------------------------

class EnvState(BaseModel):
    """Complete internal environment state for diagnostics and evaluation tracking."""
    task_id: str
    episode_id: str
    step_count: int = Field(ge=0)
    max_steps: int = Field(ge=1)
    item_index: int = Field(ge=0)
    total_items: int = Field(ge=1)
    is_done: bool = False
    cumulative_reward: float = 0.0
    normalised_score: float = Field(ge=0.0, le=1.0, default=0.0)
    actions_taken: list[dict[str, Any]] = Field(default_factory=list)
    rewards_history: list[float] = Field(default_factory=list)
    last_feedback: str = ""
    last_action_valid: bool = True


# ---------------------------------------------------------------------------
# ResetRequest — body accepted by POST /reset
# ---------------------------------------------------------------------------

class ResetRequest(BaseModel):
    """Request body for initializing an episode."""
    task_id: str | None = Field(
        default=None,
        description="Task to initialize: 'easy', 'medium', or 'hard'. Defaults to 'easy'.",
    )