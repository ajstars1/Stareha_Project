# Memory Commands

**Status:** Concept  
**Stage:** 2–3

---

## All `stareha memory` Commands

### Inbox

```bash
stareha memory inbox
```
Show pending memory candidates awaiting review.

Output:
```
Memory Inbox — 2 pending

1. [mem_abc123] "In AgentOS, you run npm run build before npm test."
   Source: terminal | Confidence: 0.84 | Sensitivity: normal
   (a)pprove  (r)eject  (e)dit  (w)hy

2. [mem_def456] "You are prioritizing Linux-first development."
   Source: conversation | Confidence: 0.93 | Sensitivity: normal
   (a)pprove  (r)eject  (e)dit  (w)hy
```

---

### Approve

```bash
stareha memory approve mem_abc123
```
Accept a candidate. Memory is written with full provenance.

---

### Reject

```bash
stareha memory reject mem_abc123
```
Discard a candidate. Feedback recorded to improve future learning.

---

### Edit

```bash
stareha memory edit mem_abc123
```
Opens memory content in editor. User corrects text. Saved version is approved with note that user edited it.

---

### Why

```bash
stareha memory why mem_abc123
```
Show full provenance. See: [Memory Why](memory-why.md)

---

### Forget

```bash
stareha memory forget mem_abc123
```
Permanently delete an approved memory. Confirmation required.

---

### List

```bash
stareha memory list
stareha memory list --project agent-os
stareha memory list --type command_pattern
stareha memory list --source terminal
```
Show all approved memories with optional filters.

---

### Search

```bash
stareha memory search "flexbox"
stareha memory search "npm test"
```
Full-text search across memory content.

---

### Sources

```bash
stareha memory sources mem_abc123
```
Show the raw events that caused this memory (full evidence trail).

---

### Stats

```bash
stareha memory stats
```
Output:
```
Memory stats:
  Total approved: 47
  Pending in inbox: 3
  Rejected total: 12
  By source: terminal (28), claude_code (12), browser (7)
  By type: command_pattern (18), project_context (11), decision (8)...
```

---

### Export

```bash
stareha memory export --format json > stareha-backup.json
stareha memory export --format markdown > stareha-backup.md
```
Export all memories for backup or inspection.

---

### Reset

```bash
stareha memory reset --confirm
```
Delete ALL memories and candidates. Irreversible. Requires explicit `--confirm`.

---

## Global Controls

```bash
stareha pause                     # Pause all learning (daemon continues running)
stareha resume                    # Resume learning
stareha status                    # Show learning status + memory count
```

---

## Related Files
- [Memory Governance](README.md)
- [Memory Why](memory-why.md)
- [Memory Governance Flow](../../_flows/memory-governance-flow.md)
