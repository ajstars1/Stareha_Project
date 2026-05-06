# Learning Flow

> Master logic file. Read before implementing. Update when logic changes.

**Status:** Defined  
**Stage:** 2–3

---

## What This Covers

End-to-end: how Stareha learns from user activity.

---

## Full Flow

```
User activity (terminal, browser, files, Claude Code)
  ↓
Event collector (daemon captures raw events)
  ↓
Redaction (strip secrets, tokens, passwords)
  ↓
Classification (what type of event? work / learn / admin)
  ↓
Importance scoring (is this worth learning from?)
  ↓
Deduplication (have we seen this pattern before?)
  ↓
Summarization (scripts first, local LLM if needed)
  ↓
Memory candidate generated (proposed memory + source + confidence)
  ↓
Memory Inbox (user reviews candidates)
  ↓
User approves / rejects / edits
  ↓
Memory written to store (with full provenance)
  ↓
Learning profile updated
  ↓
Prepared Guidance triggered (async, at end of session)
```

---

## Input Sources

| Source | Collected by | When |
|--------|-------------|------|
| Terminal commands | Shell hook / history scanner | Continuous or on session end |
| Claude Code conversations | History importer | On session end |
| Browser visits | Browser extension (Stage 7) | On navigation / page close |
| File changes | Filesystem watcher | On save |
| App usage | App usage monitor | Periodic |
| User goals | Explicit user input | On session start |

---

## Classification Rules

| Event type | Action |
|------------|--------|
| `command_run` with error | Learn error pattern |
| `command_run` success after failure | Learn fix pattern |
| `file_edited` in project | Learn active file context |
| `browser_visit` to docs/tutorial | Learn research topic |
| `claude_code_decision` | Learn architectural decision |
| `session_goal` set | Update learning profile |

---

## Importance Scoring

Score 0.0–1.0. Store if score ≥ 0.5.

Factors:
- Frequency (seen 3+ times = higher score)
- Error/fix pair (higher score)
- Explicit user signal (highest score)
- Trivial/admin commands (lower score)

---

## Learning Run Trigger

Learning runs happen:
1. On `stareha session stop`
2. On system idle (after 30 min of inactivity)
3. Manually via `stareha learn now`

---

## Rules

- Never store raw data — only summaries/patterns
- Every memory candidate must have source + timestamp + confidence
- User must approve before memory is written (MVP: auto-approve with inbox review)
- If confidence < 0.5, send to inbox, never auto-approve
- Redaction runs before any other step — no exceptions

---

## Related Files
- [Workflow Memory Flow](workflow-memory-flow.md)
- [Learning Ledger Flow](learning-ledger-flow.md)
- [Intelligence Policy Flow](intelligence-policy-flow.md)
- [Connectors](../features/01-learning/connectors/README.md)
