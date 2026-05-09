# Feature: Permission System

**Status:** Built
**Stage:** 1–5.5
**Why it matters:** Permission is the gate between observation and invasion. Setup recommends local learning sources, but the user still explicitly confirms them.

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
`stareha setup` recommends terminal, project file metadata, and manual notes for Learner mode.
User confirms sources explicitly.
User approves action types explicitly.
```

---

## First-Run Experience

```
stareha setup

Welcome to Stareha Learn.

Setup takes about two minutes and keeps raw data local.

What can Stareha use to understand your learning?

Recommended:
[x] Terminal commands and exit codes
[x] Project file activity metadata
[x] Manual notes you add with `stareha note`
[ ] Browser pages you manually save
[ ] AI chat imports

Use recommended local tracking? [Y/n]
```

The advanced `stareha init` command still exists for direct source setup and daemon/systemd installation.

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
