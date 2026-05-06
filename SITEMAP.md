# Stareha Project — Sitemap

> This is the master navigation for the entire Stareha / AgentOS Continuum project.
> Every file must appear here. Update this whenever you add or remove a file.

---

## Root

| File | What it covers |
|------|---------------|
| [README.md](README.md) | Project overview, installation, command reference, contributing |
| [LICENSE](LICENSE) | MIT license |
| [CLAUDE.md](CLAUDE.md) | AI assistant rules — documentation law, practices, skills map |
| [SITEMAP.md](SITEMAP.md) | This file — master navigation |
| [.gitignore](.gitignore) | Ignores runtime data (databases, bytecode, secrets) |

---

## Source Code (`src/`)

### Entry points

| File | What it covers |
|------|---------------|
| [src/pyproject.toml](src/pyproject.toml) | Package config, dependencies, scripts (`stareha` CLI entry point) |
| [src/apps/cli/main.py](src/apps/cli/main.py) | `stareha` CLI — all commands built with Click + Rich |
| [src/apps/daemon/main.py](src/apps/daemon/main.py) | Background daemon — starts collectors, manages threads |
| [src/apps/daemon/stareha.service](src/apps/daemon/stareha.service) | systemd user service template |

### Core packages

| File | What it covers |
|------|---------------|
| [src/packages/core/config/\_\_init\_\_.py](src/packages/core/config/__init__.py) | Config loader — `~/.stareha/config.json` with defaults |
| [src/packages/core/db/\_\_init\_\_.py](src/packages/core/db/__init__.py) | SQLite store — write_event, sessions, meta, migrations |
| [src/packages/core/db/schema.sql](src/packages/core/db/schema.sql) | Canonical schema — events, sessions, memories, candidates, ledger |

### Collectors

| File | What it covers |
|------|---------------|
| [src/packages/collectors/terminal/history\_scanner.py](src/packages/collectors/terminal/history_scanner.py) | Scans `~/.zsh_history` / `~/.bash_history` on daemon start |
| [src/packages/collectors/terminal/hook\_receiver.py](src/packages/collectors/terminal/hook_receiver.py) | HTTP server on port 7431 — receives live shell hook events |
| [src/packages/collectors/files/watcher.py](src/packages/collectors/files/watcher.py) | inotify-based file watcher — fires `file_edit` events |

### Intelligence

| File | What it covers |
|------|---------------|
| [src/packages/intelligence/scripts/pattern\_extractor.py](src/packages/intelligence/scripts/pattern_extractor.py) | Deterministic extractors — frequency, sequences, error-fix, project context |
| [src/packages/intelligence/learning\_runner.py](src/packages/intelligence/learning_runner.py) | Orchestrates extraction — dedup, feedback gate, writes candidates |
| [src/packages/intelligence/ledger.py](src/packages/intelligence/ledger.py) | Learning run tracking — `what_did_you_learn`, feedback stats |
| [src/packages/intelligence/router.py](src/packages/intelligence/router.py) | **Policy router** — scripts → local LLM → cloud LLM |
| [src/packages/intelligence/local\_llm/\_\_init\_\_.py](src/packages/intelligence/local_llm/__init__.py) | Ollama HTTP client — generate, chat, pull, is_available |
| [src/packages/intelligence/cloud\_llm/\_\_init\_\_.py](src/packages/intelligence/cloud_llm/__init__.py) | Claude API client — generate, chat, is_available |
| [src/packages/intelligence/prompts.py](src/packages/intelligence/prompts.py) | Prompt template manager — bundled defaults + user-editable |
| [src/packages/intelligence/summarizer.py](src/packages/intelligence/summarizer.py) | Session summary + memory enrichment via router |

### Memory

| File | What it covers |
|------|---------------|
| [src/packages/memory/manager.py](src/packages/memory/manager.py) | approve, reject, forget, why, list, search, sources — all memory ops |

### Guidance

