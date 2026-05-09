# Roadmap

**Current Stage:** Stage 5.5 complete — product wrapper built; Stage 6 next
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
- [x] Linux daemon (systemd user service + direct subprocess fallback — works without systemd)
- [x] SQLite event store with full schema (events, sessions, memories, memory_candidates, meta)
- [x] Filesystem watcher (inotify-simple, permission-gated)
- [x] Terminal history scanner (zsh/bash, dedup, redaction)
- [x] Live terminal hook receiver (HTTP on port 7431, shell hook for ~/.zshrc)
- [x] Claude Code connector — reads `~/.claude/projects/*.jsonl`, no extension needed
- [x] Browser connector — reads Chrome + Firefox SQLite history files directly, no extension needed
  - Chrome: `~/.config/google-chrome/Default/History` (copy + read to handle file lock)
  - Firefox: `~/.mozilla/firefox/*/places.sqlite`
  - Filters ad/tracking domains before storage
  - Extracts search queries from Chrome `keyword_search_terms` table
- [x] Redaction layer (always-on, covers API keys, tokens, env vars, JWTs, DB connstrings)
- [x] Permission system (opt-in per source, `can_collect()` gating everywhere)
- [x] `stareha init` auto-detects Chrome/Firefox/Claude Code and offers them as opt-in sources
- [x] Local-only storage

Success:
```
Stareha can run locally and observe approved events.
```

Acceptance test passed: `stareha status` shows daemon + event count growing from terminal, Claude Code (45 sessions), and Chrome (2302 visits) history.

Relevant docs:
- [Daemon & Runtime](../features/07-daemon-runtime/README.md)
- [Linux Daemon](../features/07-daemon-runtime/linux-daemon.md)

---

## Stage 2 — Workflow Memory
**Status:** Complete

Goal: Turn local activity into useful memories.

Features:
- [x] Pattern extractor (deterministic scripts, no LLM)
  - [x] Command frequency: commands run 3+ times in a project
  - [x] Command sequences: A → B pairs that consistently co-occur
  - [x] Error-fix pairs: failed_cmd → recovery_cmd within 15 minutes
  - [x] Project context: detect stack from package.json, pyproject.toml, go.mod
  - [x] Research topics: frequent domain visits + search queries from browser history
  - [x] Claude Code patterns: topics repeatedly discussed with Claude
- [x] Learning runner: `stareha learn` (manual) + triggered on session stop
- [x] Memory candidates written to inbox with confidence + sensitivity scoring
- [x] Full memory governance CLI
  - [x] `stareha memory inbox` — show pending + `--review` interactive mode
  - [x] `stareha memory approve/reject/edit <id>` — individual actions
  - [x] `stareha memory why <id>` — full provenance with evidence events
  - [x] `stareha memory sources <id>` — raw events that caused a memory
  - [x] `stareha memory list` — list approved with filters (project, type, source)
  - [x] `stareha memory search <query>` — FTS5 full-text search
  - [x] `stareha memory forget <id>` — hard delete with confirmation
  - [x] `stareha memory stats` — breakdown by source and type
- [x] Feedback loop: every approve/reject/edit writes to memory_feedback table
- [x] FTS5 index sync: memories_fts updated on approve and forget
- [x] Partial ID support: commands accept 8-char prefix, not just full UUID

Success:
```
Stareha can learn useful workflow patterns and show them to the user.
```

Acceptance test passed: `stareha learn --force` → `stareha memory inbox` → approve → `stareha memory why <id>` shows evidence trail.

Relevant docs:
- [Workflow Memory](../features/02-workflow-memory/README.md)
- [Memory Governance](../features/06-memory-governance/README.md)

---

## Stage 3 — Learning Ledger
**Status:** Complete

Goal: Make learning transparent and controllable.

Features:
- [x] `learning_runs` table — every run tracked (started, events processed, candidates, status)
- [x] `learning_run_id` on candidates and memories — full traceability
- [x] Feedback-gated confidence — 3 rejections → 75% bar, 6 → 85%, 10 → 95%
- [x] `stareha what-did-you-learn [today|yesterday|session|week]`
  - Events observed by source
  - Learning runs summary
  - All patterns found with confidence + status
  - Memories approved in period
  - Pending inbox count
- [x] `stareha ledger` — full audit view (runs, feedback stats, blocked pattern types)
- [x] `stareha status` updated — shows inbox pending count + approved memory count
- [x] Dedup improved — blocks both pending and approved to prevent re-surfacing accepted patterns
- [x] Schema migration — `_run_migrations()` adds new columns to existing DBs without data loss

Success:
```
The user can inspect, control, and improve what Stareha learns.
```

Acceptance test passed: `stareha what-did-you-learn yesterday` shows 92 events, 1 run, patterns with status; `stareha ledger` shows audit trail with feedback rates.

Relevant docs:
- [Learning Ledger](../features/03-learning-ledger/README.md)

---

## Stage 4 — Prepared Guidance
**Status:** Complete

Goal: Make Stareha proactive and mentor-like.

Features:
- [x] `packages/guidance/detector.py` — weak concept detection from 4 signal sources:
  - User notes ("struggling with X") — highest weight (0.95)
  - error_fix memories — known tool failures (0.35/occurrence)
  - Repeated exit-code failures on same command (0.20/failure)
  - Session goals ("learn X") — intent signal (0.10)
- [x] `packages/guidance/briefing.py` — deterministic work + learning briefing builder
  - Work: project context, command patterns, error patterns, recent commands, next steps
  - Learning: weak concepts with signals, strong concepts, suggested plan
