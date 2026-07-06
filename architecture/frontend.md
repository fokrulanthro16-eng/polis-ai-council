# Frontend Layers

Next.js 14 (App Router) + React 18 + TypeScript. No CSS framework, no
state management library, no test framework — deliberately minimal for
an MVP whose complexity lives in the backend.

```
frontend/
  app/            Pages (App Router): layout.tsx, page.tsx, globals.css
  components/     Presentational components, one per UI region
  lib/            API client, shared types, cosmetic role-color map
```

## `app/`

`page.tsx` is the only page and the only stateful component (`"use
client"`). It owns `result` / `loading` / `error` state, calls
`deliberate()` on submit, and renders the three result views once a
response arrives. `layout.tsx` sets page metadata. `globals.css` holds
all styling — there is no CSS-in-JS or utility framework to configure.

## `components/`

Each component is a pure function of props — no component fetches data
or holds request state itself:

- **`ProblemInput`** — textarea + submit button (also Cmd/Ctrl+Enter).
- **`AgentCard`** — renders one `AgentResult`: role, confidence badge,
  analysis, recommendation, objections.
- **`DebateTimeline`** — renders the ordered `DebateTimelineEntry[]`.
- **`ConsensusPanel`** — renders `ConsensusSummary`: agreement badge,
  final recommendation, confidence bar, risks, dissenting roles.

Because these are pure rendering components over the exact shapes
`services/council.py` returns, adding a new field to the backend
response is visible in the UI only where you choose to render it — no
component needs to change just because the API grew a field.

## `lib/`

- **`api.ts`** — `deliberate(problem)`: the single `fetch` call in the
  app, posting to `POST /api/council/deliberate`.
- **`types.ts`** — TypeScript interfaces mirroring
  `backend/app/models/schemas.py` exactly. This is a manually
  maintained mirror, not generated — see
  [docs/api.md](../docs/api.md#source-of-truth) for the sync
  obligation when the backend contract changes.
- **`roleColors.ts`** — a `role -> color` map used purely for visual
  distinction between agent cards; carries no business logic.

## Why so little abstraction

There is exactly one page, one API call, and four presentational
components. Introducing a state management library, a data-fetching
library, or a component library ahead of an actual need would be
premature for an app this size — see
[architecture/scalability.md](scalability.md) for what would justify
adding one (e.g. multiple pages, client-side caching across
deliberations, or real-time streaming of agent output as it's
produced).
