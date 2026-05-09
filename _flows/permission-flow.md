# Permission Flow

> Master logic file. Read before implementing. Update when logic changes.

**Status:** Updated
**Stage:** 1–5.5

---

## What This Covers

How permissions are requested, granted, scoped, and revoked for data sources and actions.

---

## Core Rule

```
Stareha never reads a source without explicit permission.
Act with permission only.
```

---

## Source Permission Flow

```
First run (stareha setup)
  ↓
Stareha asks for learner-friendly local sources:
  - Terminal commands and exit codes
  - Project file activity metadata
  - Manual notes
  - Optional future sources such as saved browser pages or AI chat imports
  ↓
User confirms recommended local tracking or customizes sources
  ↓
Permissions written to ~/.stareha/permissions.json
  ↓
Daemon only collects from enabled sources
  ↓
User can enable/disable at any time:
  stareha permissions add terminal
  stareha permissions remove browser
  stareha permissions list
```

The advanced `stareha init` path still exists for direct source setup.

---

## Action Permission Flow

```
Stareha wants to perform an action (e.g., run a command)
  ↓
Is this action in the pre-approved scope?
  YES → execute silently, log action
  NO ↓

Prompt user for approval:
  "Stareha wants to: run npm test in ~/projects/agent-os
   Reason: you usually run this after build. Allow? (y/n/always)"
  ↓
User responds:
  y       → execute once, do not remember
  n       → do not execute, note rejection
  always  → add to approved scope, execute
  never   → add to blocked scope, do not execute
  ↓
Decision written to action_permissions table
```

---

## Permission Scopes

| Scope | What it means |
|-------|--------------|
| `terminal:read` | Can read shell history |
| `terminal:watch` | Can observe commands as they run |
| `files:watch:<path>` | Can watch specific directory |
| `claude_code:read` | Can read Claude Code conversation history |
| `browser:read` | Can receive data from browser extension |
| `app_usage:read` | Can observe running processes |
| `action:run_command` | Can suggest/run terminal commands |
| `action:open_file` | Can suggest/open files |

---

## Permissions File Format

```json
{
  "sources": {
    "terminal": { "enabled": true, "watch": true },
    "files": {
      "enabled": true,
      "paths": ["~/projects/agent-os", "~/projects/stareha"]
    },
    "claude_code": { "enabled": true },
    "browser": { "enabled": false },
    "app_usage": { "enabled": false }
  },
  "actions": {
    "approved": ["npm test in ~/projects/agent-os"],
    "blocked": []
  }
}
```

---

## Permission CLI Commands

```bash
stareha permissions list              # Show all current permissions
stareha permissions add terminal      # Enable terminal source
stareha permissions remove browser    # Disable browser source
stareha permissions add files ~/projects/agent-os   # Watch specific path
stareha permissions reset             # Remove all permissions (fresh start)
```

---

## Related Files
- [Permission System Feature](../features/08-permission-system/README.md)
- [Source Permissions](../features/08-permission-system/source-permissions.md)
- [Action Permissions](../features/08-permission-system/action-permissions.md)
- [Product Principles](../product/principles.md) — Principles 2, 5, 6
