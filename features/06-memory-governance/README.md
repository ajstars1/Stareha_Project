# Feature: Memory Governance

**Status:** Built  
**Stage:** 2–3  
**Why it matters:** This is how users trust Stareha. Full control over what it knows — inspect, edit, delete, understand.

---

## What It Is

Memory governance is the complete system for user control over Stareha's memory. Users can see everything, understand why it was learned, correct it, and delete it.

---

## Why It Matters

Without memory governance, Stareha is a black box. With it, users own their data.

The user must always feel:
- "I know what Stareha knows"
- "I can fix anything it got wrong"
- "I can delete anything I don't want"
- "Nothing is hidden from me"

---

## Sub-Features

| Sub-feature | File | What it covers |
|-------------|------|---------------|
| Memory commands | [memory-commands.md](memory-commands.md) | All CLI commands for memory management |
| Memory why | [memory-why.md](memory-why.md) | The `why` command — most important trust feature |

---

## User Rights

The user must always be able to:
- **See** all memories (`stareha memory list`)
- **Understand** why each memory exists (`stareha memory why <id>`)
- **Edit** incorrect memories (`stareha memory edit <id>`)
- **Delete** any memory (`stareha memory forget <id>`)
- **Pause** all learning (`stareha pause`)
- **Reset** everything (`stareha reset --confirm`)
- **Export** their data (`stareha export`)

These are non-negotiable rights, not optional features.

---

## Memory Lifecycle

```
Candidate (pending) → Inbox review
  ↓
Approved → Active memory
  ↓
Active memory → can be edited, deleted, or expired
  ↓
Deleted → removed from all processing
```

---

## Related Flows
- [Memory Governance Flow](../../_flows/memory-governance-flow.md)
- [Learning Ledger Flow](../../_flows/learning-ledger-flow.md)
