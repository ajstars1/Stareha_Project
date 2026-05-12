"""
Browser history collector — reads Chrome and Firefox SQLite databases directly.
No browser extension required.

Chrome:  ~/.config/google-chrome/Default/History   (copy to /tmp — locked while running)
Firefox: ~/.mozilla/firefox/*/places.sqlite         (readable directly in WAL mode)

What is stored:
  - URL, page title, visit count, timestamp
  - Search queries (from Chrome keyword_search_terms, Firefox search history)

What is NOT stored:
  - Passwords, form data, cookies, session tokens
  - Raw query strings that contain auth tokens (redaction strips these)
"""
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from packages.shared.redact import redact_sensitive_text
from packages.permissions import can_collect

# Chrome epoch starts at 1601-01-01 (Windows FILETIME)
_CHROME_EPOCH_OFFSET = 11644473600  # seconds between 1601 and 1970


def _chrome_ts_to_epoch(chrome_ts: int) -> int:
    """Convert Chrome microsecond timestamp to Unix epoch seconds."""
    return max(0, chrome_ts // 1_000_000 - _CHROME_EPOCH_OFFSET)


def _dedup_key(source: str, url: str, ts: int) -> str:
    return hashlib.sha256(f"{source}:{url}:{ts}".encode()).hexdigest()


# ── Chrome ─────────────────────────────────────────────────────────────────────

_CHROME_PATHS = [
    Path.home() / ".config" / "google-chrome" / "Default" / "History",
    Path.home() / ".config" / "chromium" / "Default" / "History",
    Path.home() / ".config" / "chrome-data" / "Default" / "History",
    Path.home() / ".config" / "BraveSoftware" / "Brave-Browser" / "Default" / "History",
]

# Domains to skip — browser UI, ads, tracking pixels
_SKIP_DOMAINS = {
    "newtab", "settings", "extensions", "history",
    "doubleclick.net", "googlesyndication.com", "googletagmanager.com",
    "googletagservices.com", "google-analytics.com", "googleadservices.com",
    "ads.google.com", "adservice.google.com",
    "facebook.com/tr", "connect.facebook.net",
    "analytics.twitter.com", "t.co",
}


def _should_skip_url(url: str) -> bool:
    if not url or not url.startswith("http"):
        return True
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower().lstrip("www.")
        if any(skip in domain for skip in _SKIP_DOMAINS):
            return True
        if len(parsed.path) > 500:  # suspiciously long tracking URL
            return True
    except Exception:
        pass
    return False


def scan_chrome(store, since: Optional[int] = None) -> int:
    """Read Chrome/Chromium/Brave history. Returns count of new events."""
    if not can_collect("browser"):
        return 0

    existing_keys = {
        r[0] for r in store._conn.execute(
            "SELECT json_extract(content, '$.dedup') FROM events WHERE source='browser'"
        ).fetchall() if r[0]
    }

    imported = 0
    since_ts = since or 0

    for history_path in _CHROME_PATHS:
        if not history_path.exists():
            continue

        # Copy to temp — Chrome locks the file while running
        tmp = tempfile.mktemp(suffix=".sqlite")
        try:
            shutil.copy2(str(history_path), tmp)
            import sqlite3
            conn = sqlite3.connect(tmp)
            conn.row_factory = sqlite3.Row

            # Convert since to Chrome microseconds
            chrome_since = (since_ts + _CHROME_EPOCH_OFFSET) * 1_000_000 if since_ts else 0

            rows = conn.execute(
                "SELECT url, title, visit_count, last_visit_time "
                "FROM urls WHERE last_visit_time > ? ORDER BY last_visit_time DESC LIMIT 2000",
                (chrome_since,),
            ).fetchall()

            # Also grab search queries
            searches = {}
            try:
                sq = conn.execute(
                    "SELECT LOWER_TERM as term, url_id FROM keyword_search_terms "
                    "ORDER BY url_id DESC LIMIT 500"
                ).fetchall()
                for s in sq:
                    searches[s["url_id"]] = s["term"]
            except Exception:
                pass

            # Get url_id mapping
            url_ids = {}
            try:
                uid_rows = conn.execute(
                    "SELECT id, url FROM urls WHERE last_visit_time > ? LIMIT 2000",
                    (chrome_since,),
                ).fetchall()
                url_ids = {r["id"]: r["url"] for r in uid_rows}
            except Exception:
                pass

            conn.close()

            for row in rows:
                url = row["url"]
                if _should_skip_url(url):
                    continue

                epoch = _chrome_ts_to_epoch(row["last_visit_time"])
                dedup = _dedup_key("chrome", url, epoch)

                if dedup in existing_keys:
                    continue
                existing_keys.add(dedup)

                title = redact_sensitive_text(row["title"] or "")
                clean_url = redact_sensitive_text(url)

                content = json.dumps({
                    "url": clean_url,
                    "title": title,
                    "visit_count": row["visit_count"],
                    "browser": "chrome",
                    "dedup": dedup,
                })
                store.write_event(
                    type="browser_visit",
                    source="browser",
                    content=content,
                    redacted=True,
                )
                imported += 1

            # Store search queries as separate events
            for url_id, term in searches.items():
                if not term or len(term) < 2:
                    continue
                dedup = _dedup_key("chrome_search", term, url_id)
                if dedup in existing_keys:
                    continue
                existing_keys.add(dedup)
                content = json.dumps({
                    "query": term,
                    "type": "search",
                    "browser": "chrome",
                    "dedup": dedup,
                })
                store.write_event(
                    type="browser_search",
                    source="browser",
                    content=content,
                    redacted=True,
                )
                imported += 1

        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    return imported


# ── Firefox ───────────────────────────────────────────────────────────────────

def _find_firefox_profiles() -> list[Path]:
    base = Path.home() / ".mozilla" / "firefox"
    if not base.exists():
        return []
    return [
        p / "places.sqlite"
        for p in base.iterdir()
        if p.is_dir() and (p / "places.sqlite").exists()
    ]


def scan_firefox(store, since: Optional[int] = None) -> int:
    """Read Firefox history from places.sqlite. Returns count of new events."""
    if not can_collect("browser"):
        return 0

    existing_keys = {
        r[0] for r in store._conn.execute(
            "SELECT json_extract(content, '$.dedup') FROM events WHERE source='browser'"
        ).fetchall() if r[0]
    }

    imported = 0
    since_epoch_us = (since or 0) * 1_000_000  # Firefox uses microseconds

    for places_path in _find_firefox_profiles():
        # Copy to temp in case Firefox is running
        tmp = tempfile.mktemp(suffix=".sqlite")
        try:
            shutil.copy2(str(places_path), tmp)
            import sqlite3
            conn = sqlite3.connect(tmp)
            conn.row_factory = sqlite3.Row

            rows = conn.execute(
                "SELECT url, title, visit_count, last_visit_date "
                "FROM moz_places WHERE last_visit_date > ? "
                "AND visit_count > 0 ORDER BY last_visit_date DESC LIMIT 2000",
                (since_epoch_us,),
            ).fetchall()

            conn.close()

            for row in rows:
                url = row["url"]
                if _should_skip_url(url):
                    continue

                epoch = (row["last_visit_date"] or 0) // 1_000_000
                dedup = _dedup_key("firefox", url, epoch)

                if dedup in existing_keys:
                    continue
                existing_keys.add(dedup)

                title = redact_sensitive_text(row["title"] or "")
                clean_url = redact_sensitive_text(url)

                content = json.dumps({
                    "url": clean_url,
                    "title": title,
                    "visit_count": row["visit_count"],
                    "browser": "firefox",
                    "dedup": dedup,
                })
                store.write_event(
                    type="browser_visit",
                    source="browser",
                    content=content,
                    redacted=True,
                )
                imported += 1

        except Exception:
            pass
        finally:
            try:
                os.unlink(tmp)
            except Exception:
                pass

    return imported


# ── Main entry point ───────────────────────────────────────────────────────────

def scan_browser_history(store, since: Optional[int] = None) -> int:
    """Scan all available browsers. Returns total new events imported."""
    total = 0
    total += scan_chrome(store, since)
    total += scan_firefox(store, since)
    return total
