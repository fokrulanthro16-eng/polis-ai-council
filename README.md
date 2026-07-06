# POLIS — Collective Intelligence for Complex Decisions

POLIS is an **Artificial Collective Intelligence (ACI) platform**:
instead of asking one AI for an answer, you ask a **council of
specialized agents** — Research, Planner, Critic, Risk, Ethics, and
Consensus — who each analyze a problem from their own angle, see what
the agents before them said, and are free to object. The council
converges on a single, transparent consensus, complete with confidence
scores, objections, and dissenting opinions, instead of collapsing
everything into one opaque answer.

This is a working MVP that runs fully local and offline by default (a
deterministic mock reasoning engine, no paid API keys required), and
can optionally be switched to real LLM reasoning (Anthropic, OpenAI, or
Gemini) via one environment variable, without touching the
orchestrator, the protocol, or the frontend.

## Project Vision

Hard decisions rarely have one right answer viewed from one angle. A
layoff decision has a financial angle, a people angle, a risk angle,
and an ethics angle — a good decision-maker weighs all of them, not
just the loudest one. POLIS makes that process explicit and visible:
every agent's reasoning, confidence, and objections are shown side by
side, so the final consensus is *explainable*, not a black box.

Full vision, principles, and scope: **[docs/vision.md](docs/vision.md)**.

## Architecture

```
polis/
  backend/                 FastAPI service (Python)
    app/
      main.py               App entrypoint, CORS, health check
      config/               Environment/settings resolution
      models/                Pydantic request/response schemas
      agents/                One class per council member (thin adapters)
      services/
        mock_reasoning.py     Deterministic, keyword-aware reasoning (no API keys needed)
        council.py             Orchestrator: runs agents in order, builds the timeline + consensus
      utils/                 Session logging + POLIS Protocol v1 adapter
      api/                   POST /api/council/deliberate
    requirements.txt
    .env.example
  frontend/                Next.js + React + TypeScript
    app/                     Pages (App Router): layout, main page, global styles
    components/              Hero, CouncilProcess, ScenarioPicker, ProblemInput,
                              AgentCard, DebateTimeline, ConsensusPanel
    lib/                      API client, shared types, demo scenarios, role color mapping
  docs/                     Vision, architecture, workflow, agents, protocol, API, deployment docs
  design/                   Mermaid diagrams (system, workflow, deliberation, consensus, memory)
  protocol/                 POLIS Protocol v1 specification + JSON Schema
  architecture/             Deep-dive docs: backend/frontend layers, council engine, memory, scalability
  paper/                    Positioning as an ACI platform: abstract, innovation, future work
  logs/                     Generated council session records (git-ignored; see logs/README.md)
  docker-compose.yml
```

For a guided tour, start with **[docs/architecture.md](docs/architecture.md)**
and **[design/system-architecture.md](design/system-architecture.md)**.

### The council

| Agent | Role |
|---|---|
| **Orchestrator** | Runs the agents in sequence, wires each agent's output into the next agent's context, and assembles the debate timeline (implemented as `services/council.py`, not a separate card in the UI) |
| **Research Agent** | Surfaces relevant background and context for the problem |
| **Planner Agent** | Turns the problem into a concrete, phased plan |
| **Critic Agent** | Stress-tests the plan, challenges assumptions from prior agents |
| **Risk Agent** | Assesses downside exposure and proposes contingencies |
| **Ethics Agent** | Considers fairness, transparency, and stakeholder impact |
| **Consensus Agent** | Synthesizes every agent's confidence and objections into one final recommendation |

Full role-by-role detail: **[docs/agents.md](docs/agents.md)**. Sequence
and consensus math diagrams: **[design/council-deliberation.md](design/council-deliberation.md)**,
**[design/consensus-flow.md](design/consensus-flow.md)**.

Every agent's live API response follows this shape (documented in full
in **[docs/api.md](docs/api.md)**):

```json
{
  "role": "Risk Agent",
  "analysis": "...",
  "confidence": 0.68,
  "objections": ["..."],
  "recommendation": "..."
}
```

