# Memory Governance Flow

> Master logic file. Read before implementing. Update when logic changes.

**Status:** Defined  
**Stage:** 2–3

---

## What This Covers

How users review, approve, edit, reject, and maintain their memories.

---

## Core Principle

The user owns their memory. Stareha is a steward, not the owner.

---

## Full Flow

```
Memory candidate created (from learning run)
  ↓
Appears in Memory Inbox (status: 'pending')
  ↓
User runs: stareha memory inbox
  ↓
User sees list of pending candidates:
  "1. In AgentOS, you run npm run build before npm test.  [confidence: 0.84]"
  "2. You are currently prioritizing Linux-first development. [confidence: 0.93]"
  ↓
User chooses action per candidate:
  ├── approve → memory written, status: 'approved'
  ├── reject  → candidate discarded, status: 'rejected'
  ├── edit    → user corrects content, stored as edited, status: 'approved'
  └── why     → provenance shown, user decides after
  ↓
Feedback written to memory_feedback table
  ↓
Approved memories become available for:
  - Session summaries
  - Prepared guidance
  - Cloud LLM context
  - `stareha memory why` queries
  ↓
Over time:
  User feedback trains importance scoring
  (things frequently rejected → lower future scores for similar patterns)
```

---

## Memory Inbox CLI Output

```
Memory Inbox — 2 pending

1. [id: mem_abc123]
   "In AgentOS, you usually run npm run build before npm test."
   Source: terminal | Confidence: 0.84 | Sensitivity: normal
   Actions: (a)pprove  (r)eject  (e)dit  (w)hy

2. [id: mem_def456]
   "You are currently prioritizing Linux-first AgentOS Continuum."
   Source: conversation | Confidence: 0.93 | Sensitivity: normal
   Actions: (a)pprove  (r)eject  (e)dit  (w)hy
```

---

## `stareha memory why <id>` Output

```
Memory:
"You usually run npm run build before npm test in AgentOS."

Why I learned this:
- Saw this sequence 8 times in ~/projects/agent-os
- 5 times npm test failed when build hadn't run
- 4 times npm test passed after build
- Source: terminal history
- Created by: pattern_extractor (deterministic)
- Confidence: 0.84 | Sensitivity: normal
- Learned: 2026-05-01 at 14:32

Actions:
[keep]  [edit]  [forget]  [mark wrong]
```

---

## All Memory Commands

| Command | What it does |
|---------|-------------|
| `stareha memory inbox` | Show pending candidates |
| `stareha memory approve <id>` | Accept a memory |
| `stareha memory reject <id>` | Discard a candidate |
| `stareha memory edit <id>` | Edit content and approve |
| `stareha memory forget <id>` | Delete an approved memory |
| `stareha memory why <id>` | Show full provenance |
| `stareha memory sources <id>` | Show all raw events that caused this |
| `stareha memory list` | Show all approved memories |
| `stareha memory search <query>` | Search memories by content |

---

## Feedback Loop

User actions feed back into the learning system:

| User action | System learns |
|-------------|--------------|
| reject candidate | Lower score for this pattern type |
| edit candidate | Preferred content format for this source |
| mark wrong | Flag this source as unreliable for this type |
| approve without edit | Confidence calibration: this score = good |

---

## Related Files
- [Learning Ledger Flow](learning-ledger-flow.md)
- [Memory Governance Feature](../features/06-memory-governance/README.md)
- [Memory Commands](../features/06-memory-governance/memory-commands.md)
- [Memory Why](../features/06-memory-governance/memory-why.md)
