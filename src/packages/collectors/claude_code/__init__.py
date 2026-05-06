"""
Claude Code session collector.

Reads conversation history from ~/.claude/projects/*/SESSION.jsonl
Each session = one Claude Code conversation in a project directory.

What we extract (never raw code or file contents):
  - Project name (from directory path)
  - First user message of each session (what was asked)
  - Message count (how much was discussed)
  - Session timestamps

Privacy: only text messages extracted, never file contents or pastes.
Redaction runs before storage.
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from packages.shared.redact import redact_sensitive_text
from packages.permissions import can_collect

_CLAUDE_DIR = Path.home() / ".claude" / "projects"


def _project_name_from_dir(dirname: str) -> str:
    """'-home-ubuntu-Developer-Ayush-my-project' → 'my-project'."""
    parts = dirname.lstrip("-").split("-")
    return "-".join(parts[-2:]) if len(parts) >= 2 else dirname


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            b.get("text", "") for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def _ms_to_epoch(ts) -> Optional[int]:
    if not isinstance(ts, (int, float)):
        return None
    ms = int(ts)
    return ms // 1000 if ms > 1_000_000_000_000 else ms


def _parse_session(path: Path) -> Optional[dict]:
    user_messages: list[str] = []
    ts_min = ts_max = None

    try:
        with open(path, errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Collect timestamps wherever they appear
                for ts_key in ("timestamp", "created_at"):
                    raw_ts = obj.get(ts_key)
                    if isinstance(raw_ts, str):
                        try:
                            dt = datetime.fromisoformat(raw_ts.replace("Z", "+00:00"))
                            raw_ts = int(dt.timestamp() * 1000)
                        except Exception:
                            raw_ts = None
                    epoch = _ms_to_epoch(raw_ts)
                    if epoch:
                        if ts_min is None or epoch < ts_min:
                            ts_min = epoch
                        if ts_max is None or epoch > ts_max:
                            ts_max = epoch

                if obj.get("type") == "user":
                    msg = obj.get("message", {})
                    if msg.get("role") == "user":
                        text = _extract_text(msg.get("content", "")).strip()
                        if len(text) > 10:
                            user_messages.append(text[:200])
    except Exception:
        return None

    if not user_messages:
        return None

    return {
        "session_id": path.stem,
        "first_message": user_messages[0],
        "message_count": len(user_messages),
        "started_at": ts_min,
        "ended_at": ts_max,
    }


def _dedup_key(session_id: str) -> str:
    return hashlib.sha256(f"claude_code:{session_id}".encode()).hexdigest()


def scan_claude_code(store, since: Optional[int] = None) -> int:
    """
    Scan ~/.claude/projects/ for new sessions.
    Returns count of new ai_session events imported.
    """
    if not can_collect("claude_code"):
        return 0
    if not _CLAUDE_DIR.exists():
        return 0

    imported = 0
    since_ts = since or 0

    for proj_dir in _CLAUDE_DIR.iterdir():
        if not proj_dir.is_dir():
            continue
        project_name = _project_name_from_dir(proj_dir.name)

        for session_file in sorted(proj_dir.glob("*.jsonl")):
            if int(session_file.stat().st_mtime) < since_ts:
                continue

            session = _parse_session(session_file)
            if not session:
                continue

            dedup = _dedup_key(session["session_id"])
            if store._conn.execute(
                "SELECT id FROM events WHERE source='claude_code' "
                "AND json_extract(content,'$.dedup')=?",
                (dedup,),
            ).fetchone():
                continue

            content = json.dumps({
                "project": project_name,
                "first_message": redact_sensitive_text(session["first_message"]),
                "message_count": session["message_count"],
                "session_id": session["session_id"],
                "dedup": dedup,
            })
            store.write_event(
                type="ai_session",
                source="claude_code",
                content=content,
                project=str(proj_dir),
                redacted=True,
            )
            imported += 1

    return imported
