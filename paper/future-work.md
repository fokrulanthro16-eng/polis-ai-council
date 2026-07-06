# Future Work

Concrete, scoped next steps, ordered roughly by dependency (each below
generally requires the ones above it).

## 1. A real reasoning backend

Implement `services/llm_reasoning.py` conforming to the existing
`reason(role, problem, context) -> RawAgentOutput` signature, selected
in `agents/base.py` when an API key is present (see
[docs/agents.md](../docs/agents.md#reasoning-engine)). This is the
highest-leverage next step: every other improvement (richer `evidence`,
meaningful context use by the Critic/Risk/Ethics agents, real
uncertainty estimates) depends on reasoning that isn't template-based.

**Open design question:** how agents should report `confidence` when
backed by an LLM — self-reported by the model, derived from
log-probabilities, or calibrated against something else. This needs a
decision, not just an implementation.

## 2. Promote POLIS Protocol v1 from logs-only to the live API

Once evidence-backed reasoning exists, `evidence` and `goal` become
meaningful for the frontend to display, not just the session log. This
is a deliberate, versioned API change (see
[protocol/POLIS_PROTOCOL_V1.md#versioning](../protocol/POLIS_PROTOCOL_V1.md#versioning)),
requiring a corresponding `frontend/lib/types.ts` update and new UI
treatment for `evidence` — not an implicit or silent migration.

## 3. Episodic memory

Retrieval over past session logs so the council can reference prior
similar deliberations (see [architecture/memory.md](../architecture/memory.md)
for the full design sketch: embedding-based retrieval, a relevance
policy, and injection into the existing `context` mechanism). Gated on
having enough real session volume to make retrieval meaningful, and on
a real reasoning backend that can actually make use of injected
historical context.

## 4. Dynamic council composition

Today's pipeline is fixed for every problem. A natural next step is
letting the orchestrator select which roles are relevant to a given
problem (e.g., skip Ethics for a purely technical infrastructure
question) — see [architecture/scalability.md](../architecture/scalability.md#council-structure-fixed---dynamic).
This requires a routing decision the current system has no basis for
making without a real reasoning backend in place first.

## 5. Evaluation

No benchmark, user study, or comparison against single-model baselines
has been performed (see [abstract.md](abstract.md#scope-of-claims)).
Once a real reasoning backend exists, a natural evaluation would
compare decision quality, calibration, and user trust between a single-
model answer and a full council deliberation on the same problem set —
this is future work, not a claim made anywhere in this codebase today.

## Explicitly out of scope for now

- Paid API integration beyond an optional user-provided key (no bundled
  or required paid service).
- LangGraph or any heavyweight agent-orchestration framework — the
  current fixed pipeline is intentionally simple; adopting one is a
  decision to revisit only if council structure actually becomes
  dynamic (see item 4), not preemptively.
- Any production deployment hardening beyond what's already noted in
  [docs/deployment.md](../docs/deployment.md#production-considerations-not-yet-implemented).
