"""Per-agent system prompts for the LLM reasoning engine.

Derived from ``agents/roles.py``, the single source of truth for each
role's persona, description, and decision objective. Kept as its own
module (rather than inlining ``AGENT_ROLES`` access in
services/llm_reasoning.py) so that file's import stays a plain
``Dict[str, str]`` lookup, unchanged from before roles.py existed.
"""

from __future__ import annotations

from typing import Dict

from app.agents.roles import AGENT_ROLES

ROLE_PERSONAS: Dict[str, str] = {
    role: definition.system_prompt for role, definition in AGENT_ROLES.items()
}
