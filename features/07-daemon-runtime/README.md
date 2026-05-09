# Feature: Daemon & Runtime

**Status:** Built  
**Stage:** 1  
**Why it matters:** The daemon is the foundation. Without it, Stareha is a command you run manually. With it, Stareha is a companion that's always observing and preparing.

---

## What It Is

The daemon is a Linux background process (systemd user service) that continuously runs Stareha's event collection, learning runs, and guidance preparation in the background.

---

## Why It Matters

Stareha must be ambient. The user shouldn't have to think about running it.

The daemon ensures:
- Events are captured continuously (terminal, files)
- Learning runs happen automatically at the right time
- Guidance is prepared before the user needs it
- Stareha is ready when the user opens a session

---

## Sub-Features

| Sub-feature | File | What it covers |
|-------------|------|---------------|
| Linux daemon | [linux-daemon.md](linux-daemon.md) | systemd service, start/stop/status |
| Event collectors | [event-collectors.md](event-collectors.md) | What is collected, how, permission gating |
| Scheduler | [scheduler.md](scheduler.md) | When learning runs, when guidance is prepared |

---

## Daemon Responsibilities

| Responsibility | When | Status |
|---------------|------|--------|
| Collect terminal events | Continuous (via shell hook on port 7431) | ✅ |
| Scan terminal history | On daemon start | ✅ |
| Watch file changes | Continuous (inotify) | ✅ |
| Import Claude Code history | On daemon start | ✅ |
| Import browser history | On daemon start | ✅ |
| Run learning run | On session end + manually | ✅ |
| Prepare guidance | After learning run, manually | ✅ |
| Deliver briefing | On `stareha learn` / advanced session start | ✅ |
| Memory inbox notification | When new candidates arrive | ✅ |

---

## Daemon Lifecycle

```bash
stareha start   # Start daemon — tries systemd first, falls back to direct subprocess
stareha stop    # Stop daemon — kills via PID file if systemd unavailable
stareha status  # Show daemon status + memory stats + active sources + LLM status
stareha restart # Restart daemon (stop then start)
```

### Startup behaviour

On start, the daemon runs immediately:
1. Scans `~/.zsh_history` / `~/.bash_history` for terminal events
2. Scans `~/.claude/projects/` for Claude Code sessions
3. Scans Chrome/Firefox history SQLite files
4. Starts the shell hook HTTP server (port 7431)
5. Starts inotify file watchers for permitted paths

All steps are permission-gated — only enabled sources are scanned.

### systemd vs direct launch

`stareha start` tries systemd first if `~/.config/systemd/user/stareha.service` exists.
If systemd is unavailable or the service file is not installed, it launches the daemon
as a detached subprocess using `start_new_session=True`. The PID is written to
`~/.stareha/daemon.pid` and checked by all commands.

`stareha setup` installs the systemd service file as part of beginner setup. The advanced `stareha init` command can also install it. Without either setup path, direct launch is used.

---

## Resource Usage Target

- CPU: < 1% average (event-driven, not polling)
- RAM: < 50MB
- Disk: event store grows ~1MB/week at typical usage
- Network: zero unless cloud LLM explicitly triggered

---

## Related Flows
- [Learning Flow](../../_flows/learning-flow.md)
- [Permission Flow](../../_flows/permission-flow.md)
