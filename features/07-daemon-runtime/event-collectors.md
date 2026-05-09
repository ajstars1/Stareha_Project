# Event Collectors

**Status:** Concept  
**Stage:** 1

---

## What It Is

Event collectors are the daemon components that receive data from each approved source and write structured events to the event store.

---

## Collectors Overview

| Collector | Source | Permission | Stage |
|-----------|--------|-----------|-------|
| Shell hook | Terminal commands | `terminal:watch` | 1 |
| History scanner | Shell history file | `terminal:read` | 1 |
| inotify watcher | File changes | `files:watch:<path>` | 1 |
| Claude Code importer | Claude Code history | `claude_code:read` | 2 |
| Browser endpoint | Browser extension | `browser:read` | 7 |
| App usage monitor | Running processes | `app_usage:read` | 2 |

---

## Shell Hook Collector

The shell hook receives commands in real time via local HTTP.

Shell sends:
```bash
curl -s -X POST http://localhost:7431/event \
  -H "Content-Type: application/json" \
  -d '{"type":"command","cmd":"npm run build","exit":0,"pwd":"/home/ayush/projects/agent-os","ts":1746700000}'
```

Collector receives, redacts, classifies, stores.

---

## History Scanner Collector

Scans history file periodically for any commands not captured by the shell hook (e.g., sessions before Stareha was installed).

Runs:
- On `stareha start` (initial import)
- Nightly at 02:00 (catch any missed commands)
- On advanced `stareha learn` / `stareha learn --force` (manual trigger)

Deduplication: SHA256 hash of (cmd + timestamp) to avoid re-importing.

---

## inotify Watcher Collector

Uses Linux inotify to watch for file saves in approved directories.

```python
import inotify.adapters

def watch_directory(path: str):
    i = inotify.adapters.InotifyTree(path)
    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event
        if 'IN_CLOSE_WRITE' in type_names:
            emit_file_event(path, filename)
```

Only tracks: file save events, path, extension.
Never tracks: file contents.

---

## Claude Code Importer Collector

Runs on session end (triggered by `stareha done`, advanced `stareha session stop`, or idle detection).

Scans: `~/.claude/projects/*/conversations/`
Finds: sessions newer than `last_imported_at`
Extracts: decisions, tasks, bugs, project context
Stores: as `ai_session` events with full redaction

---

## Permission Gating

Before any collector runs:

```python
def can_collect(source: str, path: str = None) -> bool:
    perms = load_permissions()
    if source not in perms['sources']:
        return False
    if not perms['sources'][source].get('enabled', False):
        return False
    if path and source == 'files':
        allowed_paths = perms['sources']['files'].get('paths', [])
        return any(path.startswith(p) for p in allowed_paths)
    return True
```

If permission not granted → collector does not run. No data collected.

---

## Related Files
- [Daemon & Runtime](README.md)
- [Terminal Connector](../01-learning/connectors/terminal.md)
- [File Watcher Connector](../01-learning/connectors/file-watcher.md)
- [Claude Code Connector](../01-learning/connectors/claude-code.md)
- [Permission Flow](../../_flows/permission-flow.md)
