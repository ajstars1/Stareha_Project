# MVP Scope

**Status:** Defined  
**Stage:** 1–5.5 (runtime, memory, guidance, optional intelligence, product wrapper)

---

## MVP Goal

```
Stareha remembers what the user is working on or learning,
shows what happened in a Learning Card, and suggests the next useful step.
```

---

## MVP Features

| # | Feature | Stage |
|---|---------|-------|
| 1 | Linux daemon (`stareha start/stop/status`) | 1 |
| 2 | Terminal command learning | 2 |
| 3 | Beginner learning sessions (`learn` / `done`) | 5.5 |
| 4 | Local SQLite memory | 2 |
| 5 | Memory Inbox (CLI) | 2 |
| 6 | Learning Ledger (provenance) | 3 |
| 7 | Learning Card | 5.5 |
| 8 | Basic proactive suggestions | 3 |
| 9 | Local-first summarization | 3 |
| 10 | AI optional: scripts by default, local LLM if available, cloud only when explicitly allowed | 5 |

---

## MVP Demo Script

```bash
# First-time setup
stareha setup

# Start a learning session
stareha learn "learn web development"

# User studies and codes normally...
stareha note "I am confused about DOM selectors"

# End session
stareha done

# Return later
stareha continue
```

**Expected output for `stareha done`:**
```
Learning Card
Goal  learn web development
Project  portfolio-site  (1h 12m)

Worked on
- learn web development
- Ran 24 terminal command(s)
- Edited project files (.html x4, .css x8)

Stuck on
- I am confused about DOM selectors

Next step
-> Continue with one focused practice task for: learn web development
```

---

## MVP CLI Commands

```bash
stareha start                          # Start daemon
stareha stop                           # Stop daemon
stareha status                         # Daemon + memory status

stareha setup                          # Beginner setup
stareha                                # Home screen
stareha learn "<goal>"                 # Begin learning session
stareha learn "<goal>" --project <path> # Begin with explicit project
stareha note "<text>"                  # Add session/project note
stareha done                           # End session, trigger learning run, show Learning Card
stareha continue                       # Resume from last useful point

stareha what-did-you-learn today       # Session summary
stareha what-did-you-learn yesterday   # Prior session summary
stareha prep                           # Generate next-session guidance

stareha memory inbox                   # Show pending memory candidates
stareha memory approve <id>            # Accept a memory
stareha memory reject <id>             # Discard a memory
stareha memory edit <id>               # Edit a memory
stareha memory why <id>                # Show provenance for a memory
stareha memory forget <id>             # Delete a memory

stareha session start "<goal>"         # Advanced session control
stareha session stop                   # Advanced session stop
```

---

## MVP Non-Goals

These are explicitly out of scope for MVP:

- Desktop UI
- Browser extension
- Android app
- Cloud sync
- Requiring cloud AI for the learning loop
- Automatic cloud LLM use without explicit command-level consent
- Multi-device support
- Browser history connector (manual tagging only)

---

## MVP Success Criteria

The MVP is successful when:

1. Stareha runs as a background daemon on Linux
2. It observes terminal commands and learning sessions with permission
3. It generates useful Learning Cards at session end
4. The user can inspect every memory and its source
5. The user can approve, reject, and edit memories
6. `stareha continue` prevents the user from restarting from zero

---

## Related Files
- [Roadmap](roadmap.md)
- [Learning Ledger](../features/03-learning-ledger/README.md)
- [Workflow Memory](../features/02-workflow-memory/README.md)
- [CLI Interface](../features/09-interfaces/cli.md)