Internally, every session is also logged in the richer
**[POLIS Protocol v1](protocol/POLIS_PROTOCOL_V1.md)** message format
(adds `agent`, `goal`, `evidence`, `timestamp`) — see
**[docs/protocol.md](docs/protocol.md)** for how the two relate.

## Features

- **Multi-agent deliberation** — six accountable roles debate in a
  fixed, ordered pipeline, each seeing every prior agent's output.
- **Three built-in demo scenarios** — climate-resilient city planning,
  AI education policy, and healthcare resource allocation, one click to
  load into the council.
- **A visible council process** — a Problem → Agents → Debate →
  Consensus → Decision stepper shows where the deliberation is at all
  times.
- **Transparent consensus** — an auditable aggregation (confidence,
  objections, and dissent all weighed together into an Agreement Level
  of Strong / Moderate / Weak / Highly Contested) instead of an opaque
  synthesis step, with a "Why this decision?" breakdown of supporting
  arguments and objections, plus a compact Council Metrics panel
  (confidence, agreement score, risk level, evidence quality).
- **Runs fully offline** — the reference reasoning engine is
  deterministic and keyword-aware; no API keys, no network calls, and
  the same problem always reproduces the same council output.
- **A versioned communication protocol** — [POLIS Protocol v1](protocol/POLIS_PROTOCOL_V1.md),
  already used for structured session logging.
- **Session logging** — every deliberation is recorded to `logs/` as a
  structured, protocol-conformant JSON record.
