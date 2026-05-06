# Connector: File Watcher

**Status:** Concept  
**Stage:** 1  
**Permission required:** `files:watch:<path>`

---

## What It Is

The file watcher connector uses Linux inotify to observe file changes in approved project directories, tracking which files are being actively worked on.

---

## Why It Matters

File activity is a strong signal for:
- Which project is currently active
- Which part of the codebase is being worked on
- How long the user spent on a feature
- When a session started and ended

---

## What It Watches

Only user-approved directories. No defaults.

```bash
stareha permissions add files ~/projects/agent-os
stareha permissions add files ~/projects/stareha
```

---

## Events Generated

| Event | When | Data |
|-------|------|------|
| `file_edited` | File save (inotify IN_CLOSE_WRITE) | path, project, extension |
| `session_detected` | First file edit after idle | project, start time |
| `session_ended` | 30+ min of no file activity | project, end time, duration |
| `file_pattern` | Same file edited 5+ times in a session | path, edit count |

---

## What Is Tracked

| Tracked | Not tracked |
|---------|------------|
| File path relative to project | Full file contents |
| File extension (language) | Diffs or changes |
| Edit count | Line numbers |
| Session start/end | Private files outside watched paths |

---

## Project Detection

When a file is edited, project is detected by:
1. Walking up directory tree to find `.git`
2. Checking `package.json` / `pyproject.toml` presence
3. Matching against user-configured project paths

---

## Example Events

```json
{
  "type": "session_detected",
  "source": "file_watcher",
  "project": "agent-os",
  "project_path": "~/projects/agent-os",
  "start_at": 1746700000,
  "files_touched": ["packages/core/src/memory.ts", "packages/cli/src/index.ts"]
}
```

---

## Example Memories Generated

```
AgentOS Continuum uses a TypeScript monorepo. Most activity is in packages/core and packages/cli.
Source: file_watcher | Evidence: 23 sessions | Confidence: 0.92
```

---

## Related Files
- [Connectors Overview](README.md)
- [Project Memory](../../02-workflow-memory/project-memory.md)
- [Daemon & Runtime](../../07-daemon-runtime/README.md)
