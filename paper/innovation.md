# Innovation

What is actually novel about POLIS's design, scoped honestly against
what already exists elsewhere.

## 1. Disagreement as a first-class, preserved artifact

Most multi-agent or "mixture of experts" patterns either pick a winner
or blend outputs into a single averaged answer, discarding the
information contained in *where* the experts disagreed. POLIS's
consensus step (`build_consensus()` in
`backend/app/services/council.py`) instead:

- Tracks which specific agents dissent (`dissenting_roles`), not just
  an aggregate score.
- Folds objections into the final recommendation as explicit caveats,
  rather than silently averaging them away.
- Lowers `overall_confidence` as a direct function of how many
  objections were raised — disagreement measurably reduces the
  system's own stated confidence, rather than being cosmetic.

This is a small mechanism, but it is the architectural core of what
"transparent consensus" means in this system — see
[design/consensus-flow.md](../design/consensus-flow.md).

## 2. A protocol, not just a shared function signature

Many multi-agent demos get away with an implicit shared dict shape
because there's only one implementation of "an agent." POLIS separates
this into an explicit, versioned specification —
[POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) — with a field-by-
field reference, a JSON Schema, and validation rules, adopted *in
practice* for session logging before it's ever load-bearing for the
live API. The goal is that adding a second reasoning implementation (a
real LLM, or per-role specialized models) is a matter of conforming to
a documented contract, not reverse-engineering the current one from
code.

## 3. Deliberately deterministic before deliberately intelligent

The reference reasoning engine (`mock_reasoning.py`) is not a
placeholder apologized for — it's a design choice that lets the
*architecture* (pipeline order, context threading, consensus math,
protocol conformance) be demonstrated, tested, and reasoned about
independently of any LLM's cost, latency, or nondeterminism. A
SHA-256-seeded RNG means the same problem text always produces the same
council output, which is what makes the system's behavior legible and
reproducible during development — an underrated property once real
model calls (with their inherent variance) enter the picture.

## 4. Accountable roles over generic "agents"

Each council member has a fixed, named mandate (Research, Planner,
Critic, Risk, Ethics) rather than being an undifferentiated "agent N."
This is a small framing choice with a real consequence: a user reading
the Risk Agent's objection knows *why* that agent is the one raising
it, without needing to infer a role from generic output. The `goal`
field in [POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) makes
this mandate machine-readable, not just a naming convention.

## What is not novel here

Sequential multi-agent pipelines, role-based prompting, and
LLM-as-committee patterns are active, published areas of study
elsewhere; POLIS does not claim priority over that literature. Its
contribution is a specific, transparent, protocol-governed
implementation pattern for the deliberation-and-consensus part of that
space — see [abstract.md](abstract.md) for the explicit scope of this
claim.
