# Backend Layers

The backend is a Python/FastAPI service under `backend/app/`, organized
into seven packages. Each has one job.

```
app/
  main.py       Composition root: builds the FastAPI app, wires CORS, mounts routes.
  config/       Resolves environment variables into typed settings.
  api/          HTTP routing. Validates input, delegates, returns.
  services/     Business logic: orchestration (council.py) + reasoning (mock_reasoning.py).
  agents/       One thin adapter class per council role.
  models/       Pydantic schemas — the API contract.
  utils/        Cross-cutting concerns: protocol adapter, session logger.
```

## `config/`

`settings.py` centralizes everything previously read ad hoc via
`os.getenv()` in `main.py`: allowed CORS origins and the logs directory
path. `main.py` and `utils/session_logger.py` both import from here
instead of touching the environment directly. This is the only file
that should call `os.getenv()`.

## `api/`

`routes.py` defines one router, one endpoint:
`POST /api/council/deliberate`. Its job is strictly: validate the
request via `DeliberateRequest`, call `services.council.run_council()`,
best-effort log the session via `utils.session_logger`, and return the
`DeliberateResponse`. It contains no business logic — if you're tempted
to add an `if` statement that changes what the council does, it belongs
in `services/`, not here.

## `services/`

- **`council.py`** — the orchestrator. Owns `_PIPELINE` (agent order),
  `run_council()` (runs the pipeline, builds the timeline), and
  `build_consensus()` (the arithmetic that turns five `AgentResult`s
  into a `ConsensusSummary`). This is the single place that knows the
  council's *shape* — how many agents, what order, how they're
  aggregated.
- **`mock_reasoning.py`** — the current reasoning engine. Deterministic,
  keyword-aware, no network calls. Exposes one function,
  `reason(role, problem, context) -> RawAgentOutput`, that every agent
  calls through `BaseAgent.analyze()`. See
  [docs/agents.md](../docs/agents.md#reasoning-engine) for the LLM swap
  path.

## `agents/`

Each agent is a `BaseAgent` subclass that sets a `role` string and
nothing else, except `ConsensusAgent`, which overrides with
`synthesize()` to accept orchestrator-computed values instead of
generating its own. Agents intentionally hold zero reasoning logic —
that's what makes the reasoning engine swappable without touching six
files instead of one.

## `models/`

`schemas.py` is the API contract: `DeliberateRequest`, `AgentResult`,
`DebateTimelineEntry`, `ConsensusSummary`, `DeliberateResponse`. This is
the one file the frontend's `lib/types.ts` must be kept manually in
sync with (see [docs/api.md](../docs/api.md#source-of-truth)).

## `utils/`

New in this upgrade. Two responsibilities, both side-effecting but
neither on the request's critical path:

- **`protocol.py`** — converts an `AgentResult` into a
  [POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) message dict
  (adds `agent`, `goal`, `evidence`, `timestamp`).
- **`session_logger.py`** — writes one JSON file per deliberation to
  `logs/`, built from protocol messages. Failure to write is caught and
  logged via Python's standard `logging` module; it never raises out to
  the API layer, since a full disk or a permissions issue writing an
  audit log is not a reason to fail a successful deliberation.

## What did *not* change

`agents/*.py`, `services/council.py`, `services/mock_reasoning.py`, and
`models/schemas.py` are unchanged in behavior by this upgrade — the
restructuring added `config/` and `utils/` and moved environment
resolution out of `main.py`; it did not touch the deliberation logic or
the API contract.
