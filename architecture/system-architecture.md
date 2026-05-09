# System Architecture

**Status:** Updated
**Stage:** 5.5

---

## Full System Map

```
AgentOS Continuum
│
├── Stareha Companion (user-facing identity)
│   ├── Stareha Learn beginner loop
│   │   ├── setup
│   │   ├── learn
│   │   ├── note
│   │   ├── done / Learning Card
│   │   └── continue
│   ├── Chat / talking mode (local LLM first, cloud only with --cloud)
│   ├── Mentor mode (learning guidance)
│   └── Work companion mode (developer briefings)
│
├── Local Runtime (daemon)
│   ├── Linux daemon (systemd user service)
│   ├── Event collectors
│   │   ├── Shell hook receiver (port 7431)
│   │   ├── inotify file watcher
│   │   ├── Claude Code importer
│   │   ├── Browser endpoint (port 7432)
│   │   └── App usage monitor
│   ├── Scheduler (session end, nightly, idle)
│   └── Notification engine (CLI, tray)
│
├── Workflow Memory
│   ├── Terminal memory (command patterns, error-fix)
│   ├── Project memory (stack, focus, open tasks)
│   ├── Browser/research memory
│   ├── Claude Code memory (decisions, bugs, tasks)
│   ├── App usage memory
│   └── Learning profile
│
├── Experience Layer
│   ├── Mode presets
│   ├── Active project resolver
│   ├── Project registry
│   ├── Learning Card builder
│   ├── Beginner review flow
│   ├── Continue plan builder
│   └── Home screen
│
├── Learning Ledger (trust layer)
│   ├── Raw event log (ledger_events — immutable)
│   ├── Learning runs log
│   ├── Memory candidates (inbox)
│   ├── Memory provenance (every memory has a trail)
│   ├── User feedback log
│   └── Improvement signal log
│
├── Local Intelligence
│   ├── Layer 1: Deterministic scripts
│   │   ├── Pattern extractor
│   │   ├── Redaction engine
│   │   ├── Importance scorer
│   │   └── Deduplicator
│   ├── Layer 2: Local LLM (Ollama)
│   │   ├── Summarization
│   │   ├── Quiz drafts
│   │   └── Memory candidate generation
│   └── Layer 3: Cloud LLM (Claude)
│       ├── Talking mode
│       ├── Exercise generation
│       └── High-quality explanations
│
├── Permission System
│   ├── Source permissions (opt-in per source)
│   ├── Action permissions (per-action approval)
│   └── Permission store (permissions.json)
│
└── Interfaces
    ├── CLI (stareha commands) — Stage 1
    ├── Desktop UI (tray + panel) — Stage 6
    ├── Browser Extension — Stage 7
    └── Android App — Stage 9
```

---

## Data Flow (High Level)

```
User activity
  ↓
[Permission check]
  ↓
Event collector (per source)
  ↓
[Redaction]
  ↓
Event store (SQLite, local only)
  ↓
Pattern extractor (scripts)
  ↓
Local LLM (optional, Stage 5)
  ↓
Memory candidates → inbox
  ↓
User approves → approved memories
  ↓
Prepared guidance engine
  ↓
Experience layer
  ↓
Learning Card / continue plan / briefing delivered
```

---

## Data Locality Principles

| Data type | Stored where | Leaves device when |
|-----------|-------------|-------------------|
| Raw events | Local SQLite only | Never |
| Memory candidates | Local SQLite only | Never |
| Approved memories | Local SQLite | Only if cloud sync enabled (Stage 8) |
| Learning profile | Local JSON | Summary sent to cloud LLM with permission |
| Prepared guidance | Local filesystem | Never |
| Cloud LLM prompts | Never stored | Sent as summary-only context |

---

## Technology Stack (Proposed)

| Layer | Technology | Reason |
|-------|-----------|--------|
| Daemon | Python or Rust | Linux-native, systemd compatible |
| Event store | SQLite | Simple, file-based, no server needed |
| Pattern extractor | Python | Easy regex, fast iteration |
| Local LLM | Ollama | Easy setup, model flexibility |
| Cloud LLM | Anthropic Claude API | Explicit opt-in for talking mode and cloud-enabled tasks |
| CLI | Python Click or Rust Clap | Fast, composable |
| Desktop UI | Tauri | Lightweight, Rust-backed |
| Browser Extension | Web Extensions API | Cross-browser |
| Android | Flutter or React Native | Cross-platform |

---

## Related Files
- [Package Structure](package-structure.md)
- [Data Flow](data-flow.md)
- [Product Vision](../product/vision.md)
