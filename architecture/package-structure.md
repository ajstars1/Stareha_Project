# Package Structure

**Status:** Defined  
**Stage:** 0

---

## Monorepo Layout

```
stareha/
├── apps/
│   ├── cli/                    # stareha CLI binary
│   ├── daemon/                 # Linux daemon service
│   ├── desktop/                # Tauri desktop app (Stage 6)
│   ├── browser-extension/      # Browser extension (Stage 7)
│   └── android/                # Android app (Stage 9)
│
├── packages/
│   ├── core/                   # Shared types, DB schema, config
│   ├── collectors/             # Event collectors (terminal, files, claude-code, browser)
│   ├── intelligence/           # Scripts layer, local LLM, cloud LLM wrappers
│   ├── memory/                 # Workflow memory + learning ledger
│   ├── guidance/               # Prepared guidance engine
│   ├── permissions/            # Permission system
│   └── shared/                 # Utilities, logging, constants
│
└── docs/                       # (Stareha_Project/ — this folder)
    └── ... (this documentation workspace)
```

---

## Package Responsibilities

### `packages/core`
- SQLite schema definitions
- Shared TypeScript types (Event, Memory, Candidate, etc.)
- Config loader
- Logging utilities

### `packages/collectors`
- Shell hook event receiver (HTTP server, port 7431)
- inotify file watcher
- Claude Code history importer
- Browser extension event receiver (HTTP server, port 7432)
- App usage monitor

### `packages/intelligence`
- `scripts/` — pattern extractor, redactor, scorer, deduplicator
- `local-llm/` — Ollama client, prompt templates, task routing
- `cloud-llm/` — Anthropic SDK client, context builder, usage tracker

### `packages/memory`
- Event store writes/reads
- Memory candidate creation
- Learning ledger (provenance tracking)
- Memory inbox management
- Approved memory retrieval

### `packages/guidance`
- Session end trigger handler
- Gap analyzer (weak concept detection)
- Quiz generator
- Exercise generator
- Session briefing formatter
- Work task prep

### `packages/permissions`
- Permission file reader/writer
- Permission check functions
- Action approval flow

### `apps/cli`
- All `stareha` commands
- Talks to daemon via IPC or direct package imports
- Formatted terminal output

### `apps/daemon`
- Systemd service entry point
- Event loop
- Scheduler
- Orchestrates all packages

---

## Language Decision

Two options:

**Option A: Python**
- Fast to iterate
- Rich ecosystem (inotify, SQLite, Ollama client)
- Easy regex and pattern matching
- Slower startup (acceptable for daemon)

**Option B: Rust**
- Native Linux performance
- Small binary
- Harder to iterate quickly
- Best for Stage 3+ when product is stable

**Recommendation: Python for MVP, evaluate Rust for daemon at Stage 3.**

---

## DB Schema Location

All migrations in: `packages/core/db/migrations/`

Schema: `packages/core/db/schema.sql`

---

## Config Location

User config: `~/.stareha/config.json`

App defaults: `packages/core/config.defaults.json`

---

## Related Files
- [System Architecture](system-architecture.md)
- [Data Flow](data-flow.md)
