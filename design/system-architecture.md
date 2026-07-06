# Diagram: System Architecture

Layer-by-layer view of how a request moves through POLIS today. See
[docs/architecture.md](../docs/architecture.md) for the prose version.

```mermaid
flowchart TB
    subgraph Client["Frontend — Next.js"]
        UI["ProblemInput / AgentCard /\nDebateTimeline / ConsensusPanel"]
        APIClient["lib/api.ts — deliberate()"]
    end

    subgraph Backend["Backend — FastAPI"]
        Routes["api/routes.py\nPOST /api/council/deliberate"]
        Council["services/council.py\nOrchestrator"]
        Agents["agents/*.py\nBaseAgent subclasses"]
        Reasoning["services/mock_reasoning.py\nreason(role, problem, context)"]
        Schemas["models/schemas.py\nPydantic contracts"]
        Utils["utils/protocol.py + session_logger.py"]
        Config["config/settings.py"]
    end

    Logs[("logs/\nsession_*.json")]

    UI --> APIClient --> Routes
    Routes --> Council
    Council --> Agents --> Reasoning
    Council --> Schemas
    Routes --> Utils --> Logs
    Config --> Routes
    Config --> Utils
    Routes -->|DeliberateResponse| APIClient --> UI
```

## Notes

- The frontend never talks to `services/` or `agents/` directly — the
  API layer is the only seam it depends on, and that seam's shape is
  fixed by `models/schemas.py`.
- `utils/` sits beside, not inside, the request/response path: it
  converts the same `DeliberateResponse` into a logged record without
  altering what's sent back to the client.
- Swapping `mock_reasoning.py` for a real LLM module changes exactly one
  box in this diagram (`Reasoning`) — everything above and beside it is
  unaffected. See [docs/agents.md](../docs/agents.md#reasoning-engine).