- **Real LLM reasoning, optional** — swap in Anthropic, OpenAI, or
  Gemini with one environment variable (see "Configuring a real LLM
  provider" below); nothing else in the stack needs to change, and
  leaving it unset keeps the mock engine.

## Screenshots

*(placeholder — capture these once the app is running locally and drop
the images into `frontend/public/screenshots/`, then swap the paths
below)*

| | |
|---|---|
| **Landing + demo scenarios**<br>`frontend/public/screenshots/landing.png` | **Council process + agent cards**<br>`frontend/public/screenshots/agents.png` |
| ![Landing page with hero and scenario picker](frontend/public/screenshots/landing.png) | ![Agent perspectives grid with confidence bars](frontend/public/screenshots/agents.png) |
| **Debate timeline**<br>`frontend/public/screenshots/timeline.png` | **Consensus panel**<br>`frontend/public/screenshots/consensus.png` |
| ![Debate timeline showing agents responding to each other](frontend/public/screenshots/timeline.png) | ![Consensus panel with final decision, confidence, risks, and dissent](frontend/public/screenshots/consensus.png) |

## Installation

### Prerequisites

- Python 3.10+ (any recent version works)
- Node.js 18+ and npm

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env.local  # Windows
# cp .env.example .env.local  # macOS/Linux
```

## Running

### Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API is now running at `http://localhost:8000`. Check it with:
`curl http://localhost:8000/api/health`.

### Frontend

In a second terminal:

```bash
cd frontend
npm run dev
```

Open `http://localhost:3000` in your browser.

### Docker (optional)

```bash
docker compose up --build
```

Backend: `http://localhost:8000`, Frontend: `http://localhost:3000`.
Full deployment notes, environment variables, and production
considerations: **[docs/deployment.md](docs/deployment.md)**.

### Demo flow

1. Open `http://localhost:3000`.
2. Click one of the three **demo scenario** cards (climate planning, AI
   education policy, healthcare resource allocation) to load a
   ready-made problem — or type your own, e.g.:
   *"Should our startup lay off 20% of staff to cut costs before the next funding round?"*
3. Click **Run Council** (or press Cmd/Ctrl + Enter). The **Problem →
   Agents → Debate → Consensus → Decision** stepper tracks progress.
4. Watch the **Agent Perspectives** grid populate — each card shows that
   agent's analysis, confidence score, key recommendation, and objections.
5. Scroll to the **Debate Timeline** to see the order agents spoke in and how
   later agents responded to earlier ones.
6. Check the **Council Metrics** panel for an at-a-glance read (council
   confidence, agreement score, risk level, evidence quality), then the
   **Consensus** panel for the final decision, confidence score, top
   risks, dissenting opinions, and a "Why this decision?" breakdown of
   the supporting arguments and objections behind it.
7. Try a few different problems — the mock reasoning engine picks up on
   keywords (cost, timeline, safety, people, technology, growth) so different
   problems surface different emphases, while staying deterministic (the same
   problem text always produces the same council output). Full walkthrough:
   **[docs/workflow.md](docs/workflow.md)**. Presenting this live?
   Use **[docs/demo-script.md](docs/demo-script.md)** for a timed talk track.

## Configuring a real LLM provider

By default POLIS runs on `backend/app/services/mock_reasoning.py` — a
deterministic, offline reasoning engine, no API key required. To have
the council reason with a real model instead:

1. **Install the SDK** for the provider you want (see
   `backend/requirements-llm.txt`):
   ```bash
   pip install anthropic            # or: openai / google-generativeai
   ```
2. **Set the API key** in `backend/.env` (copy from `.env.example`):
   ```bash
   ANTHROPIC_API_KEY=sk-...         # or OPENAI_API_KEY / GEMINI_API_KEY
   ```
3. **Select the provider** — this is the switch that actually turns it on:
   ```bash
   POLIS_LLM_PROVIDER=anthropic     # or: openai / gemini
   ```

`backend/.env` is loaded automatically on backend startup (see
`app/config/settings.py`) — no shell exports needed, and it's
git-ignored so keys never get committed.

That's it — restart the backend and every agent now reasons through the
selected model, each with its own system prompt (see
`backend/app/agents/roles.py`). Setting an API key alone does nothing
without `POLIS_LLM_PROVIDER`; and if the selected provider's key or SDK
is missing, or a call fails at runtime, POLIS logs a warning and falls
back to the mock engine rather than erroring out. Model choice per
provider can be overridden with `POLIS_ANTHROPIC_MODEL` /
`POLIS_OPENAI_MODEL` / `POLIS_GEMINI_MODEL`.

### Quick start: switching between Mock and Gemini

```bash
# 1. Install Gemini's SDK
pip install google-generativeai

# 2. backend/.env
GEMINI_API_KEY=your-key-here
POLIS_LLM_PROVIDER=gemini

# 3. Restart the backend — that's the whole switch.
uvicorn app.main:app --reload --port 8000
```

To switch back to the mock engine, remove or comment out
`POLIS_LLM_PROVIDER` in `backend/.env` (or set it to an empty string)
and restart. No code changes, no frontend changes — the API response
shape is identical either way.

No other file needs to change — agents, the orchestrator, the POLIS
Protocol, and the frontend are all decoupled from how reasoning is
produced. See **[docs/agents.md](docs/agents.md#reasoning-engine)** and
**[docs/deployment.md](docs/deployment.md#environment-variables)** for
full detail.

## Future Roadmap

1. Promoting [POLIS Protocol v1](protocol/POLIS_PROTOCOL_V1.md) from
   logs-only to the live API once `evidence` can be meaningfully populated.
2. Episodic memory — retrieval over past session logs (see
   [architecture/memory.md](architecture/memory.md)).
3. Dynamic council composition — letting the orchestrator choose which
   roles are relevant per problem.
4. Formal evaluation against single-model baselines.

Full detail and explicit non-goals: **[paper/future-work.md](paper/future-work.md)**.

## Contributors

- Project lead / architecture: see repository commit history.
- Contributions welcome — see [docs/architecture.md](docs/architecture.md)
  and [architecture/](architecture/) before proposing structural changes,
  since the layering is deliberate.

## License

No license has been chosen yet for this repository — until a `LICENSE`
file is added, all rights are reserved by the project owner. Add one
(e.g. MIT, Apache-2.0) before any public release or external
contribution.

## Notes

- No paid API keys are required to run this MVP — everything works offline
  via the mock reasoning engine.
- CORS on the backend defaults to allowing `http://localhost:3000`; change
  `POLIS_ALLOWED_ORIGINS` in `backend/.env` if you serve the frontend from a
  different origin.
- Every deliberation is logged to `logs/` — see
  [docs/deployment.md#logging](docs/deployment.md#logging).
