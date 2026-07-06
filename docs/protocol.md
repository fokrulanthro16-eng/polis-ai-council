# Protocol (Overview)

POLIS defines a standard message shape that every agent's output
conforms to, independent of what powers its reasoning (mock templates
today, an LLM tomorrow). The full field-by-field specification lives in
[protocol/POLIS_PROTOCOL_V1.md](../protocol/POLIS_PROTOCOL_V1.md) — this
page is a short orientation.

## Why a protocol at all

Once more than one thing can produce an agent's output (mock engine,
different LLMs, future specialized models per role), every consumer of
that output — the orchestrator, the frontend, the session log, a future
memory store — needs one shape to agree on. The protocol is that shape.
It also matters for audit and trust: a fixed, documented schema is what
lets someone other than the author of the code inspect *why* the
council reached a recommendation.

## Two things you'll see in this codebase today

1. **The live API contract** — `AgentResult` in
   `backend/app/models/schemas.py`, returned by
   `POST /api/council/deliberate`. This is intentionally small and
   stable; the frontend depends on it and it does not change as part of
   this protocol work. See [docs/api.md](api.md).
2. **POLIS Protocol v1** — a superset message shape (adds `agent`,
   `goal`, `evidence`, and `timestamp` to the same core fields) intended
   as the standard for *all* inter-agent and agent-to-log communication
   going forward. It is already in real use: every session log written
   to `logs/` (see [docs/deployment.md](deployment.md#logging)) is a
   sequence of Protocol v1 messages, built by
   `backend/app/utils/protocol.py`.

The relationship is intentionally conservative: adopting the richer
protocol for internal records first, before ever changing the public
API, means the upgrade carries no risk of breaking the frontend or any
existing integration.

## What changes if/when Protocol v1 becomes the live API

`evidence` (currently always empty — the mock engine doesn't source real
evidence) becomes populated once a real reasoning engine can cite
sources. `goal` and `timestamp` are already meaningful today. Migrating
the public API to Protocol v1 is a deliberate, versioned decision — see
[paper/future-work.md](../paper/future-work.md) — not something that
happens implicitly.
