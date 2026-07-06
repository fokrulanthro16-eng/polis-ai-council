# Diagram: Agent Workflow

How a single agent's turn works inside the pipeline. See
[docs/agents.md](../docs/agents.md).

```mermaid
sequenceDiagram
    participant O as Orchestrator (council.py)
    participant A as Agent (e.g. Risk Agent)
    participant R as reason() (mock_reasoning.py)

    O->>A: analyze(problem, context)
    Note over A: context = every prior<br/>agent's AgentResult so far
    A->>R: reason(role, problem, context)
    Note over R: seed RNG from SHA-256(role, problem)<br/>detect topic keywords<br/>select role-specific builder
    R-->>A: RawAgentOutput<br/>(analysis, confidence, objections, recommendation)
    A-->>O: AgentResult(role, ...)
    O->>O: append to results[]<br/>append to context[]<br/>append DebateTimelineEntry
```

## Notes

- `context` grows by one entry per turn, so the sixth participant
  (Critic) has visibility into five prior results; the first
  participant (Research) has none.
- `reason()` is a pure function: same `(role, problem, context)` in,
  same `RawAgentOutput` out. That determinism is what makes council
  output reproducible across runs — see
  [docs/workflow.md](../docs/workflow.md).
- Replacing `R` with an LLM-backed implementation changes nothing about
  this sequence — the contract (`RawAgentOutput` in, `AgentResult` out)
  stays identical.
