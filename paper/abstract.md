# Abstract

**POLIS: A Transparent Multi-Agent Architecture for Collective Decision
Support**

POLIS is a reference architecture for **Artificial Collective
Intelligence (ACI)** — a class of systems that produce a decision or
recommendation not from a single model's undifferentiated output, but
from a structured deliberation among multiple specialized reasoning
roles, each accountable for a distinct angle on the problem (factual
grounding, planning, critique, risk, ethics), converging on a consensus
that preserves rather than discards disagreement.

The core contribution of the present system is architectural, not
empirical: a fixed, ordered pipeline in which each role observes the
output of every role that preceded it; a deterministic, auditable
consensus-aggregation step (mean confidence, an objection-weighted
penalty, and explicit dissent tracking) in place of an opaque
synthesis step; and a versioned inter-agent communication format
([POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md)) that decouples
*what an agent must communicate* from *how its reasoning is produced*,
so that a deterministic template engine and a future LLM-backed
reasoner are interchangeable behind the same contract.

The current implementation ships with a fully deterministic, offline
reasoning engine rather than a large language model, by design: it lets
the architecture, the consensus mechanism, and the protocol be
exercised, demonstrated, and reasoned about independently of any
specific model's behavior or cost. This is explicitly a **systems and
architecture contribution**, not a claim of validated decision-quality
improvement over single-model baselines — no user study, benchmark, or
comparative evaluation has been performed. Those are named directly as
future work in [future-work.md](future-work.md).

## Scope of claims

This paper describes what POLIS *is* (an architecture and a protocol
for transparent multi-agent deliberation) and what it is *not yet*
(a validated method, a production system, or a system backed by a real
language model). Readers should treat every claim in
[innovation.md](innovation.md) as a description of a design choice and
its rationale, not as an empirical result.
