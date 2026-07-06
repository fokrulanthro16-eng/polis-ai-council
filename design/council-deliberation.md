# Diagram: Council Deliberation

The full fixed pipeline for one `POST /api/council/deliberate` call. See
[docs/workflow.md](../docs/workflow.md).

```mermaid
sequenceDiagram
    participant U as User (frontend)
    participant API as api/routes.py
    participant Council as council.py::run_council
    participant Research as Research Agent
    participant Planner as Planner Agent
    participant Critic as Critic Agent
    participant Risk as Risk Agent
    participant Ethics as Ethics Agent
    participant Consensus as Consensus Agent
    participant Log as logs/ (session_logger)

    U->>API: POST { problem }
    API->>Council: run_council(problem)
    Council->>Research: analyze(problem, [])
    Research-->>Council: AgentResult
    Council->>Planner: analyze(problem, [Research])
    Planner-->>Council: AgentResult
    Council->>Critic: analyze(problem, [Research, Planner])
    Critic-->>Council: AgentResult
    Council->>Risk: analyze(problem, [..., Critic])
    Risk-->>Council: AgentResult
    Council->>Ethics: analyze(problem, [..., Risk])
    Ethics-->>Council: AgentResult
    Council->>Council: build_consensus(results)
    Council->>Consensus: synthesize(problem, context, overall_confidence, final_recommendation)
    Consensus-->>Council: AgentResult
    Council-->>API: DeliberateResponse
    API->>Log: write_session_log(problem, response)
    API-->>U: DeliberateResponse
```

## Notes

- The pipeline is strictly sequential and fixed-order today (no
  parallel agents, no re-entrant rounds). This is a deliberate MVP
  simplification — see [architecture/scalability.md](../architecture/scalability.md)
  for what a multi-round or parallel debate model would require.
- Session logging happens after the response is assembled but is not on
  the critical path for the client — a logging failure is caught and
  does not turn a successful deliberation into a failed request.
