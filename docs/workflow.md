# End-to-End Workflow

This walks through exactly what happens between a user typing a problem
and seeing a consensus on screen.

## 1. Input

The user types a decision or problem statement into `ProblemInput`
(`frontend/components/ProblemInput.tsx`) and submits it (button click or
Cmd/Ctrl+Enter).

## 2. Request

`frontend/lib/api.ts` posts `{ "problem": "<text>" }` to
`POST /api/council/deliberate` on the backend (`NEXT_PUBLIC_API_URL`,
defaulting to `http://localhost:8000`).

## 3. Validation

`app/api/routes.py` receives the request; FastAPI validates it against
`DeliberateRequest` (`app/models/schemas.py`) — the problem statement
must be at least 3 characters.

## 4. Deliberation

`run_council()` (`app/services/council.py`) runs the fixed pipeline:

```
Research Agent -> Planner Agent -> Critic Agent -> Risk Agent -> Ethics Agent -> Consensus Agent
```

Each agent's `analyze()` call receives the full list of prior agents'
`AgentResult`s as `context`, so later agents can reference or push back
on earlier ones (this is what the Critic Agent uses to challenge the
Planner, for instance). See [docs/agents.md](agents.md) for what each
role actually does and [design/council-deliberation.md](../design/council-deliberation.md)
for the sequence diagram.

Internally, each agent's `analyze()` delegates to the current reasoning
engine, `services/mock_reasoning.py::reason(role, problem, context)`,
which is deterministic and keyword-aware (no external API calls). See
[docs/agents.md](agents.md#reasoning-engine) for how this is swapped for
a real LLM later without touching the orchestrator.

## 5. Consensus

Once all five debating agents have spoken, `build_consensus()` computes:

- `overall_confidence` — mean confidence across agents, penalized for
  every objection raised (more objections → less certainty).
- `agreement_level` — High / Moderate / Low, thresholded on
  `overall_confidence`.
- `dissenting_roles` — agents whose confidence falls well below the
  group average.
- `final_recommendation` — the most confident agent's recommendation,
  with the top objections folded in as caveats.

The Consensus Agent then wraps this in an `AgentResult` so it appears
alongside the other agents in the UI, consistent with the detailed
`ConsensusSummary` panel. See
[design/consensus-flow.md](../design/consensus-flow.md).

## 6. Response

The backend returns a `DeliberateResponse`: the original problem, every
agent's `AgentResult` (including Consensus), the ordered debate
timeline, and the `ConsensusSummary`. Full shape documented in
[docs/api.md](api.md).

## 7. Session logging

Immediately after building the response, the API layer writes a
[POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md)-formatted session
record to `logs/session_<timestamp>_<id>.json`, containing the original
prompt, every agent's protocol message, the consensus, and a timestamp.
This does not block or alter the HTTP response — see
[docs/deployment.md](deployment.md#logging) and
[architecture/memory.md](../architecture/memory.md).

## 8. Rendering

The frontend renders three synchronized views over the same response:

- **Agent Perspectives grid** (`AgentCard.tsx`) — one card per agent.
- **Debate Timeline** (`DebateTimeline.tsx`) — the order agents spoke in.
- **Consensus panel** (`ConsensusPanel.tsx`) — final recommendation,
  confidence, agreement level, key risks/objections, dissenting agents.

Because the mock reasoning engine seeds its randomness from a hash of
`(role, problem)`, the same problem text always produces the same
council output — useful for demos and for verifying the pipeline hasn't
regressed.
