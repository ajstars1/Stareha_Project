# Stareha

**A private learning continuity companion that remembers what you were learning and prepares your next step.**

Stareha runs locally in the background, watches approved learning signals, and turns them into session continuity — without requiring cloud AI or uploading raw data.

```
Never restart your learning from zero.
```

---

## How it feels

```
$ stareha setup
✓ Setup complete.

$ stareha learn "React forms"
✓ Learning started: React forms
Project: react-auth-app (git, high confidence)

... you work normally ...

$ stareha note "I am confused about controlled inputs"
✓ Note saved. This will inform your next guidance.

$ stareha done
✓ Learning session finished (42m)

Learning Card
Goal  React forms
Project  react-auth-app  (42m)

Worked on
  - React forms
  - Ran 18 terminal command(s)
  - Edited project files (.tsx x6, .css x2)

Stuck on
  - I am confused about controlled inputs

Next step
  -> Continue with one focused practice task for: React forms

$ stareha continue
Continue Learning
Last goal  React forms
Project  react-auth-app

Next
  1. Continue with one focused practice task for: React forms
```

---

## What it is

Stareha is a **local-first, privacy-preserving learning companion** for developers and technical learners. It observes approved workflow signals, remembers session context, extracts useful patterns, and prepares a clear next step.

**Core ideas:**
- **Local-first** — raw data never leaves your device. Patterns and summaries stay in a local SQLite database.
- **Transparent** — every memory has full provenance. `stareha memory why <id>` shows exactly which events caused a memory.
- **Opt-in** — no source is watched without explicit permission. You control what Stareha sees.
- **Works without AI** — deterministic scripts and local SQLite power the base loop.
- **Optional intelligence layers** — local LLM (Ollama) can improve wording and quizzes; cloud LLM (Claude, Gemini, OpenAI, Groq) is only used by explicit cloud-enabled commands.

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
- Cloud LLM — Claude, Gemini, OpenAI, or Groq via `stareha llm setup`

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
stareha setup
```

The beginner setup asks:
- Which mode to use first. `Learner` is the stable alpha path.
- Where your learning projects live, such as `~/projects`.
- Whether to enable recommended local tracking: terminal commands, project file activity metadata, and manual notes.
- Which LLM to use — launches `stareha llm setup` (guided wizard: Cloud or Local, pick provider, set credentials).
- Whether to start a first learning session now.

Setup installs the shell hook into `~/.zshrc` or `~/.bashrc`, stores the workspace root in `~/.stareha/config.json`, and starts the daemon when needed. **Restart your shell** once after setup so the hook activates.

### 2. Start the daemon

```bash
stareha start
stareha status
```

### 3. Work normally

Everything from this point is automatic. The shell hook captures every command you run. The daemon stores events locally.

### 4. Start learning

```bash
stareha learn "React forms"
# ... work ...
stareha note "I am confused about controlled inputs"
stareha done
```

`stareha learn "goal"` starts a learning session, resolves the active project from the explicit path, current directory, nearest Git repo, manifest files, or recent activity, and links notes/events to that session.

### 5. Review what Stareha noticed

```bash
stareha done
```

At session end, Stareha builds a Learning Card and offers a beginner review flow:

```
Save / Ignore / Edit / Skip
```

The advanced memory inbox is still available for full control.

### 6. Continue later

```bash
stareha continue
```

This shows the last goal, project, useful command context, and the next step so you do not restart from zero.

---

## Command reference

### Beginner learning loop

```bash
stareha                         # home screen
stareha setup                   # first-time beginner setup
stareha learn "goal"            # start a learning session
stareha learn "goal" --project ~/projects/app
stareha note "text"             # add a note linked to the active session
stareha done                    # finish session, build Learning Card, review notices
stareha done --no-review        # finish without interactive review
stareha continue                # resume from the last useful point
```

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

These are advanced/internal commands. New learners should usually use `stareha learn "goal"` and `stareha done`.

### Learning

```bash
stareha learn                    # advanced: run pattern extraction on new events
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
stareha quiz --cloud "CSS flexbox" # explicitly allow cloud provider fallback
stareha quiz                     # run the latest prepared quiz
```

### LLM management

```bash
stareha llm setup                # connect a cloud or local provider (guided wizard)
stareha llm status               # show connected providers and which is active
```

Supported cloud providers: Claude Code (OAuth — uses your claude.ai subscription), Claude (Anthropic API key), Gemini, OpenAI, Groq.

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
stareha talk --cloud             # explicitly use active cloud provider
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
Can a script do it?      → Use script.     (free, instant, zero privacy risk)
Can local LLM do it?     → Use Ollama.     (private, runs on your machine)
Did the user explicitly allow cloud? → Use cloud LLM.   (summary-only context)
```

