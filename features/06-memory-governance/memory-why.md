# Memory Why

**Status:** Concept  
**Stage:** 3  
**Priority:** Highest — this is the most important trust feature.

---

## What It Is

`stareha memory why <id>` shows the complete provenance and reasoning behind any memory. It answers: "How did Stareha come to know this?"

---

## Why It Is The Most Important Feature

This single command transforms Stareha from a black box into a transparent companion.

Without it, the user has to trust Stareha blindly.

With it, the user can verify every single thing Stareha knows — and that verification builds genuine trust.

---

## Full Output Format

```bash
stareha memory why mem_abc123
```

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Memory [mem_abc123]
"You usually run npm run build before npm test in AgentOS."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Why I learned this:
  → Saw this command sequence 8 times in ~/projects/agent-os
  → 5 times: npm test failed when build hadn't run first
  → 4 times: npm test passed after running build
  → Date range: 2026-04-20 to 2026-05-01

How it was processed:
  → Source:    terminal history
  → Method:    pattern_extractor (deterministic script — no LLM)
  → Run ID:    run_20260501_1432
  → Created:   2026-05-01 at 14:32

Confidence:  0.84 ████████░░
Sensitivity: normal

Your action:
  → Approved on 2026-05-02 at 09:14

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Actions: [keep]  [edit]  [forget]  [mark wrong]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Fields Explained

| Field | What it means |
|-------|--------------|
| Evidence count | How many raw events support this |
| Date range | When the evidence was observed |
| Method | What processed the events (script / local LLM / cloud LLM) |
| Run ID | Which learning batch produced this (auditable) |
| Confidence | 0.0–1.0 score (pattern strength) |
| Sensitivity | How private this memory is |
| Your action | When and how the user approved it |

---

## `mark wrong` Action

If the memory is factually wrong:

```
[mark wrong] selected.

Why is this wrong?
> It's backwards — I run npm test first, then build if it fails.

Got it. I'll:
- Delete this memory
- Create a corrected candidate for your review
- Lower confidence for this pattern type from terminal
```

This corrects the memory AND improves future learning.

---

## `sources` Sub-command

```bash
stareha memory sources mem_abc123
```

Shows the actual raw events (redacted) that caused this memory:

```
Evidence events (8):

2026-04-20 10:14  npm run build  [exit 0]  ~/projects/agent-os
2026-04-20 10:15  npm test       [exit 0]  ~/projects/agent-os

2026-04-22 14:03  npm test       [exit 1]  ~/projects/agent-os
2026-04-22 14:05  npm run build  [exit 0]  ~/projects/agent-os
2026-04-22 14:06  npm test       [exit 0]  ~/projects/agent-os
...
```

This is maximum transparency — the user can see the exact raw evidence.

---

## Design Principles for This Feature

1. Show the evidence, not just the conclusion
2. Show WHAT processed it (script vs LLM) — no hidden AI
3. Make every action immediately available after viewing
4. The `mark wrong` path must correct AND improve, not just delete
5. Never require the user to trust the output without seeing the evidence

---

## Related Files
- [Memory Governance](README.md)
- [Memory Commands](memory-commands.md)
- [Provenance](../03-learning-ledger/provenance.md)
- [Memory Governance Flow](../../_flows/memory-governance-flow.md)
