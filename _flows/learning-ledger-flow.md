# Learning Ledger Flow

> Master logic file. Read before implementing. Update when logic changes.

**Status:** Defined  
**Stage:** 3

---

## What This Covers

The full pipeline from raw event to transparent, provenance-tracked memory.

This is the most important trust layer.

---

## Core Rule

```
No memory without provenance.
```

---

## Full Pipeline

```
Raw event observed
  ↓
Redaction applied
  (secrets, tokens, passwords stripped)
  ↓
Event written to ledger_events table
  (immutable, local only)
  ↓
Classification
  (event type, source, project, session)
  ↓
Summary generated
  (scripts first → local LLM if complex → never cloud at this stage)
  ↓
Memory candidate created
  {
    id,
    content,          -- the proposed memory text
    source,           -- 'terminal', 'browser', 'claude_code', etc.
    evidence_ids,     -- list of ledger_events that support this
    model_used,       -- 'pattern_extractor' / 'local_llm' / 'cloud_llm'
    confidence,       -- 0.0–1.0
    sensitivity,      -- 'low' / 'normal' / 'high'
    created_at
  }
  ↓
Candidate enters Memory Inbox
  ↓
User reviews → approve / reject / edit
  ↓
Feedback recorded
  {
    candidate_id,
    action,           -- 'approved' / 'rejected' / 'edited'
    edit_content,     -- if edited, the corrected version
    feedback_at
  }
  ↓
If approved/edited → Memory written with full provenance
  ↓
Provenance record attached
  {
    memory_id,
    evidence_events,  -- all raw events that caused this memory
    model_used,
    confidence,
    user_approved,
    approved_at
  }
  ↓
Suggestion/action may be generated from memory
  ↓
Suggestion delivered (CLI / tray notification)
  ↓
User acts / dismisses → feedback recorded
```

---

## Ledger Tables (SQLite)

```sql
-- Immutable event log
CREATE TABLE ledger_events (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  source TEXT NOT NULL,
  raw_content TEXT NOT NULL,        -- redacted already
  redaction_applied INTEGER DEFAULT 0,
  classification TEXT,
  session_id TEXT,
  project TEXT,
  created_at INTEGER NOT NULL
);

-- Learning run log
CREATE TABLE learning_runs (
  id TEXT PRIMARY KEY,
  session_id TEXT,
  started_at INTEGER,
  completed_at INTEGER,
  events_processed INTEGER,
  candidates_generated INTEGER,
  model_used TEXT,
  status TEXT
);

-- Memory candidates with full trail
CREATE TABLE memory_candidates (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  source TEXT NOT NULL,
  evidence_ids TEXT NOT NULL,       -- JSON: [ledger_event_id, ...]
  learning_run_id TEXT,
  model_used TEXT NOT NULL,
  confidence REAL NOT NULL,
  sensitivity TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  created_at INTEGER NOT NULL
);

-- User feedback on candidates
CREATE TABLE memory_feedback (
  id TEXT PRIMARY KEY,
  candidate_id TEXT NOT NULL,
  action TEXT NOT NULL,             -- 'approved', 'rejected', 'edited'
  edit_content TEXT,
  feedback_at INTEGER NOT NULL
);

-- Approved memories with provenance
CREATE TABLE memories (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  type TEXT NOT NULL,
  source TEXT NOT NULL,
  evidence_ids TEXT NOT NULL,
  learning_run_id TEXT,
  model_used TEXT NOT NULL,
  confidence REAL NOT NULL,
  sensitivity TEXT NOT NULL,
  user_approved INTEGER DEFAULT 0,
  user_edited INTEGER DEFAULT 0,
  approved_at INTEGER,
  created_at INTEGER NOT NULL
);
```

---

## `stareha memory why <id>` Output Format

```
Memory:
"You usually run npm run build before npm test in AgentOS."

Why I learned this:
- Saw this command sequence 8 times in ~/projects/agent-os
- 5 times npm test failed before build ran
- 4 times npm test passed after build
- Source: terminal history
- Created by: pattern_extractor (deterministic)
- Confidence: 0.84
- Sensitivity: normal
- Learned: 2026-05-01 at 14:32

Actions:
[keep]  [edit]  [forget]  [mark wrong]
```

---

## Related Files
- [Learning Flow](learning-flow.md)
- [Workflow Memory Flow](workflow-memory-flow.md)
- [Memory Governance Flow](memory-governance-flow.md)
- [Learning Ledger Feature](../features/03-learning-ledger/README.md)
