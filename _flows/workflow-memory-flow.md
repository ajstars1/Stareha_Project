# Workflow Memory Flow

> Master logic file. Read before implementing. Update when logic changes.

**Status:** Defined  
**Stage:** 2

---

## What This Covers

How raw events become durable workflow memories stored in the memory system.

---

## Full Flow

```
Raw event arrives (from any collector)
  ↓
Event written to SQLite event store (raw, local only)
  ↓
Pattern extractor runs (deterministic scripts)
  ↓
  ├── Command frequency analysis
  ├── Project association
  ├── Error/fix pairing
  ├── Session classification (work vs learn)
  └── Workflow sequence detection
  ↓
Memory candidate generated
  {
    content: "In AgentOS, Ayush runs npm run build before npm test",
    source: "terminal",
    project: "agent-os",
    evidence_count: 8,
    confidence: 0.84,
    sensitivity: "normal",
    created_at: timestamp
  }
  ↓
Candidate → Memory Inbox
  ↓
User approves → Memory written to memories table
  ↓
Memory available for:
  - Session summaries
  - Prepared guidance
  - Context for cloud LLM calls
  - `stareha memory why` queries
```

---

## Memory Types

| Type | What it captures | Example |
|------|-----------------|---------|
| `command_pattern` | Repeated command sequences | "Run build before test in AgentOS" |
| `project_context` | Active project, tools, structure | "AgentOS uses TypeScript monorepo" |
| `error_fix` | What fixed a repeated error | "npm cache clean fixes install errors" |
| `work_habit` | Time/app patterns | "Works in VS Code + terminal + browser" |
| `research_topic` | Browser/doc usage | "Often researches Flexbox alignment" |
| `decision` | Architecture/code decisions | "Chose SQLite for local event store" |
| `learning_goal` | What user wants to learn | "Learning web development" |
| `weak_concept` | Where user repeatedly struggles | "DOM selectors" |

---

## Storage Schema (SQLite)

```sql
-- Raw events (never modified after write)
CREATE TABLE events (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,           -- 'command_run', 'file_edit', 'browser_visit', etc.
  source TEXT NOT NULL,         -- 'terminal', 'browser', 'claude_code', 'file_watcher'
  project TEXT,                 -- associated project path
  content TEXT NOT NULL,        -- redacted raw content
  session_id TEXT,
  created_at INTEGER NOT NULL
);

-- Memory candidates (pending review)
CREATE TABLE memory_candidates (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  source TEXT NOT NULL,
  evidence_ids TEXT NOT NULL,   -- JSON array of event IDs
  confidence REAL NOT NULL,
  sensitivity TEXT NOT NULL,    -- 'low', 'normal', 'high'
  status TEXT NOT NULL,         -- 'pending', 'approved', 'rejected', 'edited'
  created_at INTEGER NOT NULL
);

-- Approved memories
CREATE TABLE memories (
  id TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  type TEXT NOT NULL,
  source TEXT NOT NULL,
  evidence_ids TEXT NOT NULL,
  confidence REAL NOT NULL,
  sensitivity TEXT NOT NULL,
  approved_at INTEGER NOT NULL,
  edited_by_user INTEGER DEFAULT 0,
  created_at INTEGER NOT NULL
);
```

---

## Pattern Extractor Rules

Runs on deterministic scripts only (no LLM at this stage).

1. **Command frequency**: If same command or sequence appears 3+ times in same project → candidate
2. **Error-fix pair**: If error follows command, then new command with success → candidate for fix
3. **Project context**: Read package.json, .git, directory name → project memory
4. **Session classification**: If session goal set as "learn X" → tag all events as learning
5. **Sequence detection**: If command A always precedes command B → sequence memory

---

## Related Files
- [Learning Flow](learning-flow.md)
- [Learning Ledger Flow](learning-ledger-flow.md)
- [Memory Governance Flow](memory-governance-flow.md)
- [Workflow Memory Feature](../features/02-workflow-memory/README.md)
