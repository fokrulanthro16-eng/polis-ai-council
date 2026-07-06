"""Real, LLM-backed reasoning engine.

Implements the same contract as services/mock_reasoning.py --
``reason(role, problem, context) -> RawAgentOutput`` -- so it is a
drop-in replacement selected by agents/base.py when an LLM provider is
configured (see config/settings.py and services/llm_providers/).

Every agent role has its own system prompt (agents/prompts.py). The
model is instructed to respond with a single JSON object matching
RawAgentOutput's fields. If the configured provider is unavailable, the
call fails, or the response can't be parsed, this module falls back to
the deterministic mock reasoning engine for that single turn -- a
flaky provider or a malformed response never fails an entire council
deliberation (see docs/deployment.md and paper/future-work.md).
"""

from __future__ import annotations

import json
import logging
import re
from typing import Dict, List

from app.agents.prompts import ROLE_PERSONAS
from app.services import mock_reasoning
from app.services.llm_providers.factory import get_provider
from app.services.mock_reasoning import RawAgentOutput

_logger = logging.getLogger("polis.llm_reasoning")

_OUTPUT_CONTRACT = (
    "Respond with ONLY a single JSON object -- no markdown code fences, no "
    "commentary before or after it -- with exactly these fields:\n"
    '{"analysis": "<2-4 sentences of your reasoning>", '
    '"confidence": <number between 0.0 and 1.0>, '
    '"objections": ["<0 or more concerns or caveats>"], '
    '"recommendation": "<one concrete, actionable sentence>"}'
)

_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)


def _system_prompt(role: str) -> str:
    persona = ROLE_PERSONAS.get(role)
    if persona is None:
        raise ValueError(f"No system prompt registered for role '{role}'")
    return f"{persona}\n\n{_OUTPUT_CONTRACT}"


def _user_prompt(problem: str, context: List[Dict]) -> str:
    lines = [f"Problem under deliberation:\n{problem}"]
    if context:
        lines.append("\nOther council members have already spoken, in order:")
        for entry in context:
            objection_note = (
                f" Objections: {'; '.join(entry['objections'])}"
                if entry["objections"]
                else ""
            )
            lines.append(
                f"- {entry['role']} (confidence {entry['confidence']:.2f}): "
                f"{entry['recommendation']}{objection_note}"
            )
        lines.append(
            "\nWhen relevant, explicitly reference the specific council member you are "
            'building on or pushing back against by name (e.g. "Building on the Research '
            'Agent\'s findings..." or "The Critic raises an important point..."), so the '
            "debate reads as a real discussion rather than isolated statements."
        )
    lines.append(
        "\nProvide your analysis now, as the agent described in your system prompt."
    )
    return "\n".join(lines)


def _parse_output(role: str, raw_text: str) -> RawAgentOutput:
    match = _JSON_OBJECT.search(raw_text)
    if not match:
        raise ValueError(f"No JSON object found in LLM response: {raw_text!r}")
    data = json.loads(match.group(0))

    analysis = str(data.get("analysis", "")).strip()
    recommendation = str(data.get("recommendation", "")).strip()
    # The Consensus Agent's recommendation is discarded by the caller
    # (council.py computes it numerically), so only analysis is required there.
    if not analysis or (not recommendation and role != "Consensus Agent"):
        raise ValueError(
            f"LLM response for '{role}' is missing required fields: {data!r}"
        )

    confidence = max(0.0, min(1.0, float(data.get("confidence", 0.5))))

    objections = data.get("objections", [])
    if not isinstance(objections, list):
        objections = []

    return RawAgentOutput(
        analysis=analysis,
        confidence=confidence,
        objections=[str(o) for o in objections],
        recommendation=recommendation,
    )


def reason(role: str, problem: str, context: List[Dict]) -> RawAgentOutput:
    """Produce an LLM-backed reasoning output for one council agent turn."""
    provider = get_provider()
    if provider is None:
        return mock_reasoning.reason(role, problem, context)

    try:
        raw_text = provider.complete(
            system_prompt=_system_prompt(role),
            user_prompt=_user_prompt(problem, context),
        )
        return _parse_output(role, raw_text)
    except Exception:
        _logger.warning(
            "LLM reasoning failed for role '%s'; falling back to mock reasoning "
            "for this turn.",
            role,
            exc_info=True,
        )
        return mock_reasoning.reason(role, problem, context)
