"""Central place to resolve environment variables into typed settings.

Every other module reads configuration from here rather than calling
``os.getenv`` directly, so the set of environment variables the backend
actually depends on stays discoverable in one file.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# backend/app/config/settings.py -> repo root is three levels up.
REPO_ROOT = Path(__file__).resolve().parents[3]

# Loads backend/.env into the process environment, if present. Must run
# before the os.getenv() calls below. override=False so real env vars
# (e.g. set by a deployment platform) always win over the local .env file.
load_dotenv(REPO_ROOT / "backend" / ".env", override=False)

ALLOWED_ORIGINS: list[str] = os.getenv(
    "POLIS_ALLOWED_ORIGINS", "http://localhost:3000"
).split(",")

LOGS_DIR: Path = Path(os.getenv("POLIS_LOGS_DIR", str(REPO_ROOT / "logs")))

# --- LLM reasoning (optional) ---------------------------------------------
# Which provider to use, if any. Empty string (the default) means "no
# provider configured" -- the council runs on the deterministic mock
# reasoning engine. See docs/agents.md#reasoning-engine and
# backend/.env.example for configuration instructions.
LLM_PROVIDER: str = os.getenv("POLIS_LLM_PROVIDER", "").strip().lower()

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL: str = os.getenv("POLIS_ANTHROPIC_MODEL", "claude-sonnet-5")

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL: str = os.getenv("POLIS_OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = os.getenv("POLIS_GEMINI_MODEL", "gemini-2.0-flash")
