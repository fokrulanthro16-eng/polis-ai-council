# Diagram: Memory Flow

POLIS today has **no cross-session memory** — every deliberation is
stateless. This diagram shows what actually persists today (working
context + session logs) versus what's planned. See
[architecture/memory.md](../architecture/memory.md) for the full
discussion and [paper/future-work.md](../paper/future-work.md) for the
roadmap.

```mermaid
flowchart TB
    subgraph Today["Today — implemented"]
        direction TB
        WM["Working memory\n(in-process, one request)\ncontext: List[AgentResult dict]\nlives only for the duration\nof run_council()"]
        SL["Session log\n(logs/session_*.json)\nPOLIS Protocol v1 messages,\nwritten after each request,\nnever read back by the app"]
        WM -. discarded after response .-> X1(( ))
        SL -. append-only, on disk .-> X2(( ))
    end

    subgraph Future["Future — roadmap, not implemented"]
        direction TB
        EM["Episodic memory store\n(e.g. embeddings + vector search\nover past session logs)"]
        RC["Retrieval at deliberation time:\nagents can be given relevant\npast sessions as extra context"]
        Learn["Longitudinal patterns:\nrecurring objections, confidence\ndrift, agent calibration over time"]
        EM --> RC --> Learn
    end

    SL -.->|"would become the input corpus for"| EM
```

## Notes

- The only thing that persists between two different problems today is
  the **code** (agent order, reasoning templates) — never the content of
  a prior deliberation.
- The session log (`logs/`) is written for **audit and observability**,
  not consumed by the app itself. It is the natural raw material for a
  future memory store, which is why it's already structured as
  [POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) messages rather
  than an ad hoc dump.
- Do not read "Future" as implemented — it is intentionally drawn as a
  separate, dashed-line subgraph to avoid overstating current
  capability. See [paper/abstract.md](../paper/abstract.md) for the
  same scoping in prose.
