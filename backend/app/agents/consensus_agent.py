from __future__ import annotations

from typing import Dict, List

from app.agents.base import BaseAgent
from app.models.schemas import AgentResult


class ConsensusAgent(BaseAgent):
    """Synthesizes every other agent's contribution into one final answer.

    Unlike the other agents, its confidence/recommendation are not generated
    independently — they are computed by the orchestrator from the full set
    of prior ``AgentResult``s (see ``services/council.py::build_consensus``)
    and passed in here so the agent's card stays consistent with the
    detailed ``ConsensusSummary`` panel shown alongside it.
    """

    role = "Consensus Agent"

    def synthesize(
        self,
        problem: str,
        context: List[Dict],
        overall_confidence: float,
        final_recommendation: str,
    ) -> AgentResult:
        output = self._reason(problem, context)
        return AgentResult(
            role=self.role,
            analysis=output.analysis,
            confidence=overall_confidence,
            objections=[],
            recommendation=final_recommendation,
        )
