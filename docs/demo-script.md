# Demo Script

A ~3-minute walkthrough for presenting POLIS live. Run everything
locally first (see [README.md#installation](../README.md#installation))
and confirm both servers are up before you start talking.

## Setup checklist (before the audience is watching)

- Backend running: `http://localhost:8000/health` returns `{"status": "ok"}`.
- Frontend running: `http://localhost:3000` loads without an error banner.
- Browser window sized so the whole page is visible without scrolling
  past the hero on load.
- No `POLIS_LLM_PROVIDER` set (or deliberately set, if you're
  demonstrating the optional real-LLM path) — either way, know which
  mode you're in before you start.

## 1. Open on the hero (10s)

Land on the page and pause on the header:

> "POLIS — Collective Intelligence for Complex Decisions. Most AI gives
> you one answer. POLIS holds a council."

Point at the **Problem → Agents → Debate → Consensus → Decision**
stepper just below the hero — this is the shape of every run, before
you've run anything.

## 2. Pick a demo scenario (15s)

Don't type from scratch — click one of the three built-in scenario
cards. Recommended for a first run: **Healthcare Resource Allocation**
(it's concrete, high-stakes, and produces clear dissent).

> "These are three hard, real-world decisions — climate policy,
> education policy, and healthcare policy. I'll click one instead of
> typing, so you can see the actual problem statement."

The scenario text fills the input box automatically.

## 3. Run the council (5s + wait)

Click **Run Council**. While it's deliberating, narrate the stepper —
the "Agents" and "Debate" steps light up:

> "Under the hood, six agents run in a fixed order — Research, Planner,
> Critic, Risk, Ethics, then a Consensus agent — each one seeing what
> every agent before it said."

This resolves in well under a second since reasoning is local and
deterministic — don't over-explain the wait, it's not the point.

## 4. Walk the Agent Perspectives grid (45s)

Pick two or three cards, not all six:

- **Research Agent** — "grounds the problem before anyone opines."
- **Critic Agent** — point out it explicitly references the prior
  agent by name in its analysis, and read one objection aloud.
- **Risk Agent** or **Ethics Agent** — whichever produced the more
  interesting objection for the scenario you picked.

Call out the confidence bar on each card — every agent commits to a
number, not just a paragraph.

## 5. Walk the Debate Timeline (30s)

Scroll to the timeline and trace it top to bottom:

> "This is the same six outputs, but in the order they actually spoke —
> you can see the Critic responding directly to the Planner, and Risk
> and Ethics building on everything said before them."

## 6. Land on Consensus (30s)

This is the payoff — spend the most time here:

> "This is what most AI tools skip straight to: one answer. POLIS shows
> its work first. Final decision, an overall confidence score computed
> from every agent's confidence and objections — not just picked by one
> model — the top risks flagged along the way, and if any agent
> disagreed strongly enough to dissent, they're named here, not
> hidden."

If the scenario produced a dissenting agent, point it out explicitly —
it's the strongest evidence that this isn't a single opinion wearing
six hats.

## 7. Close (15s)

> "Every run here is fully local and deterministic — no API keys, no
> network calls, same problem always gives the same council output,
> which is what makes it demoable anywhere. The same reasoning seam
> swaps in a real LLM per agent with one environment variable, without
> touching the API or the frontend, when we're ready for that."

## If something goes wrong

- **Error banner appears**: the backend probably isn't running — check
  `http://localhost:8000/health` in another tab, don't debug live.
- **Blank/slow response**: reload and re-click Run Council; the mock
  engine has no external dependency to fail, so this is almost always a
  frontend/backend connection issue, not a reasoning issue.
- **Want a guaranteed-reproducible run**: reuse the exact same scenario
  card — the same problem text always produces the same council output,
  so you can rehearse the exact numbers you'll see live.
