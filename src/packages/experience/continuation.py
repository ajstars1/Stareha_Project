"""Build the beginner-facing continue experience."""

from __future__ import annotations

import json

from packages.core.db import Store
from packages.experience.learning_card import build_learning_card
from packages.guidance.prep import get_pending


def _latest_successful_command(store: Store, session_id: str) -> str | None:
    session = store._conn.execute(
        "SELECT started_at, ended_at FROM sessions WHERE id=?", (session_id,)
    ).fetchone()
    params: list = [session_id]
    q = "SELECT content FROM events WHERE session_id=?"
    if session:
        q += " OR (created_at BETWEEN ? AND ?)"
        params.extend([session["started_at"], session["ended_at"] or session["started_at"]])
    q += " ORDER BY created_at DESC LIMIT 100"
    rows = store._conn.execute(
        q,
        params,
    ).fetchall()
    for row in rows:
        try:
            data = json.loads(row["content"])
        except Exception:
            continue
        if data.get("cmd") and int(data.get("exit") or 0) == 0:
            return data["cmd"]
    return None


def _step_key(step: str) -> str:
    key = step.lower().strip()
    for prefix in (
        "continue with one focused practice task for:",
        "continue:",
        "practice:",
    ):
        if key.startswith(prefix):
            key = key[len(prefix):].strip()
    return key


def build_continue_plan(store: Store) -> dict | None:
    card = build_learning_card(store)
    if not card:
        return None
    pending = get_pending(store, gtype="briefing")
    last_command = _latest_successful_command(store, card["session_id"])
    steps = [card["next_step"]]
    if pending:
        content = pending[0].get("content") or {}
        for step in content.get("next_steps", [])[:2]:
            if _step_key(step) not in {_step_key(existing) for existing in steps}:
                steps.append(step)
    return {
        "goal": card["goal"],
        "project_name": card["project_name"],
        "project": card["project"],
        "last_successful_command": last_command,
        "steps": steps[:3],
        "evidence": card["evidence"],
    }


def format_continue_plan_cli(plan: dict) -> str:
    lines = [
        "",
        "[bold]Continue Learning[/bold]",
        f"[bold]Last goal[/bold]  {plan['goal']}",
        f"[bold]Project[/bold]  {plan['project_name']}",
    ]
    if plan.get("last_successful_command"):
        lines.append(f"[bold]Last command that worked[/bold]  $ {plan['last_successful_command']}")
    lines.append("")
    lines.append("[bold]Next[/bold]")
    for index, step in enumerate(plan["steps"], 1):
        lines.append(f"  {index}. {step}")
    lines.append("")
    return "\n".join(lines)
