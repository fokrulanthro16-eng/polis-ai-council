"""Pydantic data models shared across the POLIS backend."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class DeliberateRequest(BaseModel):
    """Incoming request to run the council on a problem statement."""

    problem: str = Field(
        ...,
        min_length=3,
        description="The decision or problem the user wants the council to reason about.",
    )


class AgentResult(BaseModel):
    """A single agent's structured contribution to the deliberation."""

    role: str
    analysis: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    objections: List[str] = Field(default_factory=list)
    recommendation: str


class DebateTimelineEntry(BaseModel):
    """One entry in the ordered debate timeline shown to the user."""

    step: int
    role: str
    message: str
    responding_to: Optional[str] = None


class ConsensusExplanation(BaseModel):
    """Justification behind the consensus tier, for the "Why this decision?"
    section of the Consensus Panel."""

    supporting_arguments: List[str] = Field(default_factory=list)
    main_objections: List[str] = Field(default_factory=list)
    reasoning: str


class ConsensusSummary(BaseModel):
    """The council's aggregated final answer."""

    final_recommendation: str
    overall_confidence: float = Field(..., ge=0.0, le=1.0)
    agreement_level: str
    key_risks: List[str] = Field(default_factory=list)
    key_objections: List[str] = Field(default_factory=list)
    dissenting_roles: List[str] = Field(default_factory=list)
    explanation: ConsensusExplanation


class CouncilMetrics(BaseModel):
    """Compact, heuristic council-level indicators for the Metrics panel.

    Derived from the same AgentResults as ConsensusSummary. risk_level and
    evidence_quality are proxies from the Risk/Research agents' own
    confidence and objections, not a measured quantity -- see
    docs/protocol.md#evidence-today.
    """

    council_confidence: float = Field(..., ge=0.0, le=1.0)
    agreement_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    evidence_quality: str


class DeliberateResponse(BaseModel):
    """Full response returned by POST /api/council/deliberate."""

    problem: str
    agents: List[AgentResult]
    timeline: List[DebateTimelineEntry]
    consensus: ConsensusSummary
    metrics: CouncilMetrics
    timestamp: str
    protocol_version: str
