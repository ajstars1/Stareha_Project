"""
Terminal history scanner.
Copy pattern from: hermes-agent/agent/shell_hooks.py
Reads ~/.zsh_history or ~/.bash_history, deduplicates, redacts, stores.
"""
import hashlib
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from packages.shared.redact import redact_sensitive_text
from packages.permissions import can_collect


def _detect_shell_history() -> list[Path]:
    shell = os.environ.get("SHELL", "")
    candidates = []
    if "zsh" in shell:
        candidates.append(Path.home() / ".zsh_history")
    if "bash" in shell:
        candidates.append(Path.home() / ".bash_history")
    # fallback: try both
    if not candidates:
        candidates = [Path.home() / ".zsh_history", Path.home() / ".bash_history"]
    return [p for p in candidates if p.exists()]


def _parse_zsh_history(path: Path) -> list[dict]:
    """Parse extended zsh history format: `: timestamp:elapsed;command`"""
    entries = []
    content = path.read_text(errors="replace")
    pattern = re.compile(r"^: (\d+):\d+;(.+)$", re.MULTILINE)
    for m in pattern.finditer(content):
        entries.append({"ts": int(m.group(1)), "cmd": m.group(2).strip()})
    if not entries:
        # plain format fallback
        for line in content.splitlines():
            line = line.strip()
            if line:
                entries.append({"ts": int(time.time()), "cmd": line})
    return entries


def _parse_bash_history(path: Path) -> list[dict]:
    entries = []
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            entries.append({"ts": int(time.time()), "cmd": line})
    return entries


def _dedup_key(cmd: str, ts: int) -> str:
    return hashlib.sha256(f"{cmd}:{ts}".encode()).hexdigest()


def scan_history(store, since: Optional[datetime] = None) -> int:
    """
    Scan shell history and import new events into store.
    Returns count of new events imported.
    """
    if not can_collect("terminal"):
        return 0

    imported = 0
    since_ts = int(since.timestamp()) if since else 0

    for history_file in _detect_shell_history():
        is_zsh = "zsh" in str(history_file)
        entries = _parse_zsh_history(history_file) if is_zsh else _parse_bash_history(history_file)

        for entry in entries:
            if entry["ts"] < since_ts:
                continue

            content = redact_sensitive_text(entry["cmd"])

            dedup = _dedup_key(content, entry["ts"])
            existing = store._conn.execute(
                "SELECT id FROM events WHERE source='terminal' AND json_extract(content,'$.dedup')=?",
                (dedup,)
            ).fetchone()
            if existing:
                continue

            import json
            store.write_event(
                type="command_run",
                source="terminal",
                content=json.dumps({"cmd": content, "ts": entry["ts"], "dedup": dedup}),
                redacted=True,
            )
            imported += 1

    return imported
