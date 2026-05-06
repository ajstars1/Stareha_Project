# Claude Code Memory

**Status:** Concept  
**Stage:** 2

---

## What It Is

Claude Code memory stores what Stareha learns from the user's AI coding sessions — architectural decisions, bugs fixed, open tasks, and project discussions.

---

## Why It Matters

Claude Code sessions contain the user's explicit intent in natural language. This is the highest-signal source for understanding:
- What the user is building and why
- What decisions were made
- What problems were solved
- What is still unresolved

---

## Memory Categories

### Architectural Decisions
Choices made during Claude Code sessions.

Example:
```
Memory: "Decided to use SQLite for local event store — simpler than PostgreSQL for local-first."
Source: claude_code session 2026-05-01
Confidence: 0.91
```

### Bugs Fixed
Debugging sessions that resulted in a fix.

Example:
```
Memory: "Fixed: pnpm workspace link issue — solved by adding package to workspace root."
Source: claude_code session 2026-05-03
Confidence: 0.85
```

### Open Tasks
Incomplete items from Claude Code sessions.

Example:
```
Memory: "TODO: Wire up memory_candidates table to CLI inbox command"
Source: claude_code session 2026-05-04
Status: open
```

### Project Plans
Plans and roadmaps discussed in sessions.

Example:
```
Memory: "AgentOS Continuum roadmap: Stage 1 = daemon, Stage 2 = workflow memory, Stage 3 = ledger"
Source: claude_code session 2026-04-28
Confidence: 0.93
```

---

## How Confidence Is Assigned

| Signal | Confidence boost |
|--------|----------------|
| User explicitly states decision | +0.2 |
| Decision confirmed in multiple sessions | +0.1 |
| Decision matches observed behavior | +0.1 |
| Mentioned once, not confirmed | base: 0.5 |

---

## Related Files
- [Workflow Memory](README.md)
- [Claude Code Connector](../01-learning/connectors/claude-code.md)
- [Project Memory](project-memory.md)
- [Work Task Prep](../04-prepared-guidance/work-task-prep.md)
