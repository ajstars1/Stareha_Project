# Stareha

**Your AI companion that learns how you work, remembers what matters, and prepares your next step.**

Stareha runs locally in the background, watches your terminal (with permission), learns your patterns, and prepares personalized guidance — without sending your data anywhere.

```
Never restart from zero.
```

---

## How it feels

```
$ stareha session start "build the auth flow"
✓ Session started: build the auth flow

... you work for 2 hours ...

$ stareha session stop
✓ Session ended (2h 3m)
Learning: 3 new candidate(s) added to inbox.
Summary: You worked on the auth middleware. Ran npm test repeatedly.
         No errors detected in the final 30 minutes.

$ stareha what-did-you-learn today

  Events observed  47  (terminal: 47)
  Learning runs    1 run · 47 events processed · 3 candidates generated

  Patterns found:  3
    command_pattern  In auth-service, you often run `npm test` (12 times).
    command_pattern  In auth-service, you usually run `npm run dev` then `npm test`.
    error_fix        `npm cache clean` resolves issues after `npm install` fails (2 times).

  Memories approved:  0
  Pending in inbox:   3

$ stareha memory inbox --review
  1. [a3f9d2b1] In auth-service, you often run `npm test` (12 times).
     (a)pprove  (r)eject  (e)dit  (s)kip: a
     ✓ Approved

$ stareha prep
  Work Briefing: auth-service
  Last session: build the auth flow (2h 3m)
  Your workflow:
    · In auth-service, you often run `npm test` (12 times).
  Suggested next:
    → Continue: build the auth flow
```

---

## What it is

Stareha is a **local-first, privacy-preserving AI companion** for developers. It observes your approved workflow, extracts patterns, and prepares personalized guidance — all on your own machine.

**Core ideas:**
- **Local-first** — raw data never leaves your device. Patterns and summaries stay in a local SQLite database.
- **Transparent** — every memory has full provenance. `stareha memory why <id>` shows exactly which events caused a memory.
- **Opt-in** — no source is watched without explicit permission. You control what Stareha sees.
- **Three intelligence layers** — deterministic scripts first, local LLM (Ollama) second, cloud LLM (Claude) only when you explicitly allow it.

---

## Platform

**Linux-first.** Tested on Ubuntu 22.04+ and Arch Linux.

macOS support is planned but not yet implemented (inotify is Linux-specific; requires `watchdog` port). Windows is not planned.

---

## Requirements

- Python 3.11+
- Linux (systemd user services for daemon management)
- `curl` (for the shell hook)

