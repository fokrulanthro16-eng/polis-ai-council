# POLIS Protocol v1

Status: **Draft, v1.0.** Adopted today for session logging
(`logs/session_*.json`, via `backend/app/utils/protocol.py`). Not yet
the live HTTP API contract — see [Relationship to the live API](#relationship-to-the-live-api).

## Purpose

Every agent in POLIS — regardless of whether it's a template-based mock
reasoner or a real LLM call — must communicate in one standard shape.
This document defines that shape: **POLIS Protocol v1**.

A protocol matters here for the same reason it matters in any
multi-party system: the orchestrator, the consensus calculator, the
session log, and (eventually) a memory store all need to agree on what
an agent's output *is*, independent of how it was produced. Standardizing
it now — while there's only one reasoning engine — means adding a
second one (a real LLM, or a per-role specialized model) is additive,
not a breaking migration.

## Message schema

```json
{
  "agent": "",
  "goal": "",
  "analysis": "",
  "evidence": [],
  "confidence": 0.0,
  "objections": [],
  "recommendation": "",
  "timestamp": ""
}
```

## Field reference

| Field | Type | Required | Description |
|---|---|---|---|
| `agent` | string | yes | The speaking agent's role name, e.g. `"Risk Agent"`. Must match one of the registered council roles (see [docs/agents.md](../docs/agents.md)). |
| `goal` | string | yes | A fixed, one-sentence statement of this agent's mandate — *what it exists to evaluate*, independent of the specific problem. E.g. for the Risk Agent: `"Quantify downside exposure and propose contingencies."` Constant per role; lets a reader interpret `analysis` without needing to already know what a "Risk Agent" is. |
| `analysis` | string | yes | The agent's free-text reasoning about the specific problem. This is the substantive content. |
| `evidence` | array of strings | yes | Concrete facts, citations, or data points the analysis relies on. May be an empty array when the reasoning engine has no way to ground its output in real sources (this is the honest current state of the mock engine — see [Evidence today](#evidence-today)). Never fabricated to look non-empty. |
| `confidence` | number | yes | The agent's self-assessed confidence in its `recommendation`, in `[0.0, 1.0]`. |
| `objections` | array of strings | yes | Concerns, caveats, or pushback the agent raises — either about the problem itself or about a prior agent's reasoning. May be empty. |
| `recommendation` | string | yes | The agent's concrete, actionable suggestion given its `analysis`. |
| `timestamp` | string | yes | ISO-8601 UTC timestamp (e.g. `"2026-07-06T14:32:01Z"`) of when this message was produced. |

## Validation rules

1. `confidence` must satisfy `0.0 <= confidence <= 1.0`.
2. `agent`, `goal`, `analysis`, and `recommendation` must be non-empty
   strings (an agent that has nothing to say should not be in the
   pipeline for that turn).
3. `evidence` and `objections` are arrays; empty arrays are valid and
   expected for `evidence` under the current mock reasoning engine.
4. `timestamp` must be a valid ISO-8601 string in UTC.

A JSON Schema encoding of these rules is provided in
[`schema.json`](schema.json) for programmatic validation.

## Example messages

**A debating agent (Risk Agent):**

```json
{
  "agent": "Risk Agent",
  "goal": "Quantify downside exposure and propose contingencies.",
  "analysis": "Assessing downside exposure for \"Should we lay off 20% of staff?\", with particular attention to personnel impact. Worst-case impact appears moderate rather than catastrophic, but the probability of at least one assumption failing is non-trivial.",
  "evidence": [],
  "confidence": 0.62,
  "objections": ["Insufficient contingency plan for personnel impact if the primary approach underperforms."],
  "recommendation": "Define a specific contingency plan for personnel impact before proceeding, and set a review checkpoint.",
  "timestamp": "2026-07-06T14:32:01Z"
}
```

**The synthesizing agent (Consensus Agent):** `confidence` and
`recommendation` are the orchestrator-computed council-wide values, not
independently generated (see `ConsensusAgent.synthesize()` in
`backend/app/agents/consensus_agent.py`).

```json
{
  "agent": "Consensus Agent",
  "goal": "Synthesize every agent's confidence and objections into one final recommendation.",
  "analysis": "Synthesizing the council's perspectives into a single actionable recommendation, weighing each agent's confidence and objections rather than simply averaging opinions.",
  "evidence": [],
  "confidence": 0.64,
  "objections": [],
  "recommendation": "Adopt a phased rollout with a clear go/no-go checkpoint after the first phase. Caveat: Insufficient contingency plan for personnel impact if the primary approach underperforms.",
  "timestamp": "2026-07-06T14:32:03Z"
}
```

## Relationship to the live API

`POST /api/council/deliberate` returns `AgentResult` objects
(`backend/app/models/schemas.py`) — a **stable subset** of this
protocol: `role` (≈ `agent`), `analysis`, `confidence`, `objections`,
`recommendation`. It intentionally omits `goal`, `evidence`, and
`timestamp` today, so this specification does not change the frontend
contract or require any client update.

Every session log entry, however, is written using the **full** Protocol
v1 shape (see `backend/app/utils/protocol.py`). This means the protocol
is not merely a paper design — it is already the format real session
data is recorded in, which is the intended path to eventually promoting
it to the live API (see [docs/protocol.md](../docs/protocol.md) and
[paper/future-work.md](../paper/future-work.md)).

## Evidence today

`evidence` is defined now so the schema doesn't need a breaking change
later, but the current mock reasoning engine has no mechanism for
sourcing real citations — it always emits `[]`. This is a deliberate,
honest choice: an empty array is preferable to a plausible-sounding but
fabricated citation. Populating `evidence` meaningfully is gated on a
real reasoning backend (see [docs/agents.md](../docs/agents.md#reasoning-engine)).

## Versioning

This is v1. Backward-incompatible changes (renaming or removing a
required field, changing a type) require a v2 document and an explicit
migration note in [paper/future-work.md](../paper/future-work.md) —
never a silent change to this file.