- [x] `packages/guidance/quiz.py` — quiz generation + interactive terminal runner
  - Claude API (claude-haiku) when `ANTHROPIC_API_KEY` set
  - Template fallback always works (no API key needed)
  - Interactive runner: multiple choice (A/B/C/D) + short answer + scoring
- [x] `packages/guidance/prep.py` — orchestrator storing all guidance in `prepared_guidance` table
- [x] `prepared_guidance` table + `user_notes` table added to schema
- [x] `stareha prep [--quiz]` — generate briefing + optional quiz, display inline
- [x] `stareha brief` — show latest prepared briefing at any time
- [x] `stareha quiz [topic]` — run interactive quiz (from prep or on-demand topic)
- [x] `stareha note "text"` — add manual note (highest-weight weak concept signal)
- [x] `stareha session start` — automatically shows pending briefing before starting
- [x] Fixed: store lifecycle bug in session stop (store now closed after learning run)

Success:
```
When the user returns, Stareha has prepared useful personalized guidance.
```

Acceptance test passed: `stareha note "struggling with X"` → `stareha prep --quiz` → briefing shows weak concept + quiz generated → `stareha session start` delivers briefing automatically.

Relevant docs:
- [Prepared Guidance](../features/04-prepared-guidance/README.md)

---

## Stage 5 — Local LLM Integration
**Status:** Complete

Goal: Use local intelligence for private learning.

Features:
- [x] `packages/intelligence/local_llm/` — Ollama HTTP client (httpx, configurable timeouts, never blocks)
  - `is_available()`, `list_models()`, `generate()`, `chat()`, `pull()`
- [x] `packages/intelligence/cloud_llm/` — Claude client (thin SDK wrapper)
- [x] `packages/intelligence/router.py` — **the policy router**
  - Enforces: scripts → local LLM → cloud LLM (only with `allow_cloud=True`)
  - `generate()` and `chat()` both return `(result, layer_used)` — always know which layer ran
  - `status()` — used by `stareha status` and `stareha local-llm status`
- [x] `packages/intelligence/prompts.py` — prompt template manager
  - Bundled defaults for: `session-summary`, `quiz-generation`, `memory-enrichment`, `talk-system`
  - Written to `~/.stareha/prompts/` on demand (user-editable)
- [x] `packages/intelligence/summarizer.py` — session summary + memory enrichment via router
  - `summarize_session()` — 2-3 sentence summary after session stop (local LLM only, no cloud)
  - `enrich_memory_candidate()` — richer natural-language memory text (local LLM only)
- [x] Quiz routing updated — `generate_quiz()` now: local LLM → template by default; cloud only when explicitly allowed
- [x] Learning runner updated — `_enrich_candidates()` runs enrichment when Ollama available
- [x] `stareha status` — shows Local LLM + Cloud LLM availability with clear install hints
- [x] `stareha local-llm status` — full intelligence policy status + prompt template list
- [x] `stareha local-llm pull [model]` — pull model via Ollama
- [x] `stareha local-llm prompts` — export default templates to `~/.stareha/prompts/`
- [x] `stareha talk [--cloud]` — conversational mode using memories as context (local LLM preferred)
- [x] `stareha session stop` — generates session summary when Ollama available (non-blocking)
- [x] All layers degrade gracefully — every caller handles `None` return; CLI always tells the user why

Success:
```
Stareha can learn and prepare mostly without sending raw context online.
```

Acceptance test passed: all commands work correctly with no Ollama and no API key; `stareha status` clearly shows both layers as unavailable with install instructions; router correctly falls through all layers to `none`; quiz falls back to template; `stareha talk` shows actionable error.

Relevant docs:
- [Local Intelligence](../features/05-local-intelligence/README.md)
- [Local LLM](../features/05-local-intelligence/local-llm.md)

---

## Stage 5.5 — Stareha Learn Product Wrapper
**Status:** Complete

Goal: Turn the internal engine into a beginner-facing learning continuity product.

Features:
- [x] No-argument `stareha` home screen
- [x] `stareha setup` beginner wizard
  - Learner mode recommended and stable alpha
  - Workspace root captured without scanning every file
  - Recommended tracking enables terminal commands, project file metadata, and manual notes
- [x] `stareha learn "<goal>"` starts a learning session
  - Resolves active project from explicit path, current directory, nearest Git repo, manifest files, workspace root, or recent activity
  - Adds resolved active project to file metadata watch paths when file tracking is enabled
  - Shows pending briefing before starting
- [x] `stareha note "<text>"` accepts unquoted multi-word notes and links them to the active session/project
- [x] `stareha done` ends the session, runs learning, prepares guidance, and prints a Learning Card
- [x] Beginner review flow: "Save / Ignore / Edit / Skip" over pending memory candidates
- [x] `stareha continue` resumes from the last useful point
- [x] `packages/experience/` layer added above the existing engine
  - `mode_presets.py`
  - `project_resolver.py`
  - `project_registry.py`
  - `learning_card.py`
  - `review_flow.py`
  - `continuation.py`
  - `home.py`
- [x] Cloud LLM is no longer implicit for quiz generation; cloud fallback requires an explicit cloud-enabled command

Success:
```
The first-run product loop is setup -> learn -> note -> done -> continue.
Internal commands still exist, but normal learners do not need to understand them.
```

Acceptance test passed with an isolated temporary HOME: `stareha` home screen, `stareha learn React forms`, `stareha note ...`, `stareha done --no-review`, and `stareha continue`.

Relevant docs:
- [CLI Interface](../features/09-interfaces/cli.md)
- [MVP](mvp.md)

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
