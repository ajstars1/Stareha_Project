# Action Permissions

**Status:** Concept  
**Stage:** 2

---

## What It Is

Action permissions control what Stareha can do autonomously vs. what requires explicit user approval before acting.

---

## Core Rule

```
Suggest autonomously.
Act with permission only.
```

Stareha may always: suggest, recommend, prepare, notify.
Stareha must ask before: running commands, modifying files, opening apps.

---

## Action Types

| Action | Default | Can be pre-approved |
|--------|---------|-------------------|
| Show suggestion | Always allowed | N/A |
| Generate quiz/exercise | Always allowed | N/A |
| Notify (CLI/tray) | Always allowed | N/A |
| Run a terminal command | Requires approval | Yes, per scope |
| Open a file | Requires approval | Yes, per project |
| Write to a file | Requires approval | No (always ask) |
| Make a network request | Requires approval | No (always ask) |

---

## Approval Flow

When Stareha wants to run a command:

```
Stareha: I want to run: npm test in ~/projects/agent-os
Reason: you usually run this after build completes.

Allow?
  (y) Yes, this time
  (n) No
  (a) Always allow this in agent-os
  (never) Never suggest this
```

The choice is stored:
- `y` → execute once, no record
- `n` → do not execute, no record
- `a` → add to approved_actions for this scope
- `never` → add to blocked_actions

---

## Pre-Approved Action Scopes

Users can pre-approve classes of actions:

```bash
stareha permissions allow "npm test in ~/projects/agent-os"
stareha permissions allow "pnpm build in ~/projects/*"
stareha permissions block "rm -rf"
stareha permissions list-actions
```

---

## Action Log

All actions taken are logged:

```bash
stareha actions log
```

Output:
```
Recent actions:

2026-05-06 09:12  [auto]   suggestion shown: "run npm build next"
2026-05-06 09:14  [user]   approved: npm run build in agent-os
2026-05-06 09:15  [auto]   notification: inbox has 2 new candidates
2026-05-06 08:30  [auto]   guidance prepared for today
```

---

## Related Files
- [Permission System](README.md)
- [Source Permissions](source-permissions.md)
- [Permission Flow](../../_flows/permission-flow.md)
- [Product Principles](../../product/principles.md) — Principle 5
