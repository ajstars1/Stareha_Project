"""
Briefing builder — Stage 4.

Builds structured work and learning briefings from memories and events.
Fully deterministic — no LLM required.
"""
import json
import time
from datetime import date, datetime
from pathlib import Path
from typing import Optional

from packages.core.db import Store
from packages.guidance.detector import detect_weak_concepts, detect_strong_concepts


def _fmt_ts(ts: int) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def _fmt_dur(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m" if h else f"{m}m"


def _last_ended_session(store: Store) -> Optional[dict]:
    row = store._conn.execute(
        "SELECT * FROM sessions WHERE status='ended' ORDER BY ended_at DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


def _active_projects(store: Store) -> list[dict]:
    """Project context memories — what projects are known."""
    rows = store._conn.execute(
        "SELECT content, project, approved_at FROM memories "
        "WHERE type='project_context' ORDER BY approved_at DESC LIMIT 5"
    ).fetchall()
    return [dict(r) for r in rows]


def _command_patterns(store: Store, project: Optional[str] = None) -> list[dict]:
    """command_pattern memories — what the user habitually runs."""
    q = "SELECT content, project, confidence FROM memories WHERE type='command_pattern'"
    params: list = []
    if project:
        q += " AND (project LIKE ? OR project IS NULL)"
        params.append(f"%{project}%")
    q += " ORDER BY confidence DESC LIMIT 8"
    return [dict(r) for r in store._conn.execute(q, params).fetchall()]


def _error_fix_patterns(store: Store, project: Optional[str] = None) -> list[dict]:
    """error_fix memories — known error patterns and their fixes."""
    q = "SELECT content, project FROM memories WHERE type='error_fix'"
    params: list = []
    if project:
        q += " AND (project LIKE ? OR project IS NULL)"
        params.append(f"%{project}%")
    q += " ORDER BY approved_at DESC LIMIT 5"
    return [dict(r) for r in store._conn.execute(q, params).fetchall()]


def _recent_events_summary(store: Store, since: Optional[int] = None) -> dict:
    """Summarise recent events: counts by type and top commands."""
    q = "SELECT source, type, content FROM events WHERE 1=1"
    params: list = []
    if since:
        q += " AND created_at >= ?"
        params.append(since)
    q += " ORDER BY created_at DESC LIMIT 200"
    rows = store._conn.execute(q, params).fetchall()

    by_source: dict[str, int] = {}
    top_cmds: list[str] = []
    for row in rows:
        by_source[row[0]] = by_source.get(row[0], 0) + 1
        if row[0] == "terminal":
            try:
                data = json.loads(row[2])
                cmd = data.get("cmd", "")
                if cmd and cmd not in top_cmds:
                    top_cmds.append(cmd)
            except Exception:
                pass

    return {
        "total": len(rows),
        "by_source": by_source,
        "recent_commands": top_cmds[:10],
    }


# ── Work briefing ─────────────────────────────────────────────────────────────

def build_work_briefing(store: Store) -> dict:
    """
    Build a developer work briefing: last session context + what's known + next steps.
    Used when session goal is work-oriented (not "learn X").
    """
    last_session = _last_ended_session(store)
    projects = _active_projects(store)
    patterns = _command_patterns(store)
    errors = _error_fix_patterns(store)

    # Primary project: the one most recently active
    primary_project = None
    if projects:
        proj_path = projects[0].get("project")
        primary_project = Path(proj_path).name if proj_path else None

    # Recent events from last session
    since = last_session["started_at"] if last_session else None
    events = _recent_events_summary(store, since=since)

    # Build last-session section
    session_info = None
    if last_session:
        dur = _fmt_dur(
            (last_session["ended_at"] or int(time.time())) - last_session["started_at"]
        )
        session_info = {
            "goal": last_session.get("goal") or "no goal set",
            "ended_at": _fmt_ts(last_session["ended_at"]) if last_session.get("ended_at") else "?",
            "duration": dur,
            "events": events["total"],
        }

    # Active errors
    error_items = [e["content"] for e in errors]

    # Known command patterns for primary project
    pattern_items = [p["content"] for p in patterns if not p.get("project") or
                     (primary_project and primary_project in (p.get("project") or ""))][:5]

    # What to do next — deterministic heuristic
    next_steps = []
    if error_items:
        next_steps.append("Review and resolve the known error patterns below")
    if last_session and last_session.get("goal"):
        next_steps.append(f'Continue: {last_session["goal"]}')
    if not next_steps:
        next_steps.append("Run `stareha learn` after today's work to capture new patterns")

    return {
        "type": "work",
        "generated_at": int(time.time()),
        "primary_project": primary_project,
        "session": session_info,
        "known_patterns": pattern_items,
        "error_patterns": error_items,
        "next_steps": next_steps,
        "recent_commands": events["recent_commands"][:8],
    }


# ── Learning briefing ─────────────────────────────────────────────────────────

def build_learning_briefing(store: Store, weak_concepts: list[dict]) -> dict:
    """
    Build a learner briefing: what was worked on, what's weak, what to do next.
    Used when session goal is "learn X".
    """
    last_session = _last_ended_session(store)
    since = last_session["started_at"] if last_session else None
    events = _recent_events_summary(store, since=since)
    strong = detect_strong_concepts(store)

    session_info = None
    if last_session:
        dur = _fmt_dur(
            (last_session["ended_at"] or int(time.time())) - last_session["started_at"]
        )
        session_info = {
            "goal": last_session.get("goal") or "no goal set",
            "ended_at": _fmt_ts(last_session["ended_at"]) if last_session.get("ended_at") else "?",
            "duration": dur,
        }

    # Suggested next actions based on weak concepts
    next_steps = []
    for wc in weak_concepts[:2]:
        concept = wc["concept"]
        next_steps.append(f"Practice: {concept} (score {wc['score']:.0%})")
        if wc.get("signals"):
            next_steps.append(f"  Why: {wc['signals'][0]}")

    if not next_steps:
        if last_session and last_session.get("goal"):
            next_steps.append(f"Continue: {last_session['goal']}")
        else:
            next_steps.append("Set a session goal: `stareha session start \"learn X\"`")

    return {
        "type": "learning",
        "generated_at": int(time.time()),
        "session": session_info,
        "events_count": events["total"],
        "weak_concepts": weak_concepts[:3],
        "strong_concepts": strong[:3],
        "next_steps": next_steps,
    }


# ── Format for CLI ─────────────────────────────────────────────────────────────

def format_briefing_cli(briefing: dict) -> str:
    """Return a Rich-markup string suitable for console.print()."""
    lines: list[str] = []
    ts = datetime.fromtimestamp(briefing["generated_at"]).strftime("%Y-%m-%d")
    lines.append(f"\n[bold]Stareha Briefing[/bold]  [dim]{ts}[/dim]\n")

    if briefing["type"] == "work":
        proj = briefing.get("primary_project") or "unknown"
        lines.append(f"[bold]Project[/bold]  {proj}")

        sess = briefing.get("session")
        if sess:
            lines.append(
                f"[bold]Last session[/bold]  {sess['goal']}  "
                f"[dim]({sess['duration']} · ended {sess['ended_at']})[/dim]"
            )

        if briefing.get("known_patterns"):
            lines.append("\n[bold]Your usual workflow:[/bold]")
            for p in briefing["known_patterns"][:4]:
                lines.append(f"  [dim]·[/dim] {p}")

        if briefing.get("error_patterns"):
            lines.append("\n[bold]Known error patterns:[/bold]")
            for e in briefing["error_patterns"][:3]:
                lines.append(f"  [yellow]·[/yellow] {e}")

        if briefing.get("recent_commands"):
            lines.append("\n[bold]Recent commands:[/bold]")
            for c in briefing["recent_commands"][:5]:
                lines.append(f"  [dim]$[/dim] {c}")

        if briefing.get("next_steps"):
            lines.append("\n[bold]Suggested next:[/bold]")
            for s in briefing["next_steps"]:
                lines.append(f"  [green]→[/green] {s}")

    else:  # learning
        sess = briefing.get("session")
        if sess:
            lines.append(
                f"[bold]Last session[/bold]  {sess['goal']}  "
                f"[dim]({sess['duration']} · ended {sess['ended_at']})[/dim]"
            )

        wc = briefing.get("weak_concepts", [])
        if wc:
            lines.append("\n[bold]Areas to strengthen:[/bold]")
            for w in wc:
                sigs = "  ".join(w["signals"][:2]) if w.get("signals") else ""
                lines.append(f"  [yellow]·[/yellow] {w['concept']}  [dim](score {w['score']:.0%})[/dim]")
                if sigs:
                    lines.append(f"    [dim]{sigs}[/dim]")

        strong = briefing.get("strong_concepts", [])
        if strong:
            lines.append("\n[bold]Solid areas:[/bold]")
            for s in strong:
                lines.append(f"  [green]✓[/green] {s}")

        if briefing.get("next_steps"):
            lines.append("\n[bold]Today's plan:[/bold]")
            for i, s in enumerate(briefing["next_steps"], 1):
                lines.append(f"  {i}. {s}")

    lines.append("")
    return "\n".join(lines)
