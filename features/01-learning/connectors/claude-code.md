# Connector: Claude Code

**Status:** Concept  
**Stage:** 2  
**Permission required:** `claude_code:read`

---

## What It Is

The Claude Code connector reads from Claude Code's local session history to learn what the user was building, debugging, and deciding with AI assistance.

This is one of the highest-signal connectors — Claude Code sessions contain explicit decisions, bug descriptions, plans, and task states.

---

## Why It Matters

When a developer uses Claude Code, they:
- Describe bugs they're fixing
- Make architectural decisions
- Set up tasks and plans
- Discuss files and functions
- Get stuck and ask for help

This is the richest source of intent and context. Stareha should understand it.

---

## What It Reads

### 1. Chat History (`.claude/conversations/`)
Claude Code stores conversation history locally. The connector reads completed sessions.

Extracts:
- What the user asked Claude to do
- Bugs being fixed (described in conversation)
- Files discussed
- Decisions made
- Plans generated
- Errors encountered
- Open/pending tasks

Example memory from chat history:
```
Ayush decided AgentOS Continuum should use local scripts/local LLM first,
and cloud LLM only when needed.
Source: claude_code conversation on 2026-05-01
```

### 2. CLAUDE.md Files
Claude Code reads `CLAUDE.md` files in project directories. The connector reads these to understand project context, rules, and current focus.

Extracts:
- Project identity and stack
- Code rules and conventions
- Active project context (from `/notes/` references)
- Current goals if documented

Example memory from CLAUDE.md:
```
AgentOS project uses TypeScript strict mode, Supabase + Prisma, Next.js 14+.
Source: CLAUDE.md at ~/projects/agent-os
```

### 3. Memory Files (`.claude/projects/*/memory/`)
Claude Code's auto-memory system stores structured memories. The connector reads these as high-confidence context.

Extracts:
- User role and expertise
- Project goals and context
- Known preferences
- Past decisions

### 4. Session Task Lists
If Claude Code creates task lists during sessions, the connector extracts incomplete tasks.

Example memory:
```
Open task from last Claude Code session:
- Wire up memory_candidates table to the inbox CLI command
Source: claude_code task on 2026-05-04
```

---

## How It Works

```
On stareha session stop (or scheduled collection):
  ↓
Read ~/.claude/projects/ directory
  ↓
Find sessions newer than last_collected_at
  ↓
For each session:
  - Read conversation JSON
  - Extract decisions, bugs, tasks, files mentioned
  - Read associated CLAUDE.md if project found
  - Redact: strip any API keys, tokens, private data
  ↓
Generate events:
  - type: 'claude_code_decision'
  - type: 'claude_code_task'
  - type: 'claude_code_bug'
  - type: 'claude_code_context'
  ↓
Send to event store
```

---

## Redaction Rules

Before any event is stored:
- Strip API keys (regex: `sk-...`, `ghp_...`, etc.)
- Strip passwords mentioned in conversation
- Strip full file contents if accidentally pasted
- Keep: decisions, bug descriptions, task names, file names

---

## Data Location (Linux)

| Data type | Location |
|-----------|----------|
| Conversation history | `~/.claude/projects/*/conversations/` |
| Auto-memory | `~/.claude/projects/*/memory/` |
| Project CLAUDE.md | `<project-root>/CLAUDE.md` |
| Settings | `~/.claude/settings.json` |

---

## Example Events Generated

```json
{
  "type": "claude_code_decision",
  "source": "claude_code",
  "project": "agent-os",
  "content": "Decided to use SQLite for local event store — simpler than PostgreSQL for local-first",
  "session_date": "2026-05-01",
  "confidence": 0.91
}
```

```json
{
  "type": "claude_code_task",
  "source": "claude_code",
  "project": "stareha",
  "content": "TODO: Wire up memory_candidates table to inbox CLI command",
  "status": "open",
  "session_date": "2026-05-04"
}
```

---

## Sub-Topics (Each Deeply Important)

### Chat History
The raw conversation log. Highest signal, most complex to parse.
- Session format: JSONL or structured JSON
- Extract turns where user asks questions or makes decisions
- Identify "we decided..." / "let's use..." / "the bug is..." patterns

### CLAUDE.md
The project rules file. Static, high-confidence context.
- Read on connector init and on file change
- Parse identity, stack, rules sections
- Associate with project directory

### Memory Files
Claude Code's auto-memory. Already structured.
- Read as-is, map to Stareha memory format
- Confidence: inherit from Claude Code memory confidence

### Task Lists
Incomplete tasks from sessions.
- Track as open work items
- Surface in work session briefings
- Mark complete when user reports completion

---

## Related Files
- [Connectors Overview](README.md)
- [Claude Code Memory](../../02-workflow-memory/claude-code-memory.md)
- [Learning Ledger Flow](../../../_flows/learning-ledger-flow.md)
- [Permission Flow](../../../_flows/permission-flow.md)
