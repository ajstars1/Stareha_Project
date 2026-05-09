# Connector: Claude Code

**Status:** Built  
**Stage:** 1  
**Permission required:** `claude_code` (advanced opt-in via `stareha init` or `stareha permissions add claude_code`; not enabled by beginner setup)

---

## What It Is

The Claude Code connector reads conversation history from Claude Code's local session files to learn what the user was building, debugging, and deciding with AI assistance.

No extension or API key required — it reads the JSONL files Claude Code stores locally.

---

## What It Reads

### Session files

Location: `~/.claude/projects/<project-dir>/*.jsonl`

Each `.jsonl` file is one Claude Code conversation. Each line is a JSON event.

Relevant event types:
- `type: "user"` with `message.role: "user"` — what the user asked Claude
- `type: "assistant"` — Claude's responses (not stored, too large)
- `type: "file-history-snapshot"` — file state at session start (not stored)

### What is extracted

Per session:
- **Project name** — derived from the directory path
- **First user message** — what was being discussed (first 200 chars, redacted)
- **Message count** — how many user turns (signals how long the session was)
- **Session timestamps** — when it started/ended

### What is NOT extracted

- Full conversation text
- Code snippets or file contents pasted into conversations
- Tool results (too large, often contains file contents)
- Assistant responses

---

## Data Location (Linux)

```
~/.claude/
  projects/
    -home-ubuntu-Developer-Ayush-my-project/
      SESSION_ID.jsonl      ← one file per conversation
      SESSION_ID.jsonl
    -home-ubuntu-Developer-Ayush-other-project/
      SESSION_ID.jsonl
  history.jsonl             ← global slash-command history
  settings.json
```

Directory names mirror the filesystem path with `-` replacing `/`.

---

## Event format stored

```json
{
  "type": "ai_session",
  "source": "claude_code",
  "content": {
    "project": "my-project",
    "first_message": "can you help me fix the auth middleware",
    "message_count": 23,
    "session_id": "3216898b-be8d-41bd-9dec-f62467be4a46",
    "dedup": "sha256..."
  }
}
```

---

## Pattern extraction

The `extract_claude_code_patterns()` extractor finds topics you repeatedly discuss with Claude:

```
"You repeatedly discussed with Claude: 'fix the auth middleware' (3 sessions)."
type: decision | source: claude_code | confidence: 0.72
```

Threshold: 2+ sessions with similar first messages before generating a candidate.

---

## Privacy

- Redaction runs on every extracted message before storage
- Full conversation content is never stored — only first message + metadata
- Session files are read-only, never modified

---

## Implementation

`src/packages/collectors/claude_code/__init__.py`

Key function: `scan_claude_code(store, since=None) -> int`

Called by the daemon on startup. Returns count of new sessions imported.
Deduplicates by `sha256(session_id)` — safe to call repeatedly.

---

## Related Files

- [Connectors Overview](README.md)
- [Claude Code Memory](../../02-workflow-memory/claude-code-memory.md)
- [Pattern Extractor](../../../src/packages/intelligence/scripts/pattern_extractor.py)
