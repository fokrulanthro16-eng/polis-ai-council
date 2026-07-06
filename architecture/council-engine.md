# Council Engine

The council engine is `backend/app/services/council.py` plus the agent
adapters it drives. This is the part of POLIS that is actually novel —
everything else (FastAPI routing, Next.js rendering) is standard web
app plumbing around it.

## The pipeline is a fixed, ordered list

```python
_PIPELINE = [ResearchAgent(), PlannerAgent(), CriticAgent(), RiskAgent(), EthicsAgent()]
_CONSENSUS_AGENT = ConsensusAgent()
```

There is no dynamic routing, no voting on who speaks next, no
re-entrant rounds — every deliberation runs the same five roles in the
same order, then synthesizes. This is a deliberate MVP simplification:
a fixed pipeline is trivial to reason about, trivial to test (same
input always produces the same sequence of calls), and sufficient to
demonstrate the core value (visible, sequential, referencing
deliberation) without the complexity of a dynamic multi-agent
scheduler. See [architecture/scalability.md](scalability.md) for what a
dynamic pipeline would require.

## Context threading is what makes it a "debate," not five parallel opinions

```python
context: List[Dict] = []
for step, agent in enumerate(_PIPELINE, start=1):
    result = agent.analyze(problem, context)
    context.append(result.model_dump())
```

Each agent receives every prior agent's full `AgentResult` as `context`.
The mock reasoning engine's Critic builder, for example, reads
`context[-1]["role"]` to name who it's stress-testing. This is a
narrow use of context today (the mock engine mostly reacts to *whether*
prior objections exist, not their specific content in depth) — it's the
seam a real LLM reasoning engine would use much more richly, actually
reading and responding to the substance of prior agents' analysis.

## Consensus is deterministic arithmetic, not another model call

`build_consensus()` computes `overall_confidence`, `agreement_level`,
`dissenting_roles`, `key_risks`, `key_objections`, and
`final_recommendation` from the five `AgentResult`s using fixed rules
(mean confidence, an objection penalty, threshold buckets — see
[design/consensus-flow.md](../design/consensus-flow.md) for the exact
formula). This is intentional: consensus should be *auditable* — a
user should be able to recompute it by hand from the numbers shown on
each agent's card, not have to trust a second opaque model call to tell
them what the first five models meant.

## The Consensus Agent is not like the other five

Every other agent independently produces its own `confidence` and
`recommendation`. The Consensus Agent does not — `synthesize()` takes
the orchestrator's already-computed `overall_confidence` and
`final_recommendation` as parameters. This guarantees the Consensus
Agent's card in the UI can never contradict the `ConsensusSummary` panel
displayed alongside it, at the cost of the Consensus Agent not being a
fully independent voice. That tradeoff is deliberate — see
[design/consensus-flow.md](../design/consensus-flow.md#notes).

## The reasoning engine is the one designed seam

Every agent calls through `BaseAgent.analyze()` into
`reason(role, problem, context)`. That function's contract
(`RawAgentOutput` in, `AgentResult` out) is the entire interface between
"what the council does" (fixed) and "how each turn's content is
produced" (swappable). See
[docs/agents.md](../docs/agents.md#reasoning-engine) for the concrete
swap procedure, and [protocol/POLIS_PROTOCOL_V1.md](../protocol/POLIS_PROTOCOL_V1.md)
for the richer message shape a real reasoning engine's output is
already being logged in.
