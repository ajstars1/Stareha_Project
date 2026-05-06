# Connector: Browser

**Status:** Built  
**Stage:** 1  
**Permission required:** `browser` (enabled via `stareha init` or `stareha permissions add browser`)

---

## What It Is

The browser connector reads Chrome and Firefox history directly from their local SQLite database files. **No browser extension required.**

Both Chrome and Firefox store browsing history in SQLite databases on disk. Stareha copies the file to `/tmp`, reads it, and deletes the copy — safe even when the browser is running.

---

## Supported Browsers

| Browser | File location | Status |
|---------|--------------|--------|
| Google Chrome | `~/.config/google-chrome/Default/History` | ✅ |
| Chromium | `~/.config/chromium/Default/History` | ✅ |
| Brave | `~/.config/BraveSoftware/Brave-Browser/Default/History` | ✅ |
| Firefox | `~/.mozilla/firefox/*/places.sqlite` | ✅ |

---

## How it works

### Chrome / Chromium / Brave

The `History` file is a SQLite database locked while the browser is running. Stareha:

1. Copies it to a temp file (`shutil.copy2` — instant)
2. Opens the copy (no lock contention)
3. Reads the `urls` table and `keyword_search_terms` table
4. Deletes the temp file

Tables used:
- `urls` — `url`, `title`, `visit_count`, `last_visit_time` (Chrome epoch format)
- `keyword_search_terms` — `lower_term` (the search query you typed)

### Firefox

The `places.sqlite` file is directly readable even while Firefox is running (WAL mode). Stareha reads it after copying to temp:

Table used:
- `moz_places` — `url`, `title`, `visit_count`, `last_visit_date` (microseconds)

---

## What is stored

### `browser_visit` events

```json
{
  "type": "browser_visit",
  "source": "browser",
  "content": {
    "url": "https://supabase.com/docs/guides/auth",
    "title": "Supabase Auth Documentation",
    "visit_count": 12,
    "browser": "chrome",
    "dedup": "sha256..."
  }
}
```

### `browser_search` events

```json
{
  "type": "browser_search",
  "source": "browser",
  "content": {
    "query": "postgres row level security tutorial",
    "type": "search",
    "browser": "chrome",
    "dedup": "sha256..."
  }
}
```

---

## Filtering

URLs are filtered before storage. Skipped automatically:
- Tracking and ad domains (`doubleclick.net`, `googlesyndication.com`, etc.)
- Chrome internal URLs (`chrome://`, `chrome-extension://`)
- Empty or non-HTTP URLs
- URLs with path length > 500 chars (likely tracking parameters)

---

## Pattern extraction

The `extract_research_topics()` extractor produces candidates from browser data:

**From domain visits (threshold: 5+ visits):**
```
"You frequently visit supabase.com (101 times)."
type: research_topic | source: browser | confidence: 0.72 | sensitivity: low
```

**From search queries (threshold: 3+ identical searches):**
```
"You searched for 'postgres rls example' 5 times."
type: research_topic | source: browser | confidence: 0.69 | sensitivity: normal
```

---

## Privacy

- URL query strings run through redaction before storage (strips tokens, API keys)
- Passwords and form data are never in the `urls` table — only visited URLs
- The browser's SQLite is opened read-only via a temp copy, never modified
- No data is sent anywhere — events stay in `~/.stareha/db.sqlite`

---

## Stage 7 — Browser Extension (future)

The original design called for a browser extension to send real-time summaries. That remains planned for Stage 7. The current file-reading approach covers:
- Full visit history
- Search queries
- Domain frequency

What file reading cannot do (needs extension):
- Know when you're actively reading vs. just visiting
- Detect when you're on a tutorial vs. checking email
- Send "remember this page" on demand
- Real-time events (file reading is batch on daemon start)

---

## Implementation

`src/packages/collectors/browser/__init__.py`

Key function: `scan_browser_history(store, since=None) -> int`

Calls `scan_chrome()` then `scan_firefox()`. Returns total events imported.
Called by daemon on startup. Deduplicates by `sha256(source:url:timestamp)`.

---

## Related Files

- [Connectors Overview](README.md)
- [Browser Memory](../../02-workflow-memory/browser-memory.md)
- [Pattern Extractor](../../../src/packages/intelligence/scripts/pattern_extractor.py)
