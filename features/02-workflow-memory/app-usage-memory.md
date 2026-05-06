# App Usage Memory

**Status:** Concept  
**Stage:** 2

---

## What It Is

App usage memory stores patterns about which applications the user uses together, their work environment setup, and time-of-day work habits.

---

## Why It Matters

App patterns reveal the user's work environment and help Stareha understand context:
- "If VS Code + terminal + browser are all open → likely in active dev session"
- "If only browser is open → likely researching or in learning mode"

---

## Memory Categories

### App Combinations
Tools the user consistently uses together.

Example:
```
Memory: "Ayush usually works with terminal, VS Code, and browser open together."
Source: app_usage monitor
Evidence: 18 of 23 sessions
Confidence: 0.87
```

### Time-of-Day Patterns
When the user typically works.

Example:
```
Memory: "Peak work hours: 10:00–13:00 and 15:00–19:00"
Source: app_usage + session timestamps
Evidence: 30 sessions
Confidence: 0.82
```

### Context Inference
What app combinations suggest about current activity.

| App combination | Inferred context |
|----------------|----------------|
| terminal + VS Code + browser | Active development |
| browser only (docs) | Research/learning |
| terminal only | Deployment/server work |
| browser + notes app | Planning/research |

---

## How It's Collected

A background process polls running applications every 5 minutes during active use.

Permission required: `app_usage:read`

Data collected: application names, not window content.

Never collected: what the user is doing inside the app.

---

## Related Files
- [Workflow Memory](README.md)
- [Daemon & Runtime](../07-daemon-runtime/README.md)
- [Permission Flow](../../_flows/permission-flow.md)
