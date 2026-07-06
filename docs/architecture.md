# Architecture Overview

This is the onboarding-level map of how POLIS is built. For deep dives
see [architecture/](../architecture/) (per-layer detail),
[design/](../design/) (Mermaid diagrams), and
[protocol/](../protocol/) (the inter-agent message spec).

## System at a glance

```
polis/
  backend/                 FastAPI service (Python)
    app/
      main.py               App entrypoint, CORS, health check
      config/               Environment/settings resolution
      models/               Pydantic request/response schemas
      agents/                One class per council member (thin adapters)
      services/              Orchestration (council) + reasoning engine
      utils/                 Session logging, protocol adapter
      api/                   HTTP routes
    requirements.txt
    .env.example
  frontend/                Next.js + React + TypeScript
    app/                     Pages (App Router)
    components/              ProblemInput, AgentCard, DebateTimeline, ConsensusPanel
    lib/                      API client, shared types, role color mapping
  docs/                     Narrative documentation (this directory)
  design/                   Mermaid architecture/workflow diagrams
  protocol/                 POLIS Protocol v1 specification
  architecture/             Deep-dive per-layer documentation
  paper/                    Positioning as an ACI platform (abstract, innovation, future work)
  logs/                     Generated council session records (session.json per run)
  docker-compose.yml
```

## Layers

1. **Frontend (Next.js)** — collects a problem statement, calls the
   backend, and renders three views over the same response: per-agent
   cards, a debate timeline, and a consensus panel. Stateless; all
   reasoning happens server-side.
2. **API layer (`backend/app/api/`)** — a single FastAPI router exposing
   `POST /api/council/deliberate`. Thin: it validates input via Pydantic
   and delegates to the service layer.
3. **Service layer (`backend/app/services/`)** — `council.py` is the
   orchestrator: it runs the agent pipeline in a fixed order, threads
   each agent's output into the next agent's context, and computes the
   final consensus. `mock_reasoning.py` is the current reasoning engine
   (deterministic, keyword-aware, no API keys required).
4. **Agent layer (`backend/app/agents/`)** — one thin class per council
   role. Agents don't implement reasoning themselves; they delegate to
   the reasoning engine and shape the result into the shared
   `AgentResult` schema. This is what makes swapping in a real LLM later
   a one-file change (see [docs/agents.md](agents.md)).
5. **Model layer (`backend/app/models/`)** — Pydantic schemas that define
   the API contract (`DeliberateRequest`, `AgentResult`,
   `DebateTimelineEntry`, `ConsensusSummary`, `DeliberateResponse`).
6. **Utility layer (`backend/app/utils/`)** — cross-cutting concerns that
   aren't business logic: converting an `AgentResult` into a
   [POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) message, and
   writing the per-session log file to `logs/`.
7. **Config layer (`backend/app/config/`)** — resolves environment
   variables (allowed CORS origins, log directory) into typed settings
   used by `main.py` and `utils/`.

## Why this shape

The layering mirrors a standard backend service (API → service →
domain/agents → models) plus two additions specific to a multi-agent
product: a **protocol** that standardizes what an agent's output looks
like regardless of what powers its reasoning, and a **session log** that
makes every deliberation independently auditable after the fact. Neither
addition changes the existing request/response contract the frontend
depends on — see [docs/api.md](api.md).

## Data flow, briefly

`ProblemInput` (frontend) → `POST /api/council/deliberate` → `run_council()`
runs Research → Planner → Critic → Risk → Ethics → Consensus in order →
`DeliberateResponse` returned to the frontend → session written to
`logs/`. The full sequence diagram is in
[design/agent-workflow.md](../design/agent-workflow.md) and
[design/council-deliberation.md](../design/council-deliberation.md).
