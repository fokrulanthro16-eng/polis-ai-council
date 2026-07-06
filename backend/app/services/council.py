"""The Orchestrator: runs the council of agents in order and assembles the
debate timeline plus final consensus.

Sequence: Research -> Planner -> Critic -> Risk -> Ethics -> Consensus.
Each agent sees the AgentResults of everyone who spoke before it, so later
agents (especially Critic) can reference earlier ones.
"""

from __future__ import annotations

from typing import Dict, List

from app.agents.consensus_agent import ConsensusAgent
from app.agents.critic_agent import CriticAgent
from app.agents.ethics_agent import EthicsAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.research_agent import ResearchAgent
from app.agents.risk_agent import RiskAgent
from app.models.schemas import (
    AgentResult,
    ConsensusExplanation,
    ConsensusSummary,
    CouncilMetrics,
    DebateTimelineEntry,
    DeliberateResponse,
)
from app.utils.protocol import PROTOCOL_VERSION, utc_timestamp

# Order matters: each agent is given the AgentResults of everyone before it.
_PIPELINE = [
    ResearchAgent(),
    PlannerAgent(),
    CriticAgent(),
    RiskAgent(),
    EthicsAgent(),
]

_CONSENSUS_AGENT = ConsensusAgent()

# Confidence gap below the group average that counts an agent as dissenting.
_DISSENT_MARGIN = 0.15


def _timeline_message(result: AgentResult) -> str:
    """Condense an AgentResult into one line for the debate timeline."""
    message = result.recommendation
    if result.objections:
        message += f" (raises {len(result.objections)} objection{'s' if len(result.objections) != 1 else ''})"
    return message


def _agreement_signals(results: List[AgentResult]) -> Dict[str, object]:
    """Shared math behind both the consensus tier and the metrics panel.

    Confidence alone doesn't capture how "together" a council is: five
    agents all mildly agreeing and three strongly agreeing with two
    dissenting can land on the same mean confidence but represent very
    different levels of actual agreement. This blends the group's
    confidence with how many agents dissent and how many objections were
    raised overall.
    """
    avg_confidence = sum(r.confidence for r in results) / len(results)
    total_objections = sum(len(r.objections) for r in results)
    objection_penalty = min(0.25, 0.03 * total_objections)
    overall_confidence = round(max(0.05, min(0.99, avg_confidence - objection_penalty)), 2)

    dissenting_roles = [r.role for r in results if r.confidence < avg_confidence - _DISSENT_MARGIN]
    supporting_roles = [r.role for r in results if r.role not in dissenting_roles]
    support_ratio = len(supporting_roles) / len(results)

    objection_density = total_objections / len(results)
    objection_factor = max(0.0, 1 - min(1.0, objection_density / 2.5))

    agreement_score = round(0.5 * overall_confidence + 0.3 * support_ratio + 0.2 * objection_factor, 2)

    return {
        "avg_confidence": avg_confidence,
        "overall_confidence": overall_confidence,
        "total_objections": total_objections,
        "dissenting_roles": dissenting_roles,
        "supporting_roles": supporting_roles,
        "agreement_score": agreement_score,
    }


def _agreement_level(agreement_score: float) -> str:
    if agreement_score >= 0.78:
        return "Strong Consensus"
    if agreement_score >= 0.6:
        return "Moderate Consensus"
    if agreement_score >= 0.4:
        return "Weak Consensus"
    return "Highly Contested"


