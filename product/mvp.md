# MVP Scope

**Status:** Defined  
**Stage:** 1–3 (Stages 1, 2, 3 combined = MVP)

---

## MVP Goal

```
Stareha remembers what the user is working on or learning,
explains what it learned, and suggests the next useful step.
```

---

## MVP Features

| # | Feature | Stage |
|---|---------|-------|
| 1 | Linux daemon (`stareha start/stop/status`) | 1 |
| 2 | Terminal command learning | 2 |
| 3 | Work/learning sessions | 2 |
| 4 | Local SQLite memory | 2 |
| 5 | Memory Inbox (CLI) | 2 |
| 6 | Learning Ledger (provenance) | 3 |
| 7 | Session summary | 3 |
| 8 | Basic proactive suggestions | 3 |
| 9 | Local-first summarization | 3 |
| 10 | Cloud LLM only in talking mode | 3 |

---

## MVP Demo Script

```bash
# Start a learning session
stareha session start "learn web development"

# User studies and codes...

# Run commands through Stareha (or it observes automatically)
stareha run npm test

# End session
stareha session stop

# Ask what was learned
stareha what-did-you-learn today

# Prep tomorrow's session
stareha prep tomorrow
```

**Expected output for `stareha what-did-you-learn today`:**
```
Today I learned:
- You practiced HTML forms and CSS Flexbox.
- You struggled with DOM selectors.
- You searched Flexbox alignment examples repeatedly.
- You prefer project-based exercises.

Prepared for tomorrow:
- 5-question Flexbox quiz
- Responsive card layout exercise
- 3 DOM selector debugging tasks
```

---

## MVP CLI Commands

```bash
stareha start                          # Start daemon
stareha stop                           # Stop daemon
stareha status                         # Daemon + memory status

stareha session start "<goal>"         # Begin tracked session
stareha session stop                   # End session, trigger learning run

stareha what-did-you-learn today       # Session summary
stareha what-did-you-learn yesterday   # Prior session summary
stareha prep tomorrow                  # Generate next-session guidance

stareha memory inbox                   # Show pending memory candidates
stareha memory approve <id>            # Accept a memory
stareha memory reject <id>             # Discard a memory
stareha memory edit <id>               # Edit a memory
stareha memory why <id>                # Show provenance for a memory
stareha memory forget <id>             # Delete a memory
```

---

## MVP Non-Goals

These are explicitly out of scope for MVP:

- Desktop UI
- Browser extension
- Android app
- Cloud sync
- Local LLM integration (cloud LLM only in talking mode)
- Multi-device support
- Browser history connector (manual tagging only)

---

## MVP Success Criteria

The MVP is successful when:

1. Stareha runs as a background daemon on Linux
2. It observes terminal commands and learning sessions
3. It generates session summaries that are accurate
4. The user can inspect every memory and its source
5. The user can approve, reject, and edit memories
6. Next-session guidance is generated and delivered

---

## Related Files
- [Roadmap](roadmap.md)
- [Learning Ledger](../features/03-learning-ledger/README.md)
- [Workflow Memory](../features/02-workflow-memory/README.md)
- [CLI Interface](../features/09-interfaces/cli.md)
