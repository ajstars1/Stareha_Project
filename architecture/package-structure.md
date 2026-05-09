# Package Structure

**Status:** Updated
**Stage:** 5.5

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
│   ├── experience/             # Beginner product flows above the engine
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

### `packages/experience`
- `mode_presets.py` — Learner, Companion, and Researcher presets
- `project_resolver.py` — active project detection without scanning whole workspaces
- `project_registry.py` — known project metadata stored in the existing meta table
- `learning_card.py` — session-end learner-facing artifact
- `review_flow.py` — beginner review language over memory candidates
- `continuation.py` — `stareha continue` plan builder
- `home.py` — no-argument `stareha` home screen

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
- Beginner flow: `setup`, home, `learn`, `note`, `done`, `continue`
- Advanced flow: daemon, session, memory, ledger, permissions, LLM tooling
- Talks to daemon via local HTTP or direct package imports
- Formatted terminal output

### `apps/daemon`
- Systemd service entry point
- Event loop
- Scheduler
- Orchestrates all packages

---

## Language Decision

**Locked: Python for Stage 1–4. Re-evaluate Rust at Stage 5.**

Reasons:
- hermes-agent and agent-os have production-ready Python code to copy directly (redact.py, shell_hooks.py, retry_utils.py, rate_limit_tracker.py, sqlite store)
- inotify, SQLite, Ollama, systemd — all first-class Python
- Fast iteration on MVP
- Rust if/when performance becomes a real problem (not before Stage 5)

**Package manager:** `uv` (fast, modern, replaces pip + venv)

**Python version:** 3.11+

**Key dependencies:**
- `better-sqlite3` → `sqlite3` (stdlib, no extra install)
- `inotify-simple` — file watching
- `httpx` — async HTTP (Ollama client, daemon HTTP server)
- `click` — CLI commands
- `pydantic` — config validation + type safety
- `rich` — terminal output formatting

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
