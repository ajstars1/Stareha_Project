# Feature: Permission System

**Status:** Concept  
**Stage:** 1  
**Why it matters:** Permission is the gate between observation and invasion. Every data source requires explicit opt-in. No defaults.

---

## What It Is

The permission system controls which data sources Stareha can read from and which actions it can take autonomously. Everything is opt-in.

---

## Why It Matters

Without explicit permissions, Stareha could silently observe everything. That's a privacy violation.

With explicit permissions:
- The user knows exactly what Stareha sees
- Each source is independently controllable
- Trust is earned, not assumed

---

## Sub-Features

| Sub-feature | File | What it covers |
|-------------|------|---------------|
| Source permissions | [source-permissions.md](source-permissions.md) | Per-source opt-in for data collection |
| Action permissions | [action-permissions.md](action-permissions.md) | What Stareha can do autonomously |

---

## Core Design

```
Default state: all sources OFF, all actions require approval.
User enables sources explicitly.
User approves action types explicitly.
```

---

## First-Run Experience

```
stareha init

Welcome to Stareha.

Stareha can learn from approved sources. Nothing is enabled by default.

Which sources would you like to enable?

[ ] Terminal commands (reads shell history, observes new commands)
[ ] Project files (watches specific directories for file changes)
[ ] Claude Code (reads AI session history and CLAUDE.md files)
[ ] Browser (requires browser extension — Stage 7)
[ ] App usage (observes running application names)

Enable sources: (use space to select, enter to confirm)
```

---

## Permission Storage

```
~/.stareha/permissions.json
```

This file is user-readable and user-editable. Format: see [Permission Flow](../../_flows/permission-flow.md).

---

## Related Flows
- [Permission Flow](../../_flows/permission-flow.md)
- [Learning Flow](../../_flows/learning-flow.md) — collectors are gated by permissions
