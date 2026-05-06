# Interface: Browser Extension

**Status:** Concept  
**Stage:** 7

---

## What It Is

The Stareha browser extension connects the user's research and learning sessions in the browser to the local Stareha daemon.

---

## Why It Matters

A huge portion of learning happens in the browser. Without this connector, Stareha is blind to what the user reads, researches, and studies online.

---

## What It Does

| Feature | How it works |
|---------|-------------|
| Track research session | Detects when user is on docs/tutorial sites |
| "Remember this page" button | User clicks to add page to Stareha memory |
| Summarize current tab | Sends page metadata to Stareha (not full content) |
| Track learning resources | Notes when user returns to same resource |
| Start research session | User explicitly tags a session (e.g., "learning Flexbox") |

---

## Privacy Design

The extension sends:
- Page title
- Domain
- Estimated topic (from title + domain)
- Time spent
- User-tagged category

The extension NEVER sends:
- Full page HTML
- Login state or cookies
- Financial or personal pages (blocked by content policy)
- Pages the user hasn't approved

---

## Blocked Domains (Hardcoded)

```
banking, payment, health, medical sites
Email (gmail, outlook, etc.)
Social media feeds
Any page detected as containing personal/sensitive content
```

---

## Communication

Extension sends events to local daemon:
```
POST http://localhost:7432/browser-event
Content-Type: application/json

{"type": "research_session", "topic": "CSS Flexbox", 
 "domains": ["developer.mozilla.org"], "duration": 1500}
```

Port 7432, localhost only. User must have `browser:read` permission enabled.

---

## UI

Extension popup:
```
┌─────────────────────────┐
│ Stareha             [●] │
├─────────────────────────┤
│ Current: developer.mozilla.org
│ Topic: CSS Flexbox      │
│ Time: 24 min            │
│                         │
│ [📌 Remember this page] │
│ [🏷️  Tag as learning]   │
│ [⏸️  Pause tracking]    │
├─────────────────────────┤
│ Today: 3 research sessions
│ Last: Flexbox, React, SQLite
└─────────────────────────┘
```

---

## Related Files
- [Interfaces Overview](README.md)
- [Browser Connector](../01-learning/connectors/browser.md)
- [Browser Memory](../02-workflow-memory/browser-memory.md)
- [Roadmap](../../product/roadmap.md) — Stage 7
