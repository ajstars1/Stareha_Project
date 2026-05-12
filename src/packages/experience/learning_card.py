"""Build the learner-facing Learning Card."""

import json
import time
from collections import Counter
from pathlib import Path

from packages.core.db import Store


def _fmt_dur(seconds: int) -> str:
    minutes, _ = divmod(max(0, int(seconds)), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m" if hours else f"{minutes}m"


def _loads(value: str) -> dict:
    try:
        return json.loads(value)
    except Exception:
        return {}


def _session(store: Store, session_id: str | None = None) -> dict | None:
    if session_id:
        row = store._conn.execute("SELECT * FROM sessions WHERE id=?", (session_id,)).fetchone()
    else:
        row = store._conn.execute(
            "SELECT * FROM sessions WHERE status='ended' ORDER BY ended_at DESC LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def _session_events(store: Store, session: dict) -> list[dict]:
    started = session["started_at"]
    ended = session.get("ended_at") or int(time.time())
    rows = store._conn.execute(
        """SELECT * FROM events
           WHERE session_id=?
              OR (created_at BETWEEN ? AND ?)
           ORDER BY created_at ASC""",
        (session["id"], started, ended),
    ).fetchall()
    return [dict(r) for r in rows]


def _recent_candidates(store: Store, session: dict) -> list[dict]:
    started = session["started_at"]
    ended = session.get("ended_at") or int(time.time())
    project = session.get("project")
    params: list = [started, ended + 300]
    q = (
        "SELECT * FROM memory_candidates WHERE status='pending' "
        "AND created_at BETWEEN ? AND ?"
    )
    if project:
        q += " AND (project=? OR project IS NULL)"
        params.append(project)
    q += " ORDER BY confidence DESC LIMIT 5"
    return [dict(r) for r in store._conn.execute(q, params).fetchall()]


def build_learning_card(store: Store, session_id: str | None = None) -> dict | None:
    """Return a compact Learning Card for the latest or selected ended session."""
    session = _session(store, session_id)
    if not session:
        return None

    events = _session_events(store, session)
    command_events = []
    file_events = []
    notes = []
    for event in events:
        data = _loads(event["content"])
        if event["source"] == "terminal":
            command_events.append({**data, "created_at": event["created_at"]})
        elif event["source"] == "files":
            file_events.append({**data, "created_at": event["created_at"]})
        elif event["source"] == "manual":
            notes.append(data.get("text") or event["content"])

    failed = [c for c in command_events if int(c.get("exit") or 0) != 0]
    successful = [c for c in command_events if int(c.get("exit") or 0) == 0]
    edited_names = [f.get("name") or Path(f.get("path", "")).name for f in file_events]
    edited_exts = Counter(Path(name).suffix or "file" for name in edited_names if name)
    candidates = _recent_candidates(store, session)

    worked_on: list[str] = []
    if session.get("goal"):
        worked_on.append(session["goal"])
    if edited_exts:
        top_ext = ", ".join(f"{ext} x{count}" for ext, count in edited_exts.most_common(3))
        worked_on.append(f"Edited project files ({top_ext})")
    if command_events:
        worked_on.append(f"Ran {len(command_events)} terminal command(s)")

    stuck_on = []
    for cmd in failed[-3:]:
        if cmd.get("cmd"):
            stuck_on.append(cmd["cmd"])
    for note in notes:
        lowered = note.lower()
        if any(word in lowered for word in ("stuck", "confused", "error", "blocked")):
            stuck_on.append(note)

    what_worked = []
    for cmd in successful[-3:]:
        if cmd.get("cmd"):
            what_worked.append(cmd["cmd"])

    if failed:
        next_step = "Revisit the last failing command, then try one small fix and rerun it."
    elif candidates:
        next_step = "Review what Stareha noticed and save the useful patterns."
    elif session.get("goal"):
        next_step = f"Continue with one focused practice task for: {session['goal']}"
    else:
        next_step = "Start the next session with a specific learning goal."

    evidence = []
    if command_events:
        evidence.append(f"{len(command_events)} command event(s)")
    if file_events:
        evidence.append(f"{len(file_events)} file activity event(s)")
    if notes:
        evidence.append(f"{len(notes)} note(s)")
    if candidates:
        evidence.append(f"{len(candidates)} thing(s) Stareha noticed")

    duration = (session.get("ended_at") or int(time.time())) - session["started_at"]
    project = session.get("project")
    return {
        "session_id": session["id"],
        "goal": session.get("goal") or "Learning session",
        "project": project,
        "project_name": Path(project).name if project else "unknown",
        "duration": _fmt_dur(duration),
        "worked_on": worked_on or ["No activity captured yet"],
        "stuck_on": stuck_on[:5],
        "what_worked": what_worked[-5:],
        "next_step": next_step,
        "evidence": evidence or ["Session timing only"],
        "notices": candidates,
    }


def format_learning_card_cli(card: dict) -> str:
    """Return a Rich-markup Learning Card."""
    lines = [
        "",
        "[bold]Learning Card[/bold]",
        f"[bold]Goal[/bold]  {card['goal']}",
        f"[bold]Project[/bold]  {card['project_name']}  [dim]({card['duration']})[/dim]",
        "",
        "[bold]Worked on[/bold]",
    ]
    lines.extend(f"  - {item}" for item in card["worked_on"][:5])

    if card.get("stuck_on"):
        lines.append("")
        lines.append("[bold]Stuck on[/bold]")
        lines.extend(f"  - {item}" for item in card["stuck_on"][:5])

    if card.get("what_worked"):
        lines.append("")
        lines.append("[bold]What worked[/bold]")
        lines.extend(f"  - $ {item}" for item in card["what_worked"][-5:])

    lines.extend([
        "",
        "[bold]Next step[/bold]",
        f"  -> {card['next_step']}",
        "",
        "[bold]Evidence[/bold]",
    ])
    lines.extend(f"  - {item}" for item in card["evidence"])
    lines.append("")
    return "\n".join(lines)
