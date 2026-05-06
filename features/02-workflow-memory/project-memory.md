# Project Memory

**Status:** Concept  
**Stage:** 2

---

## What It Is

Project memory stores what Stareha knows about each project the user works on — the stack, structure, active focus, common files, build tools, and open work items.

---

## Why It Matters

When a user switches back to a project after a week away, Stareha can immediately brief them on:
- What they were working on
- The project stack and tools
- Where they left off
- What the next task is

---

## Memory Categories

### Project Context
Basic facts about the project detected from files.

Example:
```
Memory: "AgentOS Continuum is a TypeScript monorepo with packages: core, cli, daemon, ui."
Source: package.json, tsconfig.json, directory structure
Confidence: 0.95
```

### Active Focus
What part of the project is currently being worked on.

Example:
```
Memory: "Current focus in agent-os: memory candidate pipeline in packages/core/src/memory.ts"
Source: file_watcher (most edited file in last 5 sessions)
Confidence: 0.82
```

### Build Tools & Workflows
How the project is built, tested, and deployed.

Example:
```
Memory: "AgentOS build: pnpm build → pnpm test → pnpm lint"
Source: terminal + package.json scripts
Confidence: 0.88
```

### Open Work Items
Incomplete tasks or open issues noted in sessions.

Example:
```
Memory: "Open: Wire up memory_candidates table to CLI inbox command"
Source: claude_code conversation on 2026-05-04
Status: open
```

---

## How Projects Are Detected

1. `.git` directory presence → project root
2. `package.json` name field → project name
3. `pyproject.toml` / `Cargo.toml` / `go.mod` → language/stack
4. Directory structure analysis → monorepo vs single app

---

## Project Memory Schema

```json
{
  "id": "project_agent-os",
  "name": "agent-os",
  "path": "~/projects/agent-os",
  "stack": ["TypeScript", "Node.js", "SQLite", "pnpm"],
  "structure": "monorepo",
  "packages": ["core", "cli", "daemon", "ui"],
  "build_commands": ["pnpm build", "pnpm test"],
  "active_focus": "packages/core/src/memory.ts",
  "last_active": "2026-05-06",
  "session_count": 23,
  "open_tasks": ["Wire up memory_candidates to CLI"]
}
```

---

## Related Files
- [Workflow Memory](README.md)
- [File Watcher Connector](../01-learning/connectors/file-watcher.md)
- [Claude Code Memory](claude-code-memory.md)
- [Work Task Prep](../04-prepared-guidance/work-task-prep.md)
