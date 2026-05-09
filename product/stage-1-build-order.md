# Stage 1 — Build Order

**Goal:** `stareha start/stop/status` works. Daemon runs. Terminal commands observed. Events stored in SQLite.

**Language:** Python 3.11+ with `uv`  
**Done when:** `stareha status` shows daemon running + event count growing as you type commands.

**Current note:** Stage 1 is complete. `stareha init` remains as the advanced setup command described here, while the current beginner product setup is `stareha setup` from Stage 5.5.

---

## Pre-work (do first, ~15 min)

```bash
cd /home/ubuntu/Developer/Ayush/Stareha_Project/src
uv init
uv add click pydantic rich httpx inotify-simple
```

Copy these files from reference projects before writing anything new:
- `hermes-agent/agent/redact.py` → `packages/shared/redact.py`
- `hermes-agent/agent/retry_utils.py` → `packages/shared/retry.py`
- `hermes-agent/agent/rate_limit_tracker.py` → `packages/shared/rate_limit.py`
- `agent-os/packages/core/src/tools/approval.ts` → port to `packages/permissions/approval.py`

---

## Step 1 — Config + paths (30 min)

**File:** `packages/core/config.py`

What it does: loads `~/.stareha/config.json`, merges with defaults, expands `~` paths.

```python
# Key fields:
# db_path: ~/.stareha/db.sqlite
# permissions_path: ~/.stareha/permissions.json
# log_path: ~/.stareha/logs/
# daemon_port: 7431
# watched_paths: []
```

Copy pattern from: `official_claude_code/src/state/GlobalConfig.ts` (port to Python)

Acceptance test: `from packages.core.config import load_config; c = load_config(); assert c.db_path.exists() or True`

---

## Step 2 — SQLite schema + store (45 min)

**Files:**
- `packages/core/db/schema.sql` — canonical schema (write once, source of truth)
- `packages/core/db/store.py` — SQLite wrapper (init, read, write, migrate)

Schema tables needed for Stage 1:
```sql
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  source TEXT NOT NULL,
  project TEXT,
  content TEXT NOT NULL,
  session_id TEXT,
  redacted INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL
);

CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  goal TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  started_at INTEGER NOT NULL,
  ended_at INTEGER
);

CREATE TABLE meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

CREATE INDEX idx_events_source ON events(source);
CREATE INDEX idx_events_session ON events(session_id);
CREATE INDEX idx_events_created ON events(created_at);
```

Copy pattern from: `agent-os/packages/core/src/memory/sqlite.ts` (port to Python `sqlite3` stdlib)

Acceptance test: `python -c "from packages.core.db.store import Store; s = Store(':memory:'); print('ok')"`

---

## Step 3 — Redaction (15 min — mostly copy)

**File:** `packages/shared/redact.py`

Just copy `hermes-agent/agent/redact.py` directly. Then:
- Wire `RedactingFormatter` to Python's root logger
- Add `STAREHA_` prefix patterns to the list
- Test: `assert redact_sensitive_text('export API_KEY=sk-abc123xyz') == 'export API_KEY=[REDACTED]'`

This runs before **any** event is written to SQLite. Non-negotiable.

---

## Step 4 — Permission system (30 min — mostly copy)

**File:** `packages/permissions/permissions.py`

What it does: reads/writes `~/.stareha/permissions.json`. Provides `can_collect(source, path=None)`.

```python
def can_collect(source: str, path: str = None) -> bool: ...
def enable_source(source: str, path: str = None) -> None: ...
def disable_source(source: str) -> None: ...
def list_permissions() -> dict: ...
```

Port pattern from: `hermes-agent/acp_adapter/permissions.py` + `agent-os/tools/approval.ts`

Acceptance test: permissions.json starts empty, `can_collect('terminal')` returns False, enable it, returns True.

---

## Step 5 — Terminal collector: history scanner (45 min)

**File:** `packages/collectors/terminal/history_scanner.py`

What it does: reads `~/.zsh_history` or `~/.bash_history`, deduplicates against already-imported events, redacts, writes to SQLite.

```python
def scan_history(store: Store, since: datetime = None) -> int:
    # returns count of new events imported
```

Key details:
- Detect shell: check `$SHELL`, fallback to both files
- Parse zsh extended history format: `: timestamp:elapsed;command`
- Dedup: SHA256(cmd + timestamp) → skip if already in events table
- Redact before insert
- Gate with `can_collect('terminal')`

Copy pattern from: `hermes-agent/agent/shell_hooks.py` (history reading portion)

Acceptance test: run scanner, check `store.count('events', source='terminal') > 0`

---

## Step 6 — Terminal collector: live hook (30 min)

**Files:**
- `packages/collectors/terminal/hook_receiver.py` — HTTP server on port 7431
- `packages/collectors/terminal/shell_hook.sh` — shell script installed by `stareha init`

