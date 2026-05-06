# Memory Inbox

**Status:** Concept  
**Stage:** 2–3

---

## What It Is

The Memory Inbox is where pending memory candidates wait for user review. The user decides what Stareha permanently remembers.

This is the main control surface between Stareha's learning and the user's trust.

---

## Why It Matters

Auto-approving all memories would be fast but creepy. The inbox gives users:
- Visibility into what Stareha wants to learn
- Control over what gets stored
- A chance to correct wrong patterns
- Confidence that nothing is hidden

---

## CLI Interface

```bash
stareha memory inbox
```

Output:
```
Memory Inbox — 3 pending

1. [mem_abc123]
   "In AgentOS, you run npm run build before npm test."
   Source: terminal | Confidence: 0.84 | Sensitivity: normal
   (a)pprove  (r)eject  (e)dit  (w)hy

2. [mem_def456]
   "You are currently prioritizing Linux-first AgentOS Continuum."
   Source: conversation | Confidence: 0.93 | Sensitivity: normal
   (a)pprove  (r)eject  (e)dit  (w)hy

3. [mem_ghi789]
   "Frequently searches Flexbox alignment — likely a weak concept."
   Source: browser | Confidence: 0.79 | Sensitivity: normal
   (a)pprove  (r)eject  (e)dit  (w)hy
```

---

## User Actions

| Action | Command | What happens |
|--------|---------|-------------|
| Approve | `a` or `stareha memory approve <id>` | Memory written with provenance |
| Reject | `r` or `stareha memory reject <id>` | Candidate discarded, feedback logged |
| Edit | `e` or `stareha memory edit <id>` | User corrects content, then approved |
| Why | `w` or `stareha memory why <id>` | Full provenance shown |
| Skip | Enter | Leaves in inbox for later |

---

## Batch Actions (MVP)

```bash
stareha memory inbox --approve-all    # Approve everything (use carefully)
stareha memory inbox --review         # Interactive step-through
```

---

## Auto-Approve Policy

In MVP: nothing is auto-approved. All candidates wait in inbox.

Future (Stage 4+): User may configure auto-approve rules:
```bash
stareha config set inbox.auto_approve_above 0.95
stareha config set inbox.auto_approve_source terminal
```

---

## Inbox Notification

When new candidates arrive, Stareha notifies:
- CLI: shows count at start of next terminal session
- Desktop (Stage 6): tray badge with count

---

## Related Files
- [Learning Ledger](README.md)
- [Memory Commands](../06-memory-governance/memory-commands.md)
- [Memory Governance Flow](../../_flows/memory-governance-flow.md)
