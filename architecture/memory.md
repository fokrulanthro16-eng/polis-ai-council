# Memory Flow

**Honest baseline: POLIS has no cross-session memory today.** This
document describes exactly what state exists now, and separately, what
a future memory system would add. See
[design/memory-flow.md](../design/memory-flow.md) for the diagram.

## What exists today

### 1. Working memory (in-process, per-request)

The `context: List[Dict]` list built up inside `run_council()` — the
growing list of prior agents' `AgentResult`s within a *single*
deliberation. It is created fresh on every call and discarded once the
HTTP response is sent. Nothing about it survives past one request.

### 2. Session logs (on disk, write-only from the app's perspective)

As of this upgrade, every deliberation is written to `logs/` as a
[POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md)-formatted JSON
file (see `backend/app/utils/session_logger.py`). This is real,
persistent state — but the application never reads it back. It exists
for human audit and as a substrate for future work, not as functioning
memory yet.

## What memory would mean going forward

A genuine memory system would let the council draw on *past*
deliberations when reasoning about a *new* one — e.g., "we've seen a
similar layoff-decision problem before; here's what the Risk Agent
flagged then." That requires, roughly:

1. **An episodic store** — session logs indexed for retrieval (e.g. by
   embedding similarity over the `problem` field, since that's the only
   free-text field guaranteed present at the start of any deliberation).
2. **A retrieval step** in `run_council()`, before the pipeline runs,
   that fetches relevant past sessions and passes them into agents as
   additional context (extending, not replacing, the existing
   `context` list mechanism).
3. **A decision about what "relevant" means** — this is a design
   question, not just an engineering one (temporal recency? topical
   similarity? agreement/disagreement with the current problem?).

None of this is implemented. It is deliberately scoped as future work —
see [paper/future-work.md](../paper/future-work.md) — rather than
attempted prematurely: retrieval quality, embedding infrastructure, and
staleness handling are all real problems that deserve their own design
pass, not a bolt-on.

## Why the protocol adoption matters here

Session logs are written in Protocol v1 format specifically so that,
when a memory store is eventually built, it has a consistent, versioned
input format to work from instead of needing to parse or normalize
whatever ad hoc shape the logs happened to be in. This is the concrete
link between [protocol/POLIS_PROTOCOL_V1.md](../protocol/POLIS_PROTOCOL_V1.md)
and future memory work.
