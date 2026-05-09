"""Beginner-facing review flow for memory candidates."""

from __future__ import annotations

import click
from rich.console import Console

from packages.core.db import Store
from packages.memory.manager import approve_candidate, reject_candidate


def pending_notices(store: Store, *, since: int | None = None,
                    project: str | None = None, limit: int = 5) -> list[dict]:
    params: list = []
    q = "SELECT * FROM memory_candidates WHERE status='pending'"
    if since:
        q += " AND created_at >= ?"
        params.append(since)
    if project:
        q += " AND (project=? OR project IS NULL)"
        params.append(project)
    q += " ORDER BY confidence DESC LIMIT ?"
    params.append(limit)
    return [dict(r) for r in store._conn.execute(q, params).fetchall()]


def review_notices(
    store: Store,
    console: Console,
    *,
    since: int | None = None,
    project: str | None = None,
) -> None:
    rows = pending_notices(store, since=since, project=project)
    if not rows:
        return
    console.print("\n[bold]What Stareha noticed[/bold]")
    for index, row in enumerate(rows, 1):
        console.print(f"\n[bold]{index}.[/bold] {row['content']}")
        console.print(f"[dim]Why: {row['type']} · confidence {row['confidence']:.0%}[/dim]")
        action = click.prompt(
            "Action",
            type=click.Choice(["s", "i", "e", "k"], case_sensitive=False),
            default="k",
            show_default=True,
            prompt_suffix=" (s)ave (i)gnore (e)dit s(k)ip: ",
        )
        if action == "s":
            approve_candidate(store, row["id"])
            console.print("[green]Saved.[/green]")
        elif action == "i":
            reject_candidate(store, row["id"])
            console.print("[yellow]Ignored.[/yellow]")
        elif action == "e":
            edited = click.edit(row["content"])
            if edited and edited.strip() != row["content"]:
                approve_candidate(store, row["id"], edited.strip())
                console.print("[green]Edited and saved.[/green]")
            else:
                console.print("[dim]Skipped.[/dim]")