| File | What it covers |
|------|---------------|
| [src/packages/guidance/detector.py](src/packages/guidance/detector.py) | Weak concept detection — notes, error-fix, failures, session goals |
| [src/packages/guidance/briefing.py](src/packages/guidance/briefing.py) | Work + learning briefing builder (deterministic) |
| [src/packages/guidance/quiz.py](src/packages/guidance/quiz.py) | Quiz generation via router + interactive CLI runner |
| [src/packages/guidance/prep.py](src/packages/guidance/prep.py) | Guidance orchestrator — prep, store, deliver |

### Shared

| File | What it covers |
|------|---------------|
| [src/packages/shared/redact.py](src/packages/shared/redact.py) | Secret/token redaction — runs before any event is stored |
| [src/packages/shared/retry.py](src/packages/shared/retry.py) | Jittered exponential backoff for external calls |
| [src/packages/permissions/\_\_init\_\_.py](src/packages/permissions/__init__.py) | Opt-in source permissions — `can_collect()` gates all collectors |
| [src/packages/notification/\_\_init\_\_.py](src/packages/notification/__init__.py) | Desktop notifications via notify-send |

---

## Project Skills

| File | What it covers |
|------|---------------|
| [.claude/skills/stareha-doc-sync/SKILL.md](.claude/skills/stareha-doc-sync/SKILL.md) | End-of-session doc sync check — run every session |
| [.claude/skills/stareha-stage-check/SKILL.md](.claude/skills/stareha-stage-check/SKILL.md) | Stage readiness gate before advancing to next stage |

> gstack skills (globally installed): `/office-hours`, `/plan-eng-review`, `/investigate`, `/review`, `/ship`, `/document-release`, `/careful`, `/freeze`, `/autoplan` — see CLAUDE.md for when to use each.

---

## Product

| File | What it covers |
|------|---------------|
| [product/vision.md](product/vision.md) | Core vision, mission, main promise, end-goal |
| [product/principles.md](product/principles.md) | The 7 product principles (privacy, provenance, local-first, etc.) |
| [product/roadmap.md](product/roadmap.md) | Stage 0–10 roadmap with goals, features, success criteria |
| [product/mvp.md](product/mvp.md) | MVP scope, features, demo script |
| [product/naming.md](product/naming.md) | AgentOS Continuum vs Stareha — naming and relationship |
| [product/differentiators.md](product/differentiators.md) | Why Stareha vs ChatGPT, Cursor, browser history, courses |
| [product/stage-1-build-order.md](product/stage-1-build-order.md) | **Stage 1 step-by-step build order** — exact files, sequence, acceptance tests |

---

## Architecture

| File | What it covers |
|------|---------------|
| [architecture/system-architecture.md](architecture/system-architecture.md) | Full system map — all layers and components |
| [architecture/package-structure.md](architecture/package-structure.md) | Monorepo package layout |
| [architecture/data-flow.md](architecture/data-flow.md) | How data moves from raw event → memory → suggestion |

---

## Flows (Master Logic Files)

> These are the single source of truth for how each system works.
> Read before implementing. Update when logic changes.

| File | What it covers |
|------|---------------|
| [_flows/learning-flow.md](_flows/learning-flow.md) | End-to-end: how Stareha learns from user activity |
| [_flows/workflow-memory-flow.md](_flows/workflow-memory-flow.md) | How raw events become durable workflow memories |
| [_flows/learning-ledger-flow.md](_flows/learning-ledger-flow.md) | The full ledger pipeline: event → provenance → memory |
| [_flows/prepared-guidance-flow.md](_flows/prepared-guidance-flow.md) | How Stareha prepares next-session guidance |
| [_flows/intelligence-policy-flow.md](_flows/intelligence-policy-flow.md) | Scripts → Local LLM → Cloud LLM decision logic |
| [_flows/memory-governance-flow.md](_flows/memory-governance-flow.md) | Memory inbox → approve/reject/edit → feedback loop |
| [_flows/permission-flow.md](_flows/permission-flow.md) | How permissions are requested, granted, and revoked |

---

## Features

### 01 — Learning

