"""Base class shared by every council agent."""

from __future__ import annotations

from typing import Dict, List

from app.models.schemas import AgentResult
from app.services import llm_reasoning, mock_reasoning
from app.services.llm_providers.factory import get_provider


class BaseAgent:
    """A council member. Subclasses just set ``role``.

    ``analyze`` delegates to whichever reasoning engine is active: the
    real LLM engine (``services/llm_reasoning.py``) if a provider is
    configured via POLIS_LLM_PROVIDER, otherwise the deterministic mock
    engine (``services/mock_reasoning.py``). Both implement the same
    ``reason(role, problem, context) -> RawAgentOutput`` contract, so this
    class stays a thin adapter regardless of which one is active.
    """

    role: str = "Base Agent"

    def _reason(self, problem: str, context: List[Dict]):
        """Dispatch to whichever reasoning engine is active for this call.

        Shared by ``analyze`` below and ``ConsensusAgent.synthesize`` so
        every agent -- including Consensus -- reasons through a real LLM
        provider when one is configured, instead of one agent silently
        being stuck on the mock engine.
        """
        reason = (
            llm_reasoning.reason
            if get_provider() is not None
            else mock_reasoning.reason
        )
        return reason(self.role, problem, context)

    def analyze(self, problem: str, context: List[Dict]) -> AgentResult:
        output = self._reason(problem, context)
        return AgentResult(
            role=self.role,
            analysis=output.analysis,
            confidence=output.confidence,
            objections=output.objections,
            recommendation=output.recommendation,
        )
