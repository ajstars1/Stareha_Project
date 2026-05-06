# Connectors — Overview

**Status:** Partially built (terminal ✅, file watcher ✅, claude_code ✅, browser ✅)  
**Stage:** 1–7 (each connector has its own stage)

---

## What Are Connectors

Connectors are the data inputs to the learning system. Each connector reads from a specific source, applies redaction, and sends structured events to the event store.

Every connector requires explicit permission before it runs.

---

## Connector Index

| Connector | File | Stage | Status | What it reads |
|-----------|------|-------|--------|--------------|
| Terminal | [terminal.md](terminal.md) | 1 | ✅ Built | Shell command history + live hook |
| File Watcher | [file-watcher.md](file-watcher.md) | 1 | ✅ Built | Project file saves via inotify |
| Claude Code | [claude-code.md](claude-code.md) | 1 | ✅ Built | `~/.claude/projects/*.jsonl` — no extension needed |
| Browser | [browser.md](browser.md) | 1 | ✅ Built | Chrome + Firefox SQLite history files — no extension needed |

---

## Connector Interface

Every connector must implement:

```typescript
interface Connector {
  name: string
  requiredPermission: string

  isAvailable(): boolean          // check if source exists/is accessible
  collect(since: Date): Event[]   // pull events since last collection
  redact(event: Event): Event     // strip sensitive content
}
```

---

## How Connectors Are Added

To add a new connector:
1. Create a new file in `connectors/` with a full report
2. Add it to this README table
3. Add it to [SITEMAP.md](../../../SITEMAP.md)
4. Add its permission scope to the permission system
5. Implement the interface in the codebase

---

## Connector Rules

- Never store raw output — always redact before storing
- Connectors run at fixed intervals or on session events, not continuously
- If a connector fails, log the error and continue — never block the system
- Connectors are independently enable/disable-able

---

## Planned Future Connectors

| Connector | Stage | What it would read |
|-----------|-------|-------------------|
| Git | 2 | Commits, branch changes, PR activity |
| Calendar | 8 | Meeting context, work blocks |
| Slack/Discord | 8 | Work communication patterns |

## IDE Memory Note

**Cursor** — does not store AI conversation history locally. Only has `argv.json` and extension metadata. Nothing readable.

**VS Code Copilot** — conversations are server-side only. No local files.

**Claude Code** — the only IDE that stores full conversation history locally (`~/.claude/projects/`). Already built.
