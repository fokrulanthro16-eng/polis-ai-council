# Diagram: Consensus Flow

How five independent `AgentResult`s become one `ConsensusSummary`. See
`build_consensus()` in `backend/app/services/council.py` and
[docs/workflow.md](../docs/workflow.md).

```mermaid
flowchart LR
    R[Research] & P[Planner] & C[Critic] & K[Risk] & E[Ethics] --> Agg

    subgraph Agg["build_consensus()"]
        direction TB
        Avg["avg_confidence =\nmean(confidences)"]
        Pen["objection_penalty =\nmin(0.25, 0.04 * total_objections)"]
        Overall["overall_confidence =\nmax(0.05, avg - penalty)"]
        Level["agreement_level:\n>=0.75 High\n>=0.55 Moderate\nelse Low"]
        Dissent["dissenting_roles:\nconfidence < avg - 0.15"]
        Lead["lead = argmax(confidence)"]
        Final["final_recommendation =\nlead.recommendation\n+ top 2 objections as caveat"]

        Avg --> Pen --> Overall --> Level
        Avg --> Dissent
        Lead --> Final
    end

    Agg --> Summary["ConsensusSummary"]
    Summary --> Card["Consensus Agent card\n(synthesize)"]
```

## Notes

- Consensus is **arithmetic, not another LLM call**: it is fully
  deterministic given the five upstream `AgentResult`s, which keeps the
  final answer auditable — you can recompute it by hand from the
  numbers shown on each agent's card.
- `key_risks` is intentionally sourced only from the Risk Agent's
  objections; `key_objections` pools every agent's objections. Both are
  surfaced in the UI's Consensus panel, not just used internally.
- Because the Consensus Agent's card is built from the same
  orchestrator-computed values as the `ConsensusSummary` panel, the two
  can never disagree with each other in the UI.
