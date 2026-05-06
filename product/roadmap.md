# Roadmap

**Current Stage:** Stage 0 — Concept Validated  
**Platform:** Linux-first

---

## Stage 0 — Product Definition
**Status:** Complete

Goals:
- Define AgentOS Continuum and Stareha
- Define product principles
- Define learning and workflow use cases
- Define Linux-first approach
- Define Learning Ledger as core trust layer

Deliverables:
- [x] Product vision report
- [x] Roadmap
- [x] Architecture plan
- [x] Naming and positioning
- [x] MVP definition
- [x] Documentation structure (this project)

---

## Stage 1 — Linux Local Runtime
**Status:** Complete

Goal: Build the basic local runtime.

Features:
- [x] `stareha start` / `stop` / `status` / `restart`
- [x] `stareha init` — first-run wizard
- [x] `stareha session start/stop/status`
- [x] `stareha memory inbox/stats`
- [x] `stareha permissions list/add`
- [x] Linux daemon (systemd user service)
- [x] SQLite event store with full schema (events, sessions, memories, memory_candidates, meta)
- [x] Filesystem watcher (inotify-simple, permission-gated)
- [x] Terminal history scanner (zsh/bash, dedup, redaction)
- [x] Live terminal hook receiver (HTTP on port 7431, shell hook for ~/.zshrc)
- [x] Redaction layer (always-on, covers API keys, tokens, env vars, JWTs, DB connstrings)
- [x] Permission system (opt-in per source, `can_collect()` gating everywhere)
- [x] Local-only storage

Success:
```
Stareha can run locally and observe approved events.
```

Acceptance test passed: `stareha status` shows daemon + event count growing from terminal history.

Relevant docs:
- [Daemon & Runtime](../features/07-daemon-runtime/README.md)
- [Linux Daemon](../features/07-daemon-runtime/linux-daemon.md)

---

## Stage 2 — Workflow Memory

Goal: Turn local activity into useful memories.

Features:
- Terminal command pattern learning
- Project association
- Work session tracking
- Learning session tracking
- Memory candidates
- Memory Inbox
- Memory approval/rejection

Success:
```
Stareha can learn useful workflow patterns and show them to the user.
```

Relevant docs:
- [Workflow Memory](../features/02-workflow-memory/README.md)
- [Memory Governance](../features/06-memory-governance/README.md)

---

## Stage 3 — Learning Ledger

Goal: Make learning transparent and controllable.

Features:
- Learning runs with full provenance
- `stareha memory why <id>`
- `stareha what-did-you-learn today`
- Memory feedback (approve/reject/edit)
- Confidence/sensitivity scoring

Success:
```
The user can inspect, control, and improve what Stareha learns.
```

Relevant docs:
- [Learning Ledger](../features/03-learning-ledger/README.md)

---

## Stage 4 — Prepared Guidance

Goal: Make Stareha proactive and mentor-like.

Features:
- Daily/next-session preparation
- Quiz generation
- Exercise generation
- Weak concept detection
- Next-step recommendations
- Work task preparation

Success:
```
When the user returns, Stareha has prepared useful personalized guidance.
```

Relevant docs:
- [Prepared Guidance](../features/04-prepared-guidance/README.md)

---

## Stage 5 — Local LLM Integration

Goal: Use local intelligence for private learning.

Features:
- Ollama or llama.cpp integration
- Local summarization
- Local quiz/exercise drafts
- Local memory compression
- Cloud fallback only when needed

Success:
```
Stareha can learn and prepare mostly without sending raw context online.
```

Relevant docs:
- [Local Intelligence](../features/05-local-intelligence/README.md)
- [Local LLM](../features/05-local-intelligence/local-llm.md)

---

## Stage 6 — Desktop Companion

Goal: Make Stareha feel present.

Features:
- Tray/sidebar app
- Suggestions panel
- Memory Inbox UI
- Learning Ledger UI
- Start/pause learning modes
- Daily briefing

Success:
```
Stareha feels like a companion, not just a CLI command.
```

Relevant docs:
- [Desktop UI](../features/09-interfaces/desktop-ui.md)

---

## Stage 7 — Browser Extension

Goal: Connect research and learning from the browser.

Features:
- "Remember this page"
- Start research session
- Summarize current tab
- Track learning resources
- Send browser summaries to memory

Success:
```
Stareha understands what the user researches and connects it to goals.
```

Relevant docs:
- [Browser Extension](../features/09-interfaces/browser-extension.md)
- [Browser Memory](../features/02-workflow-memory/browser-memory.md)

---

## Stage 8 — Cloud Memory

Goal: Optional cross-device continuity.

Features:
- Account/device identity
- Encrypted sync
- Summary-only sync (never raw data)
- Memory export/delete
- Multi-device retrieval

Success:
```
Useful memories can follow the user across devices.
```

---

## Stage 9 — Android App

Goal: Bring Stareha to mobile.

Features:
- Share to Stareha
- Voice notes
- Learning reminders
- Mobile memory search
- Manual screenshot memory

Success:
```
Stareha can help the user continue learning across laptop and phone.
```

Relevant docs:
- [Android App](../features/09-interfaces/android-app.md)

---

## Stage 10 — End Goal

Full personal companion layer.

Stareha:
- Understands user goals
- Remembers workflows
- Tracks learning progress
- Prepares lessons and exercises
- Prepares work sessions
- Suggests next actions
- Helps debug repeated errors
- Summarizes days
- Resumes previous context
- Learns from feedback
- Uses local intelligence by default
- Works across desktop, terminal, browser, and mobile
- Syncs useful memories safely
- Lets users inspect and control everything it knows