**What each layer sees:**

| Layer | Receives | Never receives |
|-------|----------|----------------|
| Scripts | Raw events (already redacted) | — |
| Local LLM | Processed summaries, redacted command lists | Raw terminal output, file contents, secrets |
| Cloud LLM | Summary-only task context for cloud-enabled commands | Raw events, file contents, command history |

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

Without Ollama, the beginner loop still works: setup, learn, notes, Learning Cards, review, and continue all use scripts and SQLite. Quiz generation uses template questions and AI summaries are skipped. With Ollama, wording, summaries, and generated quizzes improve while staying local.

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model (llama3.2:3b is fast and light)
ollama pull llama3.2:3b

# Start Ollama
ollama serve

# Verify Stareha sees it
stareha llm status
# → Local
# →   ✓ Ollama   llama3.2:3b   (http://localhost:11434)
```

With Ollama running:
- `stareha session stop` → generates a natural-language session summary
- `stareha prep --quiz` → LLM-generated quiz questions (not templates)
- `stareha learn` → memory candidate descriptions are enriched
- `stareha talk` → conversational mode using your memories as context

---

## Cloud LLM setup (optional)

```bash
stareha llm setup
# Guided wizard — pick Cloud or Local
# Cloud options: Claude Code (OAuth), Claude API key, Gemini, OpenAI, Groq

stareha llm status
# → Cloud LLM  ✓ Gemini (Google) — gemini-3.1-flash-lite

stareha talk --cloud             # chat using active cloud provider + your approved memories
stareha quiz --cloud "Flexbox"   # explicitly allow cloud fallback for this quiz
```

Cloud is not enabled by setup. Context sent is summary-only and command-specific. Never raw events. Never command history.

**Recommended:** Claude Code OAuth — if you have a claude.ai Pro or Max subscription, no API key needed. The wizard reads `~/.claude/.credentials.json` automatically.

---

## Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Database | SQLite (local only, WAL mode) |
| Daemon | Python threading + systemd user service |
| Terminal capture | Shell hook (zsh/bash) + inotify for files |
| Pattern extraction | Deterministic scripts |
| Product experience | Beginner CLI wrapper + Learning Card |
| Local LLM | Ollama via httpx |
| Cloud LLM | Claude (OAuth + API key), Gemini, OpenAI, Groq |
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
│       │   ├── cloud_llm/        # Multi-provider cloud LLM client (Claude OAuth/API, Gemini, OpenAI, Groq)
│       │   ├── router.py         # Intelligence policy router
│       │   ├── prompts.py        # Prompt template manager
│       │   ├── learning_runner.py # Orchestrates extraction + writes candidates
│       │   ├── ledger.py         # Learning run tracking + what-did-you-learn
│       │   └── summarizer.py     # Session summary + memory enrichment
│       ├── experience/
│       │   ├── mode_presets.py   # Learner/Companion/Researcher presets
│       │   ├── project_resolver.py # Active project detection
│       │   ├── learning_card.py  # Session-end Learning Card
│       │   ├── review_flow.py    # Save/Ignore/Edit review UX
│       │   ├── continuation.py   # `stareha continue`
│       │   └── home.py           # no-argument home screen
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
| 5.5 | ✅ Complete | Product experience wrapper: `setup`, home, `learn "goal"`, `done`, `continue`, Learning Card |
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
