# POLIS — Vision

## The problem with asking one model

When you ask a single AI model a hard question, you get one voice, one
angle, and one implicit set of priorities — even when the model is
capable of reasoning about the problem from many angles internally, its
answer collapses all of that into a single, undifferentiated response.
For decisions that matter (a layoff, a product launch, a pricing change,
a security tradeoff), that collapse hides exactly the information a
careful decision-maker needs most: *which considerations were weighed,
how confident is the model in each one, and where do reasonable
perspectives disagree?*

Human institutions solve this with committees, boards, and review
processes — not because groups are always right, but because structured
disagreement surfaces blind spots that a single reasoner, human or
artificial, tends to miss.

## What POLIS is

POLIS is an **Artificial Collective Intelligence (ACI) platform**: instead
of one model answering a question, a **council of specialized agents**
—Research, Planner, Critic, Risk, Ethics, and Consensus — each analyze the
same problem from their own mandate, see what the agents before them
said, and are free to object. The result is a transparent deliberation:
a debate timeline, per-agent confidence scores and objections, and a
final consensus that explicitly folds in disagreement rather than
hiding it.

The council's output is not "the AI's answer." It is a structured,
auditable record of *how* an answer was reached.

## Principles

1. **Transparency over authority.** Every agent's analysis, confidence,
   and objections are shown, not just the final recommendation. Users
   should never have to trust a black box.
2. **Disagreement is signal, not noise.** A council where every agent
   agrees is either a simple problem or an under-specified one. Dissent
   is surfaced and preserved in the consensus summary rather than
   averaged away.
3. **Explainability is structural, not cosmetic.** Explainability comes
   from the architecture (an ordered pipeline of accountable roles, a
   shared communication protocol, a logged session record) rather than
   from a post-hoc summary prompt.
4. **Runs without a paid API.** The reference reasoning engine is fully
   deterministic and local, so anyone can run the whole council for free
   and reproduce the same output for the same problem. A real LLM can be
   dropped in later behind the same interface — see
   [docs/agents.md](agents.md) and [docs/protocol.md](protocol.md).
5. **Honest about maturity.** POLIS today is a working MVP with a mock
   reasoning engine, not a validated decision-support product. Claims
   about its capabilities are scoped accordingly — see
   [paper/abstract.md](../paper/abstract.md) and
   [paper/future-work.md](../paper/future-work.md).

## Who it's for

- Builders who want a reference architecture for transparent multi-agent
  reasoning, rather than a single opaque prompt-and-response loop.
- Teams evaluating whether structured, multi-perspective AI deliberation
  is useful for their own decision workflows before investing in a
  production LLM integration.
- Researchers and hobbyists exploring collective intelligence patterns
  in artificial systems.

## Where this is going

The MVP proves the deliberation pattern end-to-end with a mock reasoning
engine. The near-term roadmap (see
[paper/future-work.md](../paper/future-work.md)) is: (1) a real LLM
reasoning backend behind the existing `reason()` interface, (2) a formal
inter-agent communication protocol (see
[protocol/POLIS_PROTOCOL_V1.md](../protocol/POLIS_PROTOCOL_V1.md)),
already adopted for session logging, and (3) persistent memory across
sessions so the council can learn from past deliberations — see
[architecture/memory.md](../architecture/memory.md).
