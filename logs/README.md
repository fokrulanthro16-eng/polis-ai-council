# logs/

Every successful call to `POST /api/council/deliberate` writes one
session record here, named `session_<UTC timestamp>_<id>.json`.

Each file is a single JSON object:

```json
{
  "session_id": "a1b2c3d4",
  "protocol_version": "1.0",
  "timestamp": "2026-07-06T14:32:03Z",
  "problem": "...",
  "agents": [ /* POLIS Protocol v1 messages, see protocol/POLIS_PROTOCOL_V1.md */ ],
  "timeline": [ /* DebateTimelineEntry objects */ ],
  "consensus": { /* ConsensusSummary */ }
}
```

Written by `backend/app/utils/session_logger.py`. See
[docs/deployment.md](../docs/deployment.md#logging) for behavior and
[architecture/memory.md](../architecture/memory.md) for how these logs
relate to (currently nonexistent) cross-session memory.

Session files themselves are git-ignored (see `.gitignore`) — they are
runtime output, not source, and may contain user-submitted problem
text.