def build_consensus(problem: str, results: List[AgentResult]) -> ConsensusSummary:
    """Aggregate every agent's AgentResult into a single consensus."""
    if not results:
        raise ValueError("Cannot build consensus from an empty result set")

    signals = _agreement_signals(results)
    overall_confidence = signals["overall_confidence"]
    dissenting_roles = signals["dissenting_roles"]
    supporting_roles = signals["supporting_roles"]
    agreement_level = _agreement_level(signals["agreement_score"])

    key_risks = [obj for r in results if r.role == "Risk Agent" for obj in r.objections]
    key_objections = [obj for r in results for obj in r.objections]

    # The most confident agent's recommendation anchors the final answer;
    # objections from the rest are folded in as caveats.
    lead = max(results, key=lambda r: r.confidence)
    final_recommendation = lead.recommendation
    if key_objections:
        final_recommendation += " Caveat: " + " ".join(key_objections[:2])

    supporting_arguments = [
        r.recommendation
        for r in sorted(results, key=lambda r: r.confidence, reverse=True)
        if r.role in supporting_roles and r.recommendation
    ][:3]

    reasoning = (
        f"{len(supporting_roles)} of {len(results)} agents supported the lead recommendation "
        f"(avg confidence {round(signals['avg_confidence'] * 100)}%), with "
        f"{len(dissenting_roles)} dissenting voice{'s' if len(dissenting_roles) != 1 else ''} and "
        f"{signals['total_objections']} objection{'s' if signals['total_objections'] != 1 else ''} "
        f'raised overall — producing a "{agreement_level}" outcome.'
    )

    explanation = ConsensusExplanation(
        supporting_arguments=supporting_arguments,
        main_objections=key_objections[:3],
        reasoning=reasoning,
    )

    return ConsensusSummary(
        final_recommendation=final_recommendation,
        overall_confidence=overall_confidence,
        agreement_level=agreement_level,
        key_risks=key_risks,
        key_objections=key_objections,
        dissenting_roles=dissenting_roles,
        explanation=explanation,
    )


def build_metrics(results: List[AgentResult]) -> CouncilMetrics:
    """Heuristic council-level indicators for the compact Metrics panel.

    risk_level reads the Risk Agent's own confidence/objections as a proxy
    for perceived downside; evidence_quality reads the Research Agent's the
    same way as a proxy for how grounded the council's information is.
    Neither is a measured quantity -- see docs/protocol.md#evidence-today.
    """
    signals = _agreement_signals(results)

    risk_agent = next((r for r in results if r.role == "Risk Agent"), None)
    risk_signal = (
        min(1.0, (1 - risk_agent.confidence) + 0.1 * len(risk_agent.objections))
        if risk_agent
        else 0.5
    )
    if risk_signal >= 0.6:
        risk_level = "High"
    elif risk_signal >= 0.35:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    research_agent = next((r for r in results if r.role == "Research Agent"), None)
    evidence_signal = (
        max(0.0, min(1.0, research_agent.confidence - 0.15 * len(research_agent.objections)))
        if research_agent
        else 0.5
    )
    if evidence_signal >= 0.7:
        evidence_quality = "High"
    elif evidence_signal >= 0.45:
        evidence_quality = "Medium"
    else:
        evidence_quality = "Low"

    return CouncilMetrics(
        council_confidence=round(signals["avg_confidence"], 2),
        agreement_score=signals["agreement_score"],
        risk_level=risk_level,
        evidence_quality=evidence_quality,
    )


def run_council(problem: str) -> DeliberateResponse:
    """Run the full multi-agent deliberation for a given problem statement."""
    results: List[AgentResult] = []
    context: List[Dict] = []
    timeline: List[DebateTimelineEntry] = []

    for step, agent in enumerate(_PIPELINE, start=1):
        result = agent.analyze(problem, context)
        results.append(result)
        context.append(result.model_dump())
        timeline.append(
            DebateTimelineEntry(
                step=step,
                role=result.role,
                message=_timeline_message(result),
                responding_to=timeline[-1].role if timeline else None,
            )
        )

    consensus = build_consensus(problem, results)
    metrics = build_metrics(results)

    consensus_result = _CONSENSUS_AGENT.synthesize(
        problem=problem,
        context=context,
        overall_confidence=consensus.overall_confidence,
        final_recommendation=consensus.final_recommendation,
    )
    results.append(consensus_result)
    timeline.append(
        DebateTimelineEntry(
            step=len(timeline) + 1,
            role=consensus_result.role,
            message=consensus.final_recommendation,
            responding_to=timeline[-1].role if timeline else None,
        )
    )

    return DeliberateResponse(
        problem=problem,
        agents=results,
        timeline=timeline,
        consensus=consensus,
        metrics=metrics,
        timestamp=utc_timestamp(),
        protocol_version=PROTOCOL_VERSION,
    )
