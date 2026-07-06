# Future Scalability

The MVP is intentionally simple: one fixed pipeline, one mock reasoning
engine, local JSON logs, two containers. This document is a scoped list
of what would need to change to scale each dimension — not a
commitment or a claim that any of it is built.

## Reasoning engine: mock -> real LLM

The seam already exists (`reason(role, problem, context)` — see
[docs/agents.md](../docs/agents.md#reasoning-engine)). Scaling
considerations once a real LLM is behind it:

- **Latency**: five to six sequential model calls per deliberation add
  up. Consider parallelizing agents that don't need each other's output
  (Research and an initial pass of Planner could run concurrently),
  reserving strict sequencing for agents that must react to prior
  output (Critic, Risk, Ethics).
- **Cost**: per-deliberation cost becomes non-zero; would need
  request-level cost tracking and a rate limit in front of
  `/api/council/deliberate`.
- **Failure handling**: a real API call can time out or error in ways a
  local template function cannot. The orchestrator would need a defined
  behavior for a failed agent turn (skip with a flagged `AgentResult`?
  retry? fail the whole deliberation?) — an explicit design decision,
  not an afterthought.

## Council structure: fixed -> dynamic

Today's `_PIPELINE` is a static list. A more capable council might:

- Allow agents to speak more than once (true multi-round debate rather
  than one pass).
- Let the orchestrator decide which agents are relevant to a given
  problem (e.g., skip the Ethics Agent for a purely technical
  migration question) — this requires a routing decision the mock
  engine has no basis for making today.
- Run independent agents in parallel where their outputs don't depend
  on each other, changing `run_council()` from strictly sequential to a
  small dependency graph.

## Logging: local files -> structured, shipped logs

`logs/session_*.json` (see [docs/deployment.md](../docs/deployment.md#logging))
is adequate for local development and demos, not for a deployed
service:

- Ship logs to a log aggregation service rather than writing to local
  disk (containers are ephemeral; local files disappear on redeploy).
- Define a retention policy — session logs contain user-submitted
  problem text, which may be sensitive.
- Consider whether session logs need to be queryable (a database or log
  index) rather than one-file-per-session, once volume makes
  `ls logs/` an impractical way to find anything.

## Memory: none -> episodic retrieval

Covered in depth in [architecture/memory.md](memory.md). At scale, this
also means: an actual vector index (not a linear scan over JSON files),
a decision about embedding model and cost, and a policy for how much
past context to inject before it degrades rather than improves a new
deliberation.

## Deployment: two containers -> real infrastructure

`docker-compose.yml` is a local/dev convenience, not a production
topology. Moving beyond it means: horizontal scaling of the backend
(straightforward, since a single request is stateless once logging
moves off local disk), a managed database if/when memory is added, and
standard production concerns (HTTPS termination, secrets management,
health-check-based orchestration) noted in
[docs/deployment.md](../docs/deployment.md#production-considerations-not-yet-implemented).

## What this document is not

This is a list of considerations, not a roadmap with dates or
commitments. See [paper/future-work.md](../paper/future-work.md) for
the prioritized version of this list.
