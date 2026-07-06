"""Deterministic, keyword-aware "reasoning" used when no LLM API key is configured.

This is the default reasoning engine for POLIS. It does not call any external
service, so the whole council can run offline and for free. It looks at the
problem text for topical keywords (cost, security, timeline, people, etc.) and
uses that to select from role-specific analysis, objection, and recommendation
templates. A stable hash of (role, problem) seeds the RNG so the same problem
always produces the same council output, which keeps demos reproducible.

To swap in a real LLM later, implement the same signature
(`reason(role, problem, context) -> RawAgentOutput`) in a new module (e.g.
``llm_reasoning.py``) and select it in ``council.py`` based on whether an API
key is present in the environment.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RawAgentOutput:
    analysis: str
    confidence: float
    objections: List[str] = field(default_factory=list)
    recommendation: str = ""


# Keyword -> topical fragments used to make the mock analysis feel grounded in
# the actual problem text rather than fully generic.
_TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "cost": ["budget", "cost", "expensive", "cheap", "funding", "price", "money"],
    "timeline": [
        "deadline",
        "urgent",
        "asap",
        "quickly",
        "timeline",
        "launch date",
        "schedule",
    ],
    "people": ["team", "hire", "staff", "employee", "layoff", "customer", "user"],
    "technology": [
        "migrate",
        "system",
        "platform",
        "software",
        "infrastructure",
        "api",
        "database",
    ],
    "safety": ["safety", "risk", "danger", "harm", "security", "privacy", "compliance"],
    "growth": ["expand", "scale", "growth", "market", "launch", "new product"],
}


def _detect_topics(problem: str) -> List[str]:
    lowered = problem.lower()
    found = [
        topic
        for topic, kws in _TOPIC_KEYWORDS.items()
        if any(kw in lowered for kw in kws)
    ]
    return found or ["general"]


def _seeded_random(role: str, problem: str) -> random.Random:
    digest = hashlib.sha256(f"{role}:{problem}".encode("utf-8")).hexdigest()
    return random.Random(int(digest[:16], 16))


def _shorten(problem: str, max_len: int = 80) -> str:
    problem = problem.strip()
    return problem if len(problem) <= max_len else problem[: max_len - 1].rstrip() + "…"


def reason(role: str, problem: str, context: List[Dict]) -> RawAgentOutput:
    """Produce a mock but problem-aware reasoning output for a given agent role.

    ``context`` holds the AgentResult dicts of agents that already spoke this
    round, so later agents (Critic, Risk, Ethics, Consensus) can reference or
    push back on earlier ones.
    """
    rng = _seeded_random(role, problem)
    topics = _detect_topics(problem)
    short_problem = _shorten(problem)

    builder = _ROLE_BUILDERS.get(role)
    if builder is None:
        raise ValueError(f"No mock reasoning builder registered for role '{role}'")
    return builder(rng, short_problem, topics, context)


def _confidence(rng: random.Random, low: float, high: float) -> float:
    return round(rng.uniform(low, high), 2)


def _research_builder(rng, problem, topics, context) -> RawAgentOutput:
    topic_line = ", ".join(topics)
    analysis = (
        f'Reviewing available information on: "{problem}". '
        f"The relevant topic areas appear to be: {topic_line}. "
        "Based on comparable precedents and general domain knowledge, "
        "the situation has enough structure to support a reasoned recommendation, "
        "though direct, up-to-date data specific to this exact case is limited."
    )
    objections = []
    if rng.random() < 0.5:
        objections.append(
            "Available information may be incomplete or out of date; confirm with primary sources before acting."
        )
    return RawAgentOutput(
        analysis=analysis,
        confidence=_confidence(rng, 0.55, 0.8),
        objections=objections,
        recommendation="Gather one or two additional data points before finalizing, but proceed with the analysis in hand.",
    )


def _planner_builder(rng, problem, topics, context) -> RawAgentOutput:
    steps = rng.randint(3, 5)
    research = context[0] if context else None
    lead_in = (
        f"Building on the {research['role']}'s findings, breaking"
        if research
        else "Breaking"
    )
    analysis = (
        f'{lead_in} "{problem}" into a concrete plan of roughly {steps} phases: '
        "clarify the objective and constraints, evaluate the realistic options, "
        "select the option with the best effort-to-impact ratio, and define how success will be measured. "
        "A phased rollout reduces the chance of a costly all-at-once mistake."
    )
    objections = []
    if "timeline" in topics:
        objections.append(
            "The apparent time pressure may force skipping validation steps that would normally de-risk this plan."
        )
    return RawAgentOutput(
        analysis=analysis,
        confidence=_confidence(rng, 0.6, 0.85),
        objections=objections,
        recommendation="Adopt a phased rollout with a clear go/no-go checkpoint after the first phase.",
    )


def _critic_builder(rng, problem, topics, context) -> RawAgentOutput:
    prior = context[-1] if context else None
    target_role = prior["role"] if prior else "the council"
    target_claim = prior["recommendation"] if prior and prior["recommendation"] else "the proposal so far"
    analysis = (
        f"I disagree with part of the {target_role}'s proposal on \"{problem}\": it assumes conditions stay "
        f'stable and that "{target_claim}" is accurate, but neither assumption is guaranteed. '
        "A credible plan should name its weakest link explicitly."
    )
    objections = [
        "The proposed plan has not clearly stated what would count as failure or trigger a course correction.",
    ]
    if rng.random() < 0.5:
        objections.append(
            "Optimistic assumptions about timeline or resourcing were not stress-tested against a worse-case scenario."
        )
    return RawAgentOutput(
        analysis=analysis,
        confidence=_confidence(rng, 0.45, 0.7),
        objections=objections,
        recommendation="Add an explicit failure condition and a fallback option before committing.",
    )


def _risk_builder(rng, problem, topics, context) -> RawAgentOutput:
    risk_focus = (
        "financial exposure"
        if "cost" in topics
        else (
            "operational disruption"
            if "technology" in topics
            else (
                "personnel impact"
                if "people" in topics
                else "unforeseen downstream effects"
            )
        )
    )
    critic = next((c for c in context if c["role"] == "Critic Agent"), None)
    lead_in = (
        f"The Critic raises an important point — {critic['objections'][0].rstrip('.')} — so "
        if critic and critic["objections"]
        else "Building on the discussion so far, "
    )
    analysis = (
        f'{lead_in}assessing downside exposure for "{problem}", with particular attention to {risk_focus}. '
        "Worst-case impact appears moderate rather than catastrophic, but the probability of at least one "
        "assumption failing is non-trivial given the information available."
    )
    objections = [
        f"Insufficient contingency plan for {risk_focus} if the primary approach underperforms."
    ]
    return RawAgentOutput(
        analysis=analysis,
        confidence=_confidence(rng, 0.5, 0.75),
        objections=objections,
        recommendation=f"Define a specific contingency plan for {risk_focus} before proceeding, and set a review checkpoint.",
    )


def _ethics_builder(rng, problem, topics, context) -> RawAgentOutput:
    stakeholder_focus = (
        "employees and customers" if "people" in topics else "affected stakeholders"
    )
    risk = next((c for c in context if c["role"] == "Risk Agent"), None)
    lead_in = (
        "From an ethical perspective, building on the Risk Agent's assessment, "
        if risk
        else "From an ethical perspective, "
    )
    analysis = (
        f'{lead_in}considering fairness, transparency, and impact on {stakeholder_focus} for "{problem}". '
        "No clear ethical red flag is evident, but the decision should be communicated transparently "
        "to those affected, and any trade-offs made explicit rather than implicit."
    )
    objections = []
    if "safety" in topics:
        objections.append(
            "Given the safety/compliance dimension, an independent review before rollout is warranted."
        )
    if rng.random() < 0.4:
        objections.append(
            f"Ensure {stakeholder_focus} are informed of the decision and its rationale, not just its outcome."
        )
    return RawAgentOutput(
        analysis=analysis,
        confidence=_confidence(rng, 0.6, 0.85),
        objections=objections,
        recommendation=f"Proceed, but communicate the decision and its trade-offs transparently to {stakeholder_focus}.",
    )


def _consensus_builder(rng, problem, topics, context) -> RawAgentOutput:
    # Consensus is computed numerically in council.py from the other agents;
    # this builder only supplies a narrative analysis field for display.
    roles_so_far = [c["role"] for c in context]
    span = (
        f"all viewpoints from {roles_so_far[0]} through {roles_so_far[-1]}"
        if len(roles_so_far) > 1
        else "the council's viewpoint"
    )
    analysis = (
        f'After reviewing {span} on "{problem}", synthesizing the council\'s perspectives into a single '
        "actionable recommendation, weighing each agent's confidence and objections rather than simply "
        "averaging opinions."
    )
    return RawAgentOutput(
        analysis=analysis, confidence=0.0, objections=[], recommendation=""
    )


_ROLE_BUILDERS = {
    "Research Agent": _research_builder,
    "Planner Agent": _planner_builder,
    "Critic Agent": _critic_builder,
    "Risk Agent": _risk_builder,
    "Ethics Agent": _ethics_builder,
    "Consensus Agent": _consensus_builder,
}
