"""
app.py — CodePatrol server entry point required by OpenEnv and Docker runtime.
"""

from __future__ import annotations

import uvicorn
from server.main import app


def main() -> None:
    """Launch the CodePatrol FastAPI service with Uvicorn."""
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()