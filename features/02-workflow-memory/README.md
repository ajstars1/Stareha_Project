# Feature: Workflow Memory

**Status:** Concept  
**Stage:** 2  
**Why it matters:** Memory is what makes Stareha a companion, not just a tool. Without persistent workflow memory, every session starts from zero.

---

## What It Is

Workflow memory stores durable, approved patterns about how the user works — their commands, projects, habits, decisions, and research.

This is the persistent memory layer that makes the "never restart from zero" promise possible.

---

## Why It Matters

Developers constantly lose context. They forget:
- Why they changed a file
- Which command fixed an issue
- What they researched yesterday
- What the next task was

Workflow memory solves this by accumulating context over time.

---

## Memory Types

| Type | File | What it captures |
|------|------|----------------|
| Terminal memory | [terminal-memory.md](terminal-memory.md) | Command sequences, project habits, error-fix pairs |
| Project memory | [project-memory.md](project-memory.md) | File patterns, build tools, active focus area |
| Browser/research memory | [browser-memory.md](browser-memory.md) | Research topics, frequently used docs |
| Claude Code memory | [claude-code-memory.md](claude-code-memory.md) | Decisions, bugs fixed, open tasks |
| App usage memory | [app-usage-memory.md](app-usage-memory.md) | Work environment, time-of-day patterns |

---

## How It Works

See: [Workflow Memory Flow](../../_flows/workflow-memory-flow.md)

Short version:
1. Connectors send raw events to the event store
2. Pattern extractors run on the events (deterministic scripts)
3. Interesting patterns become memory candidates
4. User reviews and approves candidates
5. Approved memories are stored with full provenance
6. Memories are available for session summaries and prepared guidance

---

## Memory Lifecycle

```
Event → Candidate → Inbox → Approved Memory → Active
                         ↘ Rejected → Discarded
```

Approved memories can be:
- Updated when new evidence arrives
- Corrected by the user
- Deleted by the user
- Aged out if not seen for 90 days (optional)

---

## Related Flows
- [Workflow Memory Flow](../../_flows/workflow-memory-flow.md)
- [Learning Ledger Flow](../../_flows/learning-ledger-flow.md)
- [Memory Governance Flow](../../_flows/memory-governance-flow.md)
