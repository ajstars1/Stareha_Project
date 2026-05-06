# Work Task Preparation

**Status:** Concept  
**Stage:** 4

---

## What It Is

Work task preparation is Stareha's ability to analyze the developer's recent work session and prepare a focused briefing for the next: what was completed, what is in progress, and what the most logical next step is.

---

## Why It Matters

Developers lose context constantly. After a weekend or even a 24-hour break, they often forget exactly where they stopped.

Stareha eliminates this context loss by maintaining work state between sessions.

---

## What Goes Into Work Task Prep

| Input | Source |
|-------|--------|
| Completed tasks | Session history, Claude Code memory |
| In-progress work | Last edited files (file watcher) |
| Open tasks | Claude Code conversations, user notes |
| Last command run | Terminal memory |
| Active errors | Error pattern memory |
| Architectural decisions | Claude Code memory |

---

## Output: Work Briefing

See: [Session Briefing](session-briefing.md) — Work format section

Key elements:
1. Project name + last active time + duration
2. Completed list (with file references if available)
3. In-progress item (with specific stopping point)
4. Open task list (prioritized)
5. Next suggested step (specific, actionable)
6. Relevant command or context

---

## Next Step Suggestion Logic

```
Last edited file → identify function/feature being worked on
  ↓
Scan for incomplete TODO comments or partial implementations
  ↓
Cross-reference with open tasks from Claude Code memory
  ↓
Score by:
  - Recency (most recently touched = highest priority)
  - Blocking (does this block other tasks?)
  - Explicitness (was it written as next step in Claude Code session?)
  ↓
Suggest top 1 next step with context
```

---

## Bug Investigation Prep

If error patterns are detected:

```
Recurring error: "cannot find module @stareha/core" (3 occurrences)
Last failed command: npm test in packages/cli
Potential fix: Check pnpm workspace links — this fixed it previously in agent-os.
```

---

## Related Files
- [Prepared Guidance](README.md)
- [Project Memory](../02-workflow-memory/project-memory.md)
- [Claude Code Memory](../02-workflow-memory/claude-code-memory.md)
- [Session Briefing](session-briefing.md)
