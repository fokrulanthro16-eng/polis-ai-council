# Deployment

## Local development

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux

uvicorn app.main:app --reload --port 8000
```

Verify with `curl http://localhost:8000/api/health`.

### Frontend

```bash
cd frontend
npm install
copy .env.example .env.local  # Windows
# cp .env.example .env.local  # macOS/Linux

npm run dev
```

Open `http://localhost:3000`.

## Docker Compose

```bash
docker compose up --build
```

This builds and runs both services from `docker-compose.yml`: backend on
`:8000`, frontend on `:3000`, wired together via `NEXT_PUBLIC_API_URL`
(build arg) and `POLIS_ALLOWED_ORIGINS` (runtime env var). No database
or cache service is defined — the MVP is stateless aside from the
`logs/` directory written by the backend container's filesystem.

## Environment variables

| Variable | Where | Default | Purpose |
|---|---|---|---|
| `POLIS_ALLOWED_ORIGINS` | backend | `http://localhost:3000` | Comma-separated CORS allow-list. |
| `POLIS_LLM_PROVIDER` | backend | unset | `anthropic` \| `openai` \| `gemini`. Unset (default) uses the mock reasoning engine. See [docs/agents.md](agents.md#reasoning-engine). |
| `ANTHROPIC_API_KEY` | backend | unset | Required when `POLIS_LLM_PROVIDER=anthropic`. |
| `POLIS_ANTHROPIC_MODEL` | backend | `claude-sonnet-5` | Model override for the Anthropic provider. |
| `OPENAI_API_KEY` | backend | unset | Required when `POLIS_LLM_PROVIDER=openai`. |
| `POLIS_OPENAI_MODEL` | backend | `gpt-4o-mini` | Model override for the OpenAI provider. |
| `GEMINI_API_KEY` | backend | unset | Required when `POLIS_LLM_PROVIDER=gemini`. |
| `POLIS_GEMINI_MODEL` | backend | `gemini-2.0-flash` | Model override for the Gemini provider. |
| `NEXT_PUBLIC_API_URL` | frontend | `http://localhost:8000` | Where the frontend sends deliberation requests. |

## Logging

Every `POST /api/council/deliberate` call writes one session record to
`logs/` as `session_<UTC timestamp>_<short id>.json`, containing the
original prompt, every agent's output in
[POLIS Protocol v1](../protocol/POLIS_PROTOCOL_V1.md) format, the
debate timeline, the consensus, and an ISO-8601 timestamp. This is
local-filesystem logging suitable for development and demos; log
writing is best-effort and never fails the HTTP request (see
`backend/app/utils/session_logger.py`). Session files are excluded from
version control (see `.gitignore`) since they're runtime output, not
source.

For anything beyond local development, treat `logs/` as a starting
point, not a production logging solution — see
[architecture/scalability.md](../architecture/scalability.md) for what
changes at scale (structured log shipping, retention policy, PII
handling for user-submitted problem text).

## Production considerations (not yet implemented)

The MVP is designed to run locally or in two containers behind a
reverse proxy you provide. Before deploying it somewhere with real
traffic, you would need to add — none of this exists today, and this
list is intentionally scoped as roadmap, not a claim about the current
system:

- Rate limiting / abuse protection on `/api/council/deliberate`.
- Structured, shipped logging instead of local JSON files.
- Secrets management for any LLM API key (never commit `.env`).
- Horizontal scaling of the backend (the service is stateless per
  request today, so this is straightforward once logging moves off the
  local filesystem — see [architecture/scalability.md](../architecture/scalability.md)).
- HTTPS termination and a real allow-list for `POLIS_ALLOWED_ORIGINS`.