**Optional — for better intelligence:**
- [Ollama](https://ollama.ai) — local LLM, keeps everything private
- `ANTHROPIC_API_KEY` — for cloud LLM fallback and `stareha talk --cloud`

---

## Installation

```bash
git clone https://github.com/ajstars1/Stareha_Project
cd Stareha_Project/src
pip3 install -e .
```

Verify:

```bash
stareha --help
```

---

## Quick start

### 1. First-time setup

```bash
stareha init
```

The wizard asks:
- Enable terminal history? → **yes** — this is the core data source
- Watch a project directory? → optional, give it a path like `~/projects`
- Enable Claude Code history? → yes if you use Claude Code

It installs a shell hook into `~/.zshrc` (or `~/.bashrc`) and sets up the systemd service. **Restart your shell** after init so the hook activates.

### 2. Start the daemon

```bash
stareha start
stareha status
```

### 3. Work normally

Everything from this point is automatic. The shell hook captures every command you run. The daemon stores events locally.

### 4. Use a session for focused work

```bash
stareha session start "fix the login bug"
# ... work ...
stareha session stop
```

Session stop automatically runs the pattern extractor and shows you what was learned.

### 5. Review what Stareha wants to remember

```bash
stareha memory inbox --review
```

You approve, reject, or edit each candidate. Nothing is stored without your say-so.

### 6. Get tomorrow's plan

```bash
stareha prep
```

---

## Command reference

### Daemon

```bash
stareha start                    # start the background daemon
stareha stop                     # stop the daemon
stareha restart                  # restart
stareha status                   # show status: events, inbox, LLM availability
```

### Sessions

```bash
stareha session start "goal"     # begin a tracked session with a goal
stareha session stop             # end session, trigger learning run
stareha session status           # show current session info
```

### Learning

```bash
stareha learn                    # run pattern extraction on new events
stareha learn --force            # run on all events (ignores last-run timestamp)
stareha what-did-you-learn today
stareha what-did-you-learn yesterday
stareha what-did-you-learn session
stareha what-did-you-learn week
stareha ledger                   # full audit log: learning runs, feedback stats
```

### Memory

```bash
stareha memory inbox             # show pending candidates
stareha memory inbox --review    # interactive: approve/reject/edit each one
stareha memory review            # shorthand for --review

stareha memory approve <id>      # approve by ID (first 8 chars work)
stareha memory reject <id>       # reject
stareha memory edit <id>         # edit content then approve

stareha memory why <id>          # full provenance: which events caused this
stareha memory sources <id>      # raw events used as evidence

stareha memory list              # all approved memories
stareha memory list --type command_pattern
stareha memory list --project my-project
stareha memory search "flexbox"  # full-text search

stareha memory forget <id>       # permanently delete a memory
stareha memory stats             # counts by source and type
```

### Guidance

```bash
stareha prep                     # prepare briefing for next session
stareha prep --quiz              # briefing + quiz on top weak concept
stareha brief                    # show latest prepared briefing

stareha note "struggling with async/await"   # manual note (highest-signal input)

stareha quiz "CSS flexbox"       # run a quiz on any topic
stareha quiz                     # run the latest prepared quiz
```

### Local LLM (Ollama)

```bash
stareha local-llm status         # Ollama availability, models, prompt templates
stareha local-llm pull           # pull configured model (llama3.2:3b by default)
stareha local-llm pull mistral:7b
stareha local-llm prompts        # export default prompts to ~/.stareha/prompts/
```

### Talk mode

```bash
stareha talk                     # conversation using local LLM + your memories
stareha talk --cloud             # use Claude (requires ANTHROPIC_API_KEY)
```

Context sent = approved memories only. Never raw events.

### Permissions

```bash
stareha permissions list
stareha permissions add terminal
stareha permissions add files /path/to/project
```

---

## Privacy model

Stareha has three intelligence layers. The decision rule:

```
Can a script do it?      → Use script.   (free, instant, zero privacy risk)
Can local LLM do it?     → Use Ollama.   (private, runs on your machine)
Is cloud LLM needed?     → Use Claude.   (only when you explicitly allow it)
```

**What each layer sees:**

| Layer | Receives | Never receives |
|-------|----------|----------------|
| Scripts | Raw events (already redacted) | — |
| Local LLM | Processed summaries, redacted command lists | Raw terminal output, file contents, secrets |
| Cloud LLM | Memory summaries, learning profile summary | Raw events, file contents, command history |

**Redaction** runs before any event is written to SQLite. API keys (`sk-*`, `ghp_*`, etc.), passwords, tokens, JWTs, database connection strings — all stripped automatically.

**Your data:**

```
~/.stareha/
  db.sqlite          ← all events, memories, sessions (never uploaded)
  config.json        ← your config
  permissions.json   ← what sources are enabled
  prompts/           ← editable LLM prompt templates
```

---

## Local LLM setup (recommended)

Without Ollama, Stareha works fully — quiz generation uses template questions, session summaries are skipped. With Ollama, everything improves and stays private.

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (llama3.2:3b is fast and light)
ollama pull llama3.2:3b

# Start Ollama
ollama serve

# Verify Stareha sees it
stareha status
# → Local LLM  ✓ ollama:11434 — llama3.2:3b
```

With Ollama running:
- `stareha session stop` → generates a natural-language session summary
- `stareha prep --quiz` → LLM-generated quiz questions (not templates)
- `stareha learn` → memory candidate descriptions are enriched
- `stareha talk` → conversational mode using your memories as context

---

## Cloud LLM setup (optional)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
stareha status
# → Cloud LLM  ✓ claude-sonnet-4-6

stareha talk --cloud             # chat with Claude using your memories as context
stareha prep --quiz              # Claude-quality quiz if Ollama unavailable
```

Context sent to Claude = memory summaries only. Never raw events. Never command history.

---

## Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Database | SQLite (local only, WAL mode) |
| Daemon | Python threading + systemd user service |
| Terminal capture | Shell hook (zsh/bash) + inotify for files |
| Pattern extraction | Deterministic scripts |
| Local LLM | Ollama via httpx |
| Cloud LLM | Anthropic Claude via SDK |
| CLI | Click + Rich |
| Redaction | Regex (ported from Hermes/NearAI) |

---

## Project structure

```
Stareha_Project/
├── src/                          # Source code
│   ├── pyproject.toml            # Package config and dependencies
│   ├── apps/
│   │   ├── cli/main.py           # stareha CLI entry point (Click)
│   │   └── daemon/
│   │       ├── main.py           # Background daemon
│   │       └── stareha.service   # systemd service template
│   └── packages/
│       ├── core/
│       │   ├── config/           # Config loader (~/.stareha/config.json)
│       │   └── db/               # SQLite store + schema + migrations
│       ├── collectors/
│       │   ├── terminal/         # Shell history scanner + live hook receiver
│       │   └── files/            # inotify file watcher
│       ├── intelligence/
│       │   ├── scripts/          # Deterministic pattern extractor
│       │   ├── local_llm/        # Ollama HTTP client
│       │   ├── cloud_llm/        # Claude API client
│       │   ├── router.py         # Intelligence policy router
│       │   ├── prompts.py        # Prompt template manager
│       │   ├── learning_runner.py # Orchestrates extraction + writes candidates
│       │   ├── ledger.py         # Learning run tracking + what-did-you-learn
│       │   └── summarizer.py     # Session summary + memory enrichment
│       ├── memory/
│       │   └── manager.py        # approve/reject/forget/why/list/search
│       ├── guidance/
│       │   ├── detector.py       # Weak concept detection
│       │   ├── briefing.py       # Work + learning briefing builder
│       │   ├── quiz.py           # Quiz generation + interactive runner
│       │   └── prep.py           # Guidance orchestrator
│       ├── permissions/          # Opt-in source permissions
│       ├── shared/
│       │   └── redact.py         # Secret/token redaction
│       └── notification/         # Desktop notifications (notify-send)
│
├── product/                      # Product docs
│   ├── vision.md
│   ├── roadmap.md                # Stage 0–10 plan
│   ├── principles.md
│   └── mvp.md
├── features/                     # Per-feature design docs
├── _flows/                       # End-to-end flow diagrams
├── architecture/                 # System architecture docs
├── SITEMAP.md                    # Full doc navigation
└── CLAUDE.md                     # AI assistant rules for this project
```

---

## Roadmap

| Stage | Status | What it adds |
|-------|--------|-------------|
| 0 | ✅ Complete | Product definition, docs structure |
| 1 | ✅ Complete | Daemon, SQLite, terminal scanner, shell hook, file watcher, redaction, permissions |
| 2 | ✅ Complete | Pattern extractor, learning runner, memory governance CLI |
| 3 | ✅ Complete | Learning ledger, audit log, feedback-gated confidence, `what-did-you-learn` |
| 4 | ✅ Complete | Weak concept detection, briefing builder, quiz generation, `prep`/`brief`/`quiz`/`note` |
| 5 | ✅ Complete | Intelligence policy router, Ollama integration, `talk` mode, session summarizer |
| 6 | 🔨 Next | Desktop companion: REST API, web panel, system tray, desktop notifications |
| 7 | Planned | Browser extension: research session tracking, "remember this page" |
| 8 | Planned | Cloud memory: encrypted cross-device sync (summaries only) |
| 9 | Planned | Android app: voice notes, learning reminders, mobile memory search |
| 10 | Vision | Full companion: goals, workflows, lessons, exercises, cross-device |

---

## Contributing

Stareha is in active development. Contributions are welcome.

**Before contributing, read:**
- [`CLAUDE.md`](CLAUDE.md) — project conventions, code rules, commit format
- [`product/roadmap.md`](product/roadmap.md) — which stage is active
- [`_flows/`](_flows/) — master logic files for each system (read before touching behaviour)

**Commit format:** `type: short description`
Types: `feat` `fix` `docs` `chore`

**Good first contributions:**
- Test on a different Linux distro and report issues
- Add bash history parser improvements (currently basic)
- Improve the pattern extractor confidence scoring
- Write tests for `packages/intelligence/scripts/pattern_extractor.py`
- Port the file watcher from `inotify-simple` to `watchdog` for macOS support

**Opening an issue:** Include your OS, Python version, and `stareha status` output.

---

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Ayush Jamwal](https://github.com/ajstars1)*
