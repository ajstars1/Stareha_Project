# Connector: Browser

**Status:** Concept  
**Stage:** 7  
**Permission required:** `browser:read`

---

## What It Is

The browser connector receives research and learning session data from a companion browser extension. It connects what the user reads, researches, and learns online to their Stareha learning profile.

---

## Why It Matters

Most learning and research happens in the browser. Developers:
- Read documentation while coding
- Search for error solutions
- Follow tutorials
- Research new topics

Without browser context, Stareha misses a huge portion of the user's learning activity.

---

## Architecture

This connector is different from others — it cannot read the browser directly (privacy).

Instead:
1. User installs the Stareha browser extension
2. Extension sends **summaries only** (never full page content)
3. Summaries arrive via local HTTP endpoint on the daemon

```
Browser Extension
  ↓  (local only, port 7432)
Stareha Daemon HTTP Endpoint
  ↓
Browser Connector
  ↓
Event Store
```

---

## What the Extension Sends

| Event | When | Data |
|-------|------|------|
| `page_visit` | Tab opened/focused | Domain, title, estimated topic |
| `research_session` | 3+ pages on same topic | Topic summary, domains visited |
| `resource_saved` | User clicks "Remember this" | URL, title, user note |
| `learning_session` | User on tutorial/docs for 10+ min | Topic, resource type |
| `search_query` | User searches something | Query (anonymized if needed) |

The extension NEVER sends:
- Full page HTML
- Cookies or login state
- Financial or personal pages
- Pages the user doesn't explicitly share

---

## User Controls (Extension)

- Pause collection
- Mark current tab as private
- See what was sent
- Clear browser data from Stareha

---

## Example Events

```json
{
  "type": "research_session",
  "source": "browser",
  "topic": "CSS Flexbox",
  "domains": ["developer.mozilla.org", "css-tricks.com"],
  "duration_minutes": 25,
  "search_count": 6,
  "timestamp": "2026-05-01T14:00:00Z"
}
```

---

## Example Memories Generated

```
When learning web development, Ayush often researches Flexbox, DOM selectors, and React components.
Source: browser | Evidence: 6 research sessions | Confidence: 0.87
```

```
developer.mozilla.org and css-tricks.com are Ayush's primary CSS references.
Source: browser | Evidence: 12 visits | Confidence: 0.91
```

---

## Stage Note

This connector is Stage 7 (Browser Extension stage). In MVP, browser data is collected manually:
- User can run `stareha note "I was researching Flexbox"` to add context
- Or use `stareha session start "learning Flexbox"` to tag a manual session

---

## Related Files
- [Connectors Overview](README.md)
- [Browser Memory](../../02-workflow-memory/browser-memory.md)
- [Browser Extension Interface](../../09-interfaces/browser-extension.md)
