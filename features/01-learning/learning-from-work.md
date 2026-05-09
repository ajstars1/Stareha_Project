# Learning From Work

**Status:** Concept  
**Stage:** 2

---

## What It Is

Stareha learns from the user's actual work sessions — not from what they tell it, but from what they do.

A "work session" is any period of active development activity: editing files, running commands, debugging, researching.

---

## Why It Matters

Manual logging of learning is friction. Nobody reliably writes "today I learned X" after every session.

Stareha removes that friction by observing (with permission) and extracting the important patterns automatically.

---

## How Work Sessions Are Tracked

```
Work session begins:
  User opens terminal / editor in a project directory
  File watcher detects activity → session_started event

During session:
  Terminal commands captured (with permission)
  File changes noted (which files, how often)
  Errors and fixes recorded
  Claude Code conversations noted if active

Work session ends:
  30 minutes of inactivity → session_ended event
  OR: stareha done
  OR: advanced stareha session stop
  ↓
Learning run triggered
```

---

## What Is Extracted From a Work Session

| Signal | Extraction method | Example memory |
|--------|-----------------|----------------|
| Active project | File watcher + git detection | "Working on agent-os" |
| Commands used | Terminal connector | "Runs npm run build in agent-os" |
| Errors encountered | Exit code monitoring | "npm test fails with 'missing module'" |
| Fixes found | Error-fix pair detection | "npm ci fixes module errors" |
| Files most edited | File watcher frequency | "Most active: packages/core/memory.ts" |
| Decisions made | Claude Code connector | "Decided to use SQLite for event store" |
| Session duration | session_started + session_ended timestamps | "Typically works 2-4 hours at a time" |

---

## Explicit Learning Sessions

The beginner product flow explicitly tags sessions:

```bash
stareha learn "build memory candidate pipeline"
# ... user works ...
stareha done
```

This tags all events during the session with the explicit goal, increasing the quality of extracted memories.

Advanced users can still use `stareha session start` and `stareha session stop` directly.

---

## Example Output

After a learning session, `stareha done` shows a Learning Card. Advanced users can also run `stareha what-did-you-learn today`:

```
Today in agent-os:
- You worked for 3h 20m
- Most edited: packages/core/src/memory.ts, packages/cli/src/index.ts
- 4 errors encountered:
  - "cannot find module '@stareha/core'" (fixed with npm link)
  - TypeScript type errors in memory.ts (3 occurrences)
- Decision noted: use SQLite instead of JSON files for event store
- Build sequence: tsc → npm run build → npm test
```

---

## Related Files
- [Learning Feature](README.md)
- [Connectors](connectors/README.md)
- [Learning Flow](../../_flows/learning-flow.md)
- [Workflow Memory](../02-workflow-memory/README.md)
