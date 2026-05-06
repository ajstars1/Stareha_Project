# Terminal Memory

**Status:** Concept  
**Stage:** 2

---

## What It Is

Terminal memory stores learned patterns from shell command history: sequences, habits, error-fix pairs, and project-specific workflows.

---

## Why It Matters

The terminal is where developer workflows live. Repeated command patterns tell Stareha:
- How the user builds and tests their projects
- What errors they encounter regularly
- What fixes actually work
- What their project setup routine looks like

---

## Memory Categories

### Command Sequences
Commands that consistently appear in order.

Example:
```
Memory: "In AgentOS, you run npm run build before npm test."
Evidence: Sequence observed 8 times
Confidence: 0.84
```

### Project-Specific Habits
Commands that appear only in a specific project.

Example:
```
Memory: "In agent-os, you start the dev server with pnpm dev."
Evidence: 12 occurrences in ~/projects/agent-os
Confidence: 0.91
```

### Error-Fix Pairs
A failed command followed by a successful resolution.

Example:
```
Memory: "npm cache clean --force fixes module installation errors in agent-os."
Evidence: Error→fix pair observed 3 times
Confidence: 0.78
```

### Setup Routines
Sequences that appear when setting up a new project or environment.

Example:
```
Memory: "Project setup: git clone → npm install → cp .env.example .env → npm run dev"
Evidence: Observed in 4 different projects
Confidence: 0.71
```

---

## How It's Stored

Each terminal memory includes:
- `content`: human-readable memory text
- `project`: associated project path
- `evidence_ids`: list of event IDs from ledger
- `evidence_count`: how many times observed
- `confidence`: 0.0–1.0 score
- `last_seen`: most recent occurrence
- `source`: "terminal"

---

## How It's Used

| Consumer | Use |
|----------|-----|
| Session briefing | "You usually run X next" |
| Prepared guidance | "You have this error pattern — here's the fix" |
| Work task prep | Suggest next command in workflow |
| Session summary | List commands run today |

---

## Related Files
- [Workflow Memory](README.md)
- [Terminal Connector](../01-learning/connectors/terminal.md)
- [Workflow Memory Flow](../../_flows/workflow-memory-flow.md)
