# Feature: Interfaces

**Status:** Concept  
**Stage:** 1 (CLI) → 6 (Desktop) → 7 (Browser) → 9 (Android)

---

## What It Is

Stareha's interface surfaces — the ways the user interacts with the companion across different contexts.

---

## Interface Index

| Interface | File | Stage | Priority |
|-----------|------|-------|----------|
| CLI | [cli.md](cli.md) | 1 | MVP — build first |
| Desktop UI | [desktop-ui.md](desktop-ui.md) | 6 | After CLI proven |
| Browser Extension | [browser-extension.md](browser-extension.md) | 7 | After desktop |
| Android App | [android-app.md](android-app.md) | 9 | Long-term |

---

## Interface Philosophy

Start terminal-first. Prove the loop. Then add surfaces.

A great CLI companion is more valuable than a mediocre GUI.

Do not build the desktop UI until the CLI experience is excellent.

---

## CLI First Reasons

- Linux developers live in the terminal
- CLI is the fastest to build and iterate
- CLI is the easiest to automate and test
- Every future interface talks to the same daemon — CLI proves the daemon works

---

## Interface Progression

```
Stage 1: CLI
  → All core commands
  → Session management
  → Memory inbox
  → Learning/work briefings

Stage 6: Desktop UI
  → Tray icon
  → Suggestions panel
  → Memory inbox GUI
  → Daily briefing window

Stage 7: Browser Extension
  → Research session tracking
  → "Remember this page"
  → Tab summary send to Stareha

Stage 9: Android App
  → Voice notes
  → Learning reminders
  → Mobile memory search
```
