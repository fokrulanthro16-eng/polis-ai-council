# API Reference

Base URL: `http://localhost:8000` (default; override via
`NEXT_PUBLIC_API_URL` on the frontend and `POLIS_ALLOWED_ORIGINS` on the
backend for CORS).

## `GET /`

Liveness check.

```json
{ "service": "polis-backend", "status": "ok" }
```

## `GET /api/health`

Health check used by orchestration/monitoring.

```json
{ "status": "healthy" }
```

## `POST /api/council/deliberate`

Runs the full council on a problem statement and returns the per-agent
breakdown, debate timeline, and consensus.

### Request

```json
{ "problem": "Should our startup lay off 20% of staff to cut costs before the next funding round?" }
```

| Field | Type | Constraints |
|---|---|---|
| `problem` | string | min length 3 |

### Response — `200 OK`

```json
{
  "problem": "Should our startup lay off 20% of staff ...",
  "agents": [
    {
      "role": "Research Agent",
      "analysis": "...",
      "confidence": 0.71,
      "objections": ["..."],
      "recommendation": "..."
    }
  ],
  "timeline": [
    {
      "step": 1,
      "role": "Research Agent",
      "message": "...",
      "responding_to": null
    }
  ],
  "consensus": {
    "final_recommendation": "...",
    "overall_confidence": 0.64,
    "agreement_level": "Moderate Consensus",
    "key_risks": ["..."],
    "key_objections": ["..."],
    "dissenting_roles": ["Critic Agent"],
    "explanation": {
      "supporting_arguments": ["..."],
      "main_objections": ["..."],
      "reasoning": "4 of 5 agents supported the lead recommendation ..."
    }
  },
  "metrics": {
    "council_confidence": 0.63,
    "agreement_score": 0.69,
    "risk_level": "Medium",
    "evidence_quality": "Medium"
  },
  "timestamp": "2026-07-06T14:36:00Z",
  "protocol_version": "1.0"
}
```

### Response schema

| Type | Field | Notes |
|---|---|---|
| `DeliberateResponse` | `problem` | Echoes the request. |
| | `agents` | `AgentResult[]` — one entry per council member, in speaking order, including Consensus. |
| | `timeline` | `DebateTimelineEntry[]` — ordered, human-readable debate log. |
| | `consensus` | `ConsensusSummary` — aggregated final answer. |
| | `metrics` | `CouncilMetrics` — compact, heuristic council-level indicators. |
| | `timestamp` | ISO-8601 UTC timestamp (`YYYY-MM-DDTHH:MM:SSZ`) for this deliberation; also the value used for the session log written to `logs/`. |
| | `protocol_version` | The [POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) version this session was logged under, e.g. `"1.0"`. |
| `AgentResult` | `role` | Agent name, e.g. `"Risk Agent"`. |
| | `analysis` | Free-text reasoning. May explicitly reference another agent by name (e.g. "The Critic raises an important point..."), so the debate reads as a discussion rather than isolated statements. |
| | `confidence` | Float, `0.0`–`1.0`. |
| | `objections` | List of strings; may be empty. |
| | `recommendation` | Free-text recommendation. |
| `DebateTimelineEntry` | `step` | 1-indexed position in the timeline. |
| | `role` | Speaking agent for this step. |
| | `message` | Condensed recommendation (+ objection count). |
| | `responding_to` | Role of the previous speaker, or `null` for the first entry. |
| `ConsensusSummary` | `final_recommendation` | Lead agent's recommendation with top objections folded in as caveats. |
| | `overall_confidence` | Float, `0.0`–`1.0`; mean confidence penalized per objection. |
| | `agreement_level` | `"Strong Consensus"` / `"Moderate Consensus"` / `"Weak Consensus"` / `"Highly Contested"` — derived from a weighted `agreement_score` (confidence + agent support ratio + objection density), not confidence alone. See `services/council.py::_agreement_signals`. |
| | `key_risks` | Objections raised specifically by the Risk Agent. |
| | `key_objections` | All objections, from every agent. |
| | `dissenting_roles` | Agents whose confidence is well below the group average. |
| | `explanation` | `ConsensusExplanation` — powers the Consensus Panel's "Why this decision?" section. |
| `ConsensusExplanation` | `supporting_arguments` | Up to 3 recommendations from non-dissenting agents, highest confidence first. |
| | `main_objections` | Up to 3 objections, from `key_objections`. |
| | `reasoning` | One-sentence narrative explaining how the agreement tier was reached. |
| `CouncilMetrics` | `council_confidence` | Float, `0.0`–`1.0`; raw mean of all debating agents' confidence (pre-objection-penalty). |
| | `agreement_score` | Float, `0.0`–`1.0`; the same composite score used to pick `agreement_level`. |
| | `risk_level` | `"Low"` / `"Medium"` / `"High"` — heuristic proxy from the Risk Agent's own confidence/objections, not a measured quantity. |
| | `evidence_quality` | `"Low"` / `"Medium"` / `"High"` — heuristic proxy from the Research Agent's own confidence/objections, not a measured quantity (see [docs/protocol.md](protocol.md#evidence-today)). |

### Errors

Validation errors (e.g. `problem` shorter than 3 characters) return
FastAPI's standard `422 Unprocessable Entity` with a `detail` array
describing the failing field.

## Source of truth

These schemas are defined once in
`backend/app/models/schemas.py` and mirrored (kept manually in sync) in
`frontend/lib/types.ts`. If you add or rename a field, update both.

## Side effects

Every successful call to `/api/council/deliberate` also writes a
[POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) session record to
`logs/` (see [docs/deployment.md](deployment.md#logging)). This does
not appear in the HTTP response and failures to write it do not fail
the request.