Hook receiver: tiny `httpx` or stdlib HTTP server, receives POST `/event`, redacts, stores.

Shell script (added to `~/.zshrc` by `stareha init`):
```bash
_stareha_hook() {
  local cmd="$1" exit_code="$?" pwd="$PWD"
  curl -s -X POST http://localhost:7431/event \
    -H 'Content-Type: application/json' \
    -d "{\"type\":\"command\",\"cmd\":\"$cmd\",\"exit\":$exit_code,\"pwd\":\"$pwd\",\"ts\":$(date +%s)}" \
    2>/dev/null &
}
precmd_functions+=(_stareha_hook)
```

Acceptance test: start receiver, POST a test event, check SQLite has it, check redaction ran.

---

## Step 7 — File watcher (30 min — mostly copy)

**File:** `packages/collectors/files/watcher.py`

What it does: uses `inotify-simple` to watch permitted directories. On `IN_CLOSE_WRITE`, fires a `file_edit` event.

```python
def watch(paths: list[str], store: Store) -> None:
    # blocking loop — run in thread
```

Gate with `can_collect('files', path)`.  
Never store file contents — only path + extension + timestamp.

Copy pattern from: `official_claude_code/src/utils/FileWatcher.ts` (port to Python inotify-simple)

Acceptance test: watch `/tmp/test/`, create a file, check SQLite has `file_edit` event.

---

## Step 8 — Daemon (1 hour)

**File:** `apps/daemon/main.py`

What it does: starts everything, runs the event loop, exposes port 7431.

```python
def main():
    config = load_config()
    store = Store(config.db_path)
    
    # Start collectors in threads
    if can_collect('terminal'):
        threading.Thread(target=hook_receiver, args=(store,), daemon=True).start()
    
    for path in config.watched_paths:
        if can_collect('files', path):
            threading.Thread(target=watch, args=([path], store), daemon=True).start()
    
    # Scan history on start
    scan_history(store)
    
    # Keep alive
    signal.pause()
```

PID file: `~/.stareha/daemon.pid` — used by CLI to check if running.

---

## Step 9 — Systemd service (20 min)

**File:** `apps/daemon/stareha.service` (template, installed by `stareha init`)

```ini
[Unit]
Description=Stareha AI Companion Daemon
After=default.target

[Service]
Type=simple
ExecStart=%h/.local/bin/stareha daemon
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

`stareha init` copies this to `~/.config/systemd/user/stareha.service` and runs `systemctl --user enable stareha`.

---

## Step 10 — CLI commands (1 hour)

**File:** `apps/cli/main.py`

Build these commands in order — stop when `stareha status` works:

```
stareha init          # first-run wizard: enable sources, install shell hook, enable systemd
stareha start         # systemctl --user start stareha
stareha stop          # systemctl --user stop stareha
stareha status        # show daemon running + event count + active sources
stareha session start # write session to DB, set active
stareha session stop  # close session, print summary
```

Use `click` for command parsing. Use `rich` for output formatting.

`stareha status` target output:
```
Stareha  running (uptime: 2h 14m)
──────────────────────────────────
Sources    terminal ✓   files ✗   claude-code ✗
Events     247 total   12 today
Session    learning flexbox (active, 45 min)
Inbox      0 pending
```

---

## Acceptance Test for Stage 1 Complete

```bash
# 1. Install
stareha init  # should complete without error

# 2. Daemon runs
stareha start
stareha status  # shows "running"

# 3. Events captured
echo "test" > /tmp/test.txt  # if files permission enabled
ls /tmp                       # terminal command captured

# 4. Events in DB
sqlite3 ~/.stareha/db.sqlite "SELECT count(*) FROM events;"
# should show > 0

# 5. Clean shutdown
stareha stop
stareha status  # shows "stopped"
```

---

## File Creation Order (strict)

```
1. packages/core/config.py
2. packages/core/db/schema.sql
3. packages/core/db/store.py
4. packages/shared/redact.py         ← copy from hermes-agent
5. packages/shared/retry.py          ← copy from hermes-agent
6. packages/permissions/permissions.py
7. packages/collectors/terminal/history_scanner.py
8. packages/collectors/terminal/hook_receiver.py
9. packages/collectors/files/watcher.py
10. apps/daemon/main.py
11. apps/daemon/stareha.service
12. apps/cli/main.py
```

**Total estimated time:** 6–8 hours for a working Stage 1.

---

## Related Files
- [Daemon & Runtime](../features/07-daemon-runtime/README.md)
- [Terminal Connector](../features/01-learning/connectors/terminal.md)
- [Permission System](../features/08-permission-system/README.md)
- [Reuse Map](../reference/reuse-map.md)
