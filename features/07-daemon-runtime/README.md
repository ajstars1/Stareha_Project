# Feature: Daemon & Runtime

**Status:** Concept  
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

| Responsibility | When |
|---------------|------|
| Collect terminal events | Continuous (via shell hook) |
| Watch file changes | Continuous (inotify) |
| Import Claude Code history | On session end |
| Run learning run | On session end + scheduled |
| Prepare guidance | After learning run |
| Deliver suggestions | On session start / scheduled |
| Memory inbox notification | When new candidates arrive |

---

## Daemon Lifecycle

```bash
stareha start   # Start daemon (systemd enable + start)
stareha stop    # Stop daemon  (systemd stop)
stareha status  # Show daemon status + memory stats + active sources
stareha restart # Restart daemon
```

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
