# Feature: Learning Ledger

**Status:** Built  
**Stage:** 3  
**Why it matters:** This is the trust layer. Without it, Stareha is creepy. With it, Stareha is trustworthy.

---

## What It Is

The Learning Ledger is a transparent audit log of everything Stareha has learned, how it learned it, and what evidence supports each memory.

Every memory has full provenance — where it came from, when, why, and how confident Stareha is.

---

## Why It Matters

If Stareha learns from local activity, users need to answer:
- What did it see?
- What did it ignore?
- What did it learn?
- Why did it learn that?
- Which source caused this memory?
- Can I edit or delete it?

Without this, the product feels like spyware.

With this, it feels like a trustworthy assistant.

---

## Core Rule

```
No memory without provenance.
```

---

## Sub-Features

| Sub-feature | File | What it covers |
|-------------|------|---------------|
| Provenance | [provenance.md](provenance.md) | The provenance data model — what's tracked per memory |
| Pipeline | [pipeline.md](pipeline.md) | Event → redaction → classification → memory candidate |
| Memory Inbox | [memory-inbox.md](memory-inbox.md) | Approve, reject, edit, why |
| Feedback Loop | [feedback-loop.md](feedback-loop.md) | How feedback improves learning |

---

## What the Ledger Tracks

For every memory:

| Field | What it is |
|-------|-----------|
| Raw event IDs | Which events caused this memory |
| Redaction applied | Was any data stripped? |
| Summary generated | What summary was created |
| Model/script used | What intelligence layer processed it |
| Confidence score | 0.0–1.0 |
| Sensitivity score | low / normal / high |
| User action | Approved / rejected / edited |
| Feedback recorded | What the user corrected |

---

## The `memory why` Command

The most important feature in the ledger:

```bash
stareha memory why mem_abc123
```

Output:
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

Actions: [keep]  [edit]  [forget]  [mark wrong]
```

---

## Related Flows
- [Learning Ledger Flow](../../_flows/learning-ledger-flow.md)
- [Memory Governance Flow](../../_flows/memory-governance-flow.md)
