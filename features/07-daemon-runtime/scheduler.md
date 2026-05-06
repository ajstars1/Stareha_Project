# Scheduler

**Status:** Concept  
**Stage:** 1

---

## What It Is

The scheduler determines when learning runs execute, when guidance is prepared, and when periodic tasks like history scanning occur.

---

## Why It Matters

Timing matters for the companion experience:
- Learning runs should happen when sessions end (not interrupt active work)
- Guidance should be ready before the user needs it
- Background tasks should not spike CPU during active development

---

## Scheduled Tasks

| Task | Trigger | Frequency |
|------|---------|-----------|
| Learning run | Session end + idle (30 min) | After each session |
| Guidance preparation | After learning run | After each session |
| History scan | Startup + nightly | Daily at 02:00 |
| Claude Code import | Session end | After each session |
| Memory inbox notification | After learning run | When candidates > 0 |
| App usage snapshot | While active | Every 5 minutes |
| Log rotation | Nightly | Daily at 03:00 |

---

## Session-End Detection

```
User runs stareha session stop
  OR
30 minutes of no file edits AND no terminal commands
  ↓
session_ended event emitted
  ↓
Triggers:
  - Claude Code import
  - Learning run
  - Guidance preparation
```

---

## Learning Run Schedule

```
Session ended at T
  T + 0s:   Import Claude Code history
  T + 30s:  Run pattern extractor on new events
  T + 60s:  Run local LLM summarization (if available)
  T + 120s: Generate memory candidates
  T + 130s: Write candidates to inbox
  T + 135s: Prepare guidance (background)
  T + 300s: Guidance ready
```

---

## Idle Detection

```python
IDLE_THRESHOLD_SECONDS = 1800  # 30 minutes

def is_idle() -> bool:
    last_event = db.get_last_event_time()
    return (time.time() - last_event) > IDLE_THRESHOLD_SECONDS
```

---

## Priority Queue

Learning tasks are queued with priority:

| Priority | Task |
|----------|------|
| 1 (highest) | Session-triggered learning run |
| 2 | Guidance preparation |
| 3 | Scheduled history scan |
| 4 (lowest) | Background deduplication |

If system is under load (CPU > 70%), lower priority tasks are deferred.

---

## Manual Triggers

```bash
stareha learn now           # Trigger learning run immediately
stareha prep now            # Trigger guidance preparation immediately
stareha import claude-code  # Force Claude Code import
```

---

## Related Files
- [Daemon & Runtime](README.md)
- [Linux Daemon](linux-daemon.md)
- [Learning Flow](../../_flows/learning-flow.md)
