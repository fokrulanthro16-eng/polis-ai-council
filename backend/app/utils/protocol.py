"""Adapter from the live AgentResult schema to a POLIS Protocol v1 message.

See protocol/POLIS_PROTOCOL_V1.md for the full field-by-field spec. This
is used for session logging (utils/session_logger.py) and does not
change the DeliberateResponse returned to the frontend.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from app.agents.roles import AGENT_ROLES
from app.models.schemas import AgentResult

PROTOCOL_VERSION = "1.0"


def utc_timestamp() -> str:
    """Canonical POLIS Protocol v1 timestamp: UTC, second precision, Z-suffixed.

    Shared by services/council.py (stamps DeliberateResponse) and
    utils/session_logger.py (reuses response.timestamp rather than
    generating its own), so one deliberation has exactly one timestamp.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# Fixed, one-sentence decision objective per role -- the protocol's "goal"
# field. Sourced from agents/roles.py, the single place role mandates live.
_ROLE_GOALS: Dict[str, str] = {
    role: definition.objective for role, definition in AGENT_ROLES.items()
}


def to_protocol_message(result: AgentResult, timestamp: str) -> Dict[str, Any]:
    """Convert an AgentResult into a POLIS Protocol v1 message dict.

    ``evidence`` is always empty today: the mock reasoning engine has no
    mechanism for sourcing real citations, and an empty list is preferable
    to a fabricated one (see POLIS_PROTOCOL_V1.md#evidence-today).
    """
    return {
        "agent": result.role,
        "goal": _ROLE_GOALS.get(result.role, ""),
        "analysis": result.analysis,
        "evidence": [],
        "confidence": result.confidence,
        "objections": list(result.objections),
        "recommendation": result.recommendation,
        "timestamp": timestamp,
    }
