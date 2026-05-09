"""Home screen for the no-argument `stareha` command."""

from __future__ import annotations

import time
from pathlib import Path

from packages.core.db import Store
from packages.experience.learning_card import build_learning_card


def build_home(store: Store) -> dict:
    active = store.get_active_session()
    pending = store._conn.execute(
        "SELECT count(*) FROM memory_candidates WHERE status='pending'"
    ).fetchone()[0]
    approved = store._conn.execute("SELECT count(*) FROM memories").fetchone()[0]
    events_today = store.count_events(since=int(time.time()) - 86400)
    card = build_learning_card(store)
    return {
        "active": dict(active) if active else None,
        "pending": pending,
        "approved": approved,
        "events_today": events_today,
        "last_card": card,
    }


def format_home_cli(home: dict) -> str:
    lines = ["", "[bold]Stareha Learn[/bold]", "[dim]Never restart your learning from zero.[/dim]", ""]
    active = home.get("active")
    if active:
        elapsed = int((time.time() - active["started_at"]) / 60)
        project = Path(active["project"]).name if active.get("project") else "unknown project"
        lines.append(f"[bold green]Learning now[/bold green]  {active.get('goal') or 'No goal'}")
        lines.append(f"[dim]{project} · {elapsed}m active[/dim]")
        lines.append("")
        lines.append("Next command: [bold]stareha done[/bold]")
    else:
        card = home.get("last_card")
        if card:
            lines.append(f"[bold]Last session[/bold]  {card['goal']}")
            lines.append(f"[dim]{card['project_name']} · next: {card['next_step']}[/dim]")
            lines.append("")
            lines.append("Next command: [bold]stareha continue[/bold]")
        else:
            lines.append("Start with: [bold]stareha learn \"React forms\"[/bold]")

    lines.append("")
    lines.append(
        f"[dim]{home['events_today']} events today · "
        f"{home['pending']} noticed · {home['approved']} saved memories[/dim]"
    )
    lines.append("")
    return "\n".join(lines)

