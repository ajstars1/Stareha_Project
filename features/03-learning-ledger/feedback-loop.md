# Feedback Loop

**Status:** Concept  
**Stage:** 3

---

## What It Is

The feedback loop is how user decisions about memories (approve, reject, edit, mark wrong) feed back into the learning system to make future learning more accurate.

---

## Why It Matters

Without feedback, Stareha would keep proposing the same kinds of wrong memories.

With feedback, Stareha gets smarter over time — not by guessing, but by learning from explicit corrections.

---

## Feedback Types

| Action | Feedback signal |
|--------|---------------|
| `approve` | This pattern type + source = valid at this confidence |
| `reject` | This pattern type or source = unreliable for this context |
| `edit` | User's correction is the canonical content format |
| `mark wrong` | This source created a bad memory — flag source |
| `approve after why` | User needed provenance to trust this — lower auto-confidence |

---

## How Feedback Affects Learning

### Rejection feedback

When a candidate is rejected:
- Pattern type score for that source is reduced by 0.05
- If 3+ rejections of same pattern type → threshold raised for new candidates of that type

### Edit feedback

When a candidate is edited:
- The edit is analyzed to find what was wrong
- Future candidates of same type prefer the user's format
- Edited text becomes training signal for local LLM summarization

### Mark wrong feedback

When a memory is marked wrong:
- All candidates from that source in that session are flagged for review
- Source confidence for that event type is reduced

---

## Feedback Storage

```sql
CREATE TABLE memory_feedback (
  id TEXT PRIMARY KEY,
  candidate_id TEXT NOT NULL,
  action TEXT NOT NULL,           -- 'approved', 'rejected', 'edited', 'marked_wrong'
  edit_content TEXT,              -- only if edited
  context_note TEXT,              -- optional user comment
  feedback_at INTEGER NOT NULL
);
```

---

## Feedback Dashboard (Future — Stage 6)

A page showing:
- Most approved pattern types
- Most rejected pattern types
- Sources with low approval rates
- Edit frequency by memory type

Helps the user understand and tune what Stareha learns.

---

## Related Files
- [Learning Ledger](README.md)
- [Memory Governance Flow](../../_flows/memory-governance-flow.md)
- [Learning Flow](../../_flows/learning-flow.md)