| File | What it covers |
|------|---------------|
| [features/01-learning/README.md](features/01-learning/README.md) | Learning feature overview and sub-feature index |
| [features/01-learning/learning-from-work.md](features/01-learning/learning-from-work.md) | How Stareha learns from actual user work sessions |
| [features/01-learning/learning-profile.md](features/01-learning/learning-profile.md) | What a learning profile contains and how it's built |
| [features/01-learning/connectors/README.md](features/01-learning/connectors/README.md) | All connectors overview — what connects, how, why |
| [features/01-learning/connectors/claude-code.md](features/01-learning/connectors/claude-code.md) | Claude Code connector — chat history, CLAUDE.md, session import |
| [features/01-learning/connectors/terminal.md](features/01-learning/connectors/terminal.md) | Terminal/shell history connector |
| [features/01-learning/connectors/browser.md](features/01-learning/connectors/browser.md) | Browser research connector |
| [features/01-learning/connectors/file-watcher.md](features/01-learning/connectors/file-watcher.md) | File system watcher connector |

### 02 — Workflow Memory

| File | What it covers |
|------|---------------|
| [features/02-workflow-memory/README.md](features/02-workflow-memory/README.md) | Workflow memory overview — types, storage, retrieval |
| [features/02-workflow-memory/terminal-memory.md](features/02-workflow-memory/terminal-memory.md) | Command patterns, project-specific habits |
| [features/02-workflow-memory/project-memory.md](features/02-workflow-memory/project-memory.md) | File activity, build tools, project structure |
| [features/02-workflow-memory/browser-memory.md](features/02-workflow-memory/browser-memory.md) | Research sessions, learning topics, docs used |
| [features/02-workflow-memory/claude-code-memory.md](features/02-workflow-memory/claude-code-memory.md) | Decisions, bugs fixed, open tasks from AI sessions |
| [features/02-workflow-memory/app-usage-memory.md](features/02-workflow-memory/app-usage-memory.md) | App combinations, time-of-day patterns |

### 03 — Learning Ledger

| File | What it covers |
|------|---------------|
| [features/03-learning-ledger/README.md](features/03-learning-ledger/README.md) | The trust layer — what it is, why it's non-negotiable |
| [features/03-learning-ledger/provenance.md](features/03-learning-ledger/provenance.md) | No memory without provenance — provenance data model |
| [features/03-learning-ledger/pipeline.md](features/03-learning-ledger/pipeline.md) | Raw event → redaction → classification → memory candidate |
| [features/03-learning-ledger/memory-inbox.md](features/03-learning-ledger/memory-inbox.md) | Memory inbox UI/CLI — approve, reject, edit, why |
| [features/03-learning-ledger/feedback-loop.md](features/03-learning-ledger/feedback-loop.md) | How user feedback improves future learning |

### 04 — Prepared Guidance

| File | What it covers |
|------|---------------|
| [features/04-prepared-guidance/README.md](features/04-prepared-guidance/README.md) | Proactive guidance — what it is, when it triggers |
| [features/04-prepared-guidance/weak-concept-detection.md](features/04-prepared-guidance/weak-concept-detection.md) | How weak areas are identified from learning data |
| [features/04-prepared-guidance/quiz-generation.md](features/04-prepared-guidance/quiz-generation.md) | Quiz generation from learning profile + weak concepts |
| [features/04-prepared-guidance/exercise-generation.md](features/04-prepared-guidance/exercise-generation.md) | Mini-project and coding exercise generation |
| [features/04-prepared-guidance/session-briefing.md](features/04-prepared-guidance/session-briefing.md) | The next-session briefing format and delivery |
| [features/04-prepared-guidance/work-task-prep.md](features/04-prepared-guidance/work-task-prep.md) | Work context: task summaries, next steps, bug plans |

### 05 — Local Intelligence

