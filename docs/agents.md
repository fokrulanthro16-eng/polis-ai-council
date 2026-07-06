# Agents

The council is a fixed pipeline of six roles. Five debate in sequence;
the sixth synthesizes their output.

| Order | Agent | Class | Mandate |
|---|---|---|---|
| 1 | Research Agent | `agents/research_agent.py` | Gather and summarize relevant background and context for the problem. |
| 2 | Planner Agent | `agents/planner_agent.py` | Turn the problem into a concrete, phased plan. |
| 3 | Critic Agent | `agents/critic_agent.py` | Stress-test the plan so far; surface weak assumptions and gaps. |
| 4 | Risk Agent | `agents/risk_agent.py` | Assess downside exposure and propose contingencies. |
| 5 | Ethics Agent | `agents/ethics_agent.py` | Evaluate fairness, transparency, and stakeholder impact. |
| 6 | Consensus Agent | `agents/consensus_agent.py` | Synthesize every agent's confidence and objections into one final recommendation. |

The **Orchestrator** is not a card in the UI — it's `services/council.py`,
which runs the pipeline, threads context between agents, and computes
the numeric consensus that the Consensus Agent's card displays.

## Shared output shape

Every debating agent returns an `AgentResult`
(`backend/app/models/schemas.py`):

```json
{
  "role": "Risk Agent",
  "analysis": "...",
  "confidence": 0.68,
  "objections": ["..."],
  "recommendation": "..."
}
```

This is the **live API contract** the frontend depends on today — see
[docs/api.md](api.md). It is a stable subset of the richer
[POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) message shape used
internally for session logs (adds `agent`, `goal`, `evidence`, and
`timestamp`). See [docs/protocol.md](protocol.md) for how the two relate.

## How an agent works

Every agent is a thin subclass of `BaseAgent` (`agents/base.py`) that
only sets a `role` string:

```python
class ResearchAgent(BaseAgent):
    role = "Research Agent"
```

`BaseAgent.analyze(problem, context)` delegates to the reasoning engine
and wraps its output in an `AgentResult`. Agents hold no reasoning logic
of their own — this is deliberate, see below.

The Consensus Agent is the one exception: its `synthesize()` method
takes the orchestrator-computed `overall_confidence` and
`final_recommendation` as arguments, rather than generating them
independently, so its card always agrees with the `ConsensusSummary`
panel shown next to it.

## Reasoning engine

Agents don't decide *how* to reason — that's delegated to a swappable
function: `reason(role: str, problem: str, context: List[Dict]) -> RawAgentOutput`.

There are two implementations of that signature, and `agents/base.py`
picks between them on every call based on
`llm_providers.factory.get_provider()`:

- **`services/mock_reasoning.py`** — a deterministic, keyword-aware
  generator with no external dependencies. It looks for topical
  keywords (cost, timeline, people, technology, safety, growth) in the
  problem text and selects from role-specific analysis/objection/
  recommendation templates. A SHA-256 hash of `(role, problem)` seeds
  the RNG, so the same problem text always produces the same council
  output. This is the default, and requires no configuration.
- **`services/llm_reasoning.py`** — calls a real LLM provider (see
  `services/llm_providers/`), using a per-role system prompt from
  `agents/prompts.py`, and parses its JSON response into a
  `RawAgentOutput`. Active only when `POLIS_LLM_PROVIDER` is set (see
  "Configuring a real LLM provider" below).

**Fallback is layered, not all-or-nothing:**

1. If no provider is configured, or the configured one fails to
   initialize (missing SDK, missing API key, unknown name),
   `get_provider()` returns `None` and `agents/base.py` uses
   `mock_reasoning` for the whole run.
2. Even with a provider active, if a single API call fails or returns
   text `llm_reasoning.py` can't parse into a valid `RawAgentOutput`,
   only *that agent's turn* falls back to `mock_reasoning` — one flaky
   call never fails the whole deliberation.

No other file needs to change to swap reasoning engines: the
orchestrator, the API layer, the POLIS Protocol logging, and the
frontend are all decoupled from how reasoning is produced. This is the
seam the whole layering in [docs/architecture.md](architecture.md) is
built around.

### Configuring a real LLM provider

1. Install the optional SDK for the provider you want (see
   `backend/requirements-llm.txt`), e.g. `pip install anthropic`.
2. Set that provider's API key in `backend/.env` (see `.env.example`
   for `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY`).
3. Set `POLIS_LLM_PROVIDER=anthropic` (or `openai` / `gemini`) in
   `backend/.env`.

An API key alone does not switch anything on — `POLIS_LLM_PROVIDER`
must be set explicitly. See `docs/deployment.md` for the full
environment variable reference.

## Per-role definitions

Every role has three distinct pieces, all defined in one place —
`agents/roles.py`'s `AGENT_ROLES` — so they can't drift out of sync
with each other:

- **`system_prompt`** — the persona and mandate handed to the LLM as
  its system instruction. Consumed by `services/llm_reasoning.py` via
  `agents/prompts.py`'s `ROLE_PERSONAS` (a thin derived view over
  `AGENT_ROLES`, kept as a separate module so that import stays a
  plain `Dict[str, str]` lookup).
- **`description`** — a short, human-readable summary of what the role
  does (the "Mandate" column above).
- **`objective`** — the one-sentence decision objective logged as the
  `goal` field in every POLIS Protocol v1 message. Consumed by
  `utils/protocol.py`'s `_ROLE_GOALS` (also derived from
  `AGENT_ROLES`).

## Adding a new agent role

1. Create `agents/<role>_agent.py` with a `BaseAgent` subclass and a
   `role` string.
2. Add an entry for it in `agents/roles.py`'s `AGENT_ROLES` (system
   prompt, description, objective) so it works under both reasoning
   engines and logs a meaningful `goal` in session logs.
3. Add a builder function for it in `mock_reasoning.py`'s
   `_ROLE_BUILDERS`.
4. Insert it into `_PIPELINE` in `services/council.py` at the position
   you want it to speak.

No frontend changes are required — `AgentCard` renders whatever roles
are present in the response.
