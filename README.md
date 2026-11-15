---
# CodePatrol 🛡️
### Autonomous SDLC Triage & Vulnerability Benchmark for AI Agents

Modern software teams spend hours every sprint reading bug tickets, deciding priorities, assigning issues, and reviewing code diffs. **CodePatrol** is a standalone evaluation framework built to measure how effectively LLMs and autonomous agents handle these exact real-world engineering responsibilities.

---

## Core Capabilities

CodePatrol tests four essential engineering skills:

* **Impact Severity Grading:** Distinguishing non-blocking UI glitches from system-critical outages.
* **Service & Team Routing:** Directing issues to frontend, backend, security, or platform infrastructure teams.
* **Security Flaw Interception:** Catching critical vulnerabilities (like SQL injection or authentication bypasses) during pull request reviews.
* **Resolution Scheduling:** Analyzing active tickets and scheduling an optimal, priority-ordered fix pipeline.

---

## Evaluation Tiers

* **Tier 1 — Single Incident Classification**  
  Tests basic understanding on an isolated ticket.  
  * **Objective:** Correctly label severity (`critical`, `high`, `medium`, `low`).  
  * **Action:** `{"action": "classify", "severity": "<level>"}`  
  * **Horizon:** Up to 3 steps.

* **Tier 2 — Batch Queue Routing**  
  Simulates a sprint queue with 5 mixed tickets.  
  * **Objective:** Resolve both ticket severity and the responsible team (`frontend`, `backend`, `infra`, `security`).  
  * **Action:** `{"action": "triage", "severity": "<level>", "team": "<team>"}`  
  * **Horizon:** Up to 15 steps.

* **Tier 3 — Full Pipeline Audit & PR Review**  
  A complex scenario covering 8 bug reports and 3 pull request diffs.  
  * **Objective:** Triage all issues, identify security flaws inside code diffs, leave constructive review feedback, and output an optimal execution order.  
  * **PR Review Action:** `{"action": "review_pr", "verdict": "request_changes", "comment": "...", "security_issue": true}`  
  * **Ordering Action:** `{"action": "prioritize", "order": ["BUG-005", "BUG-001", ...]}`  
  * **Horizon:** Up to 25 steps.

---

## Environment Interface

### Observation Frame
At each decision point, the agent receives a JSON state:

| Field | Type | Description |
| :--- | :--- | :--- |
| `task_id` | string | Current tier identifier |
| `item_id` | string | Active record ID (e.g., `BUG-003`, `PR-101`) |
| `item_type` | string | Record type (`bug_report` or `pull_request`) |
| `title` | string | Issue title or PR header |
| `body` | string | Stack trace context or git diff snippet |
| `labels` | list | Contextual metadata tags |
| `available_actions` | list | Actions valid for the current step |
| `step_number` | int | Active step index (1-based) |
| `max_steps` | int | Step budget before auto-termination |
| `current_score` | float | Running cumulative reward |
| `feedback` | string | Evaluator feedback from the previous action |

---

## Reward Architecture

CodePatrol uses step-level reward feedback so the model learns from every operational choice:

* **Severity Accuracy:** Full credit for exact matches; partial distance credit for adjacent ratings.
* **Service Routing:** Credit awarded for directing issues to the correct operational domain.
* **Security Catch:** Missing an active vulnerability in a pull request forfeits all reward points for that diff.
* **Operational Penalties:** Penalties are applied for malformed JSON schemas (`-0.30`), redundant duplicate actions (`-0.10`), or skipped items (`-0.20`).

---

## Service Endpoints

The core engine runs via a REST API:

| Method | Path | Purpose |
| :--- | :--- | :--- |
| `POST` | `/reset` | Initialize a session (payload: `{"task_id": "tier_1"}`) |
| `POST` | `/step` | Submit an action payload |
| `GET` | `/state` | Inspect current session context and episode status |
| `GET` | `/tasks` | Retrieve schemas and track parameters |
| `GET` | `/health` | Check service health |
| `GET` | `/docs` | Interactive Swagger API interface |

---

## Benchmark Results

Evaluation baseline using `gpt-4o-mini`:

| Benchmark Tier | Target Pass Rate | Recorded Score | Steps Taken |
| :--- | :---: | :---: | :---: |
| **Tier 1 (Classification)** | 75% | **100%** | 1 |
| **Tier 2 (Queue Triage)** | 55% | **82.0%** | 5 |
| **Tier 3 (Pipeline Audit)** | 30% | **80.1%** | 12 |
| **Composite Score** | — | **87.4%** | — |

---

## Getting Started

### Method 1: Docker (Recommended)

```bash
# Clone the repository
git clone [https://github.com/Khushirajora/CodePatrol.git](https://github.com/Khushirajora/CodePatrol.git)
cd CodePatrol

# Build and start the container
docker build -t codepatrol-engine .
docker run -p 7860:7860 codepatrol-engine
- **Inference time:** All 3 tasks complete in under 20 minutes
Method 2: Local Python Environment
# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate   # Mac/Linux: source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Launch API server
uvicorn server.main:app --host 0.0.0.0 --port 7860 --reload
Running an Agent Run
Create a .env file in the root folder:
API_BASE_URL=[https://api.openai.com/v1](https://api.openai.com/v1)
MODEL_NAME=gpt-4o-mini
API_KEY=your_key_here
ENV_URL=http://localhost:7860
Run the baseline agent runner:

Bash
python inference.py
Directory Overview
CodePatrol/
├── Dockerfile              # Container deployment file
├── requirements.txt        # Core dependencies
├── inference.py            # Agent harness & test runner
├── data/
│   └── bug_reports.json    # Standardized evaluation scenarios
└── server/
    ├── main.py             # FastAPI routing and application startup
    ├── env.py              # Environment state machine and transition rules
    ├── models.py           # Pydantic schema validation
    ├── tasks/              # Tier-based scenario definitions
    └── graders/            # Scoring modules and penalty calculations
License
This project is licensed under the MIT License.