# Stareha

**Your AI companion that learns how you work, remembers what matters, and prepares your next step.**

AgentOS Continuum gives your computer memory. Stareha turns that memory into guidance.

---

## What it is

Stareha is a local-first background companion for developers and learners. It observes your approved workflow (terminal, files, Claude Code sessions), learns useful patterns, and prepares personalized guidance before you ask.

```
Never restart from zero.
```

Every time you open your laptop, Stareha knows what you were working on, where you got stuck, and what to do next.

---

## Current stage

**Stage 4 — Prepared Guidance built and working.**

```bash
stareha note "struggling with async/await"  # highest-signal weak concept input
stareha prep --quiz                          # generate briefing + quiz for weak concepts
stareha brief                                # show latest briefing at any time
stareha quiz "CSS flexbox"                   # run an interactive quiz on any topic
stareha session start "learn web dev"        # automatically shows pending briefing
```

Stage 1: daemon, SQLite event store, terminal scanner, live hook, file watcher, redaction, permissions.  
Stage 2: pattern extractor, learning runner, full memory governance CLI.  
Stage 3: learning_runs audit, feedback-gated confidence, `what-did-you-learn`, `ledger`.  
Stage 4: weak concept detector, deterministic briefing builder, quiz generation (Claude API + template fallback), `prep`/`brief`/`quiz`/`note`, briefing delivery on session start.

Moving to Stage 5: Local LLM — replace cloud quiz generation with Ollama.

See [product/roadmap.md](product/roadmap.md) for the full plan.

---

## How it will work (MVP)

```bash
stareha session start "learn web development"
# ... you work, Stareha observes ...
stareha session stop

stareha what-did-you-learn today
# Today I learned:
# - You practiced CSS Flexbox for 95 minutes
# - You struggled with DOM selectors (4 errors)
# - You searched Flexbox alignment 6 times

stareha prep tomorrow
# Tomorrow's plan:
# 1. 10-min Flexbox recap
# 2. 5-question quiz
# 3. Responsive card exercise
```

---

## Principles

- **Local-first** — raw data never leaves your device
- **Transparent** — every memory has full provenance (`stareha memory why <id>`)
- **Opt-in** — no source is watched without explicit permission
- **Quiet** — only appears when it has something useful

---

## Documentation

All design docs live in this repo. Start with:

- [product/vision.md](product/vision.md) — what Stareha is and why
- [product/roadmap.md](product/roadmap.md) — Stage 0–10 roadmap
- [SITEMAP.md](SITEMAP.md) — full navigation of all docs

---

## Stack

**Language:** Python (MVP) — fast iteration, rich ecosystem for daemon/SQLite/inotify  
**LLM:** Scripts first → Ollama (local) → Claude (cloud, only when needed)  
**Storage:** SQLite (local only)  
**Platform:** Linux-first

---

*Private — Ayush Jamwal*
