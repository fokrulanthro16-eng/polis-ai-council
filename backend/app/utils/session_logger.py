"""Writes one POLIS Protocol v1 session record per deliberation to logs/.

Logging is best-effort: a failure to write a session log must never turn
a successful deliberation into a failed API response (see
docs/deployment.md#logging).
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from app.config import settings
from app.models.schemas import DeliberateResponse
from app.utils.protocol import to_protocol_message

_logger = logging.getLogger("polis.session_logger")


def write_session_log(problem: str, response: DeliberateResponse) -> None:
    """Persist a session record for one deliberation under settings.LOGS_DIR.

    Reuses ``response.timestamp``/``response.protocol_version`` (stamped
    once by services/council.py) rather than generating a second timestamp
    here, so the API response, the exported session JSON, and the on-disk
    log all agree on exactly when the deliberation happened.
    """
    timestamp = response.timestamp
    session_id = uuid.uuid4().hex[:8]

    record = {
        "session_id": session_id,
        "protocol_version": response.protocol_version,
        "timestamp": timestamp,
        "problem": problem,
        "agents": [to_protocol_message(agent, timestamp) for agent in response.agents],
        "timeline": [entry.model_dump() for entry in response.timeline],
        "consensus": response.consensus.model_dump(),
        "metrics": response.metrics.model_dump(),
    }

    file_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = settings.LOGS_DIR / f"session_{file_stamp}_{session_id}.json"

    try:
        settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    except OSError:
        _logger.warning("Failed to write session log to %s", path, exc_info=True)