| File | What it covers |
|------|---------------|
| [features/05-local-intelligence/README.md](features/05-local-intelligence/README.md) | Intelligence policy — 3 layers, decision rules |
| [features/05-local-intelligence/scripts-layer.md](features/05-local-intelligence/scripts-layer.md) | Deterministic scripts — what they do, when they run |
| [features/05-local-intelligence/local-llm.md](features/05-local-intelligence/local-llm.md) | Local LLM (Ollama) — tasks, models, privacy guarantee |
| [features/05-local-intelligence/cloud-llm.md](features/05-local-intelligence/cloud-llm.md) | Cloud LLM — when allowed, what context is sent, policy |
| [features/05-local-intelligence/redaction.md](features/05-local-intelligence/redaction.md) | Secret/sensitive data redaction before any processing |

### 06 — Memory Governance

| File | What it covers |
|------|---------------|
| [features/06-memory-governance/README.md](features/06-memory-governance/README.md) | Full memory control system — user owns their data |
| [features/06-memory-governance/memory-commands.md](features/06-memory-governance/memory-commands.md) | All `stareha memory` CLI commands and outputs |
| [features/06-memory-governance/memory-why.md](features/06-memory-governance/memory-why.md) | The `memory why` command — most important trust feature |

### 07 — Daemon & Runtime

| File | What it covers |
|------|---------------|
| [features/07-daemon-runtime/README.md](features/07-daemon-runtime/README.md) | Linux daemon overview — systemd, lifecycle, responsibilities |
| [features/07-daemon-runtime/linux-daemon.md](features/07-daemon-runtime/linux-daemon.md) | Systemd service, start/stop/status, event loop |
| [features/07-daemon-runtime/event-collectors.md](features/07-daemon-runtime/event-collectors.md) | What gets collected, how, permission model |
| [features/07-daemon-runtime/scheduler.md](features/07-daemon-runtime/scheduler.md) | When learning runs, when guidance is prepared |

### 08 — Permission System

| File | What it covers |
|------|---------------|
| [features/08-permission-system/README.md](features/08-permission-system/README.md) | Permission model — opt-in sources, scope, revocation |
| [features/08-permission-system/source-permissions.md](features/08-permission-system/source-permissions.md) | Per-source permissions (terminal, browser, files, etc.) |
| [features/08-permission-system/action-permissions.md](features/08-permission-system/action-permissions.md) | Action permissions — what Stareha can do autonomously |

### 09 — Interfaces

| File | What it covers |
|------|---------------|
| [features/09-interfaces/README.md](features/09-interfaces/README.md) | All interface surfaces overview |
| [features/09-interfaces/cli.md](features/09-interfaces/cli.md) | CLI — all commands, MVP commands, command structure |
| [features/09-interfaces/desktop-ui.md](features/09-interfaces/desktop-ui.md) | Desktop tray/sidebar app — Stage 6 |
| [features/09-interfaces/browser-extension.md](features/09-interfaces/browser-extension.md) | Browser extension — Stage 7 |
| [features/09-interfaces/android-app.md](features/09-interfaces/android-app.md) | Android app — Stage 9 |

---

## Dependency Map

```
product/vision.md
  └── product/principles.md
  └── product/roadmap.md
        └── product/mvp.md

architecture/system-architecture.md
  └── architecture/package-structure.md
  └── architecture/data-flow.md

features/01-learning/
  └── connectors/ → feeds → features/02-workflow-memory/
  └── learning-profile → feeds → features/04-prepared-guidance/

features/02-workflow-memory/
  └── feeds → features/03-learning-ledger/

features/03-learning-ledger/
  └── pipeline.md → uses → features/05-local-intelligence/
  └── memory-inbox.md → uses → features/06-memory-governance/

features/04-prepared-guidance/
  └── weak-concept-detection → reads → features/03-learning-ledger/
  └── quiz/exercise generation → uses → features/05-local-intelligence/

features/07-daemon-runtime/
  └── event-collectors → sends to → features/02-workflow-memory/
  └── scheduler → triggers → features/04-prepared-guidance/

features/08-permission-system/
  └── gates → features/07-daemon-runtime/event-collectors
  └── gates → features/05-local-intelligence/cloud-llm
```
