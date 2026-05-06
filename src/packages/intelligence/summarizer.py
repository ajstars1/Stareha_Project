"""
Session and event summarizer — Stage 5.

Uses the intelligence router to generate natural-language summaries.
Always falls back gracefully — returns None when no LLM is available.

Privacy: only processed, redacted summaries are passed to LLMs.
Never raw events, file contents, or full command history.
"""
import json
from typing import Optional

from packages.core.db import Store
from packages.intelligence import router
from packages.intelligence.prompts import get as get_prompt


def _fmt_dur(seconds: int) -> str:
    m, _ = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m" if h else f"{m}m"


def summarize_session(store: Store, session_id: str) -> Optional[str]:
    """
    Generate a 2-3 sentence summary of a session using the router.

    Input to LLM: goal, duration, top-10 unique commands, event counts.
    NOT sent: raw terminal output, file contents, secrets.

    Returns None if no LLM layer is available.
    """
    row = store._conn.execute(
        "SELECT * FROM sessions WHERE id=?", (session_id,)
    ).fetchone()
    if not row:
        return None

    import time
    ended = row["ended_at"] or int(time.time())
    duration = _fmt_dur(ended - row["started_at"])
    goal = row["goal"] or "no explicit goal"

    # Top unique commands — already redacted before storage
    events = store._conn.execute(
        "SELECT content FROM events WHERE session_id=? AND source='terminal' LIMIT 100",
        (session_id,),
    ).fetchall()
    cmds: list[str] = []
    for e in events:
        try:
            data = json.loads(e[0])
            cmd = data.get("cmd", "")
            if cmd and cmd not in cmds:
                cmds.append(cmd)
        except Exception:
            pass

    event_count = store._conn.execute(
        "SELECT count(*) FROM events WHERE session_id=?", (session_id,)
    ).fetchone()[0]

    top_cmds = ", ".join(f"`{c}`" for c in cmds[:10]) or "none"

    prompt = get_prompt(
        "session-summary",
        goal=goal,
        duration=duration,
        event_count=event_count,
        cmd_count=len(cmds),
        commands=top_cmds,
    )

    result, layer = router.generate(prompt, allow_cloud=False, timeout=30.0)
    return result


def enrich_memory_candidate(content: str, project: Optional[str], count: int) -> Optional[str]:
    """
    Use local LLM to rewrite a script-generated memory as cleaner natural language.

    Input: the raw pattern text, project name, occurrence count.
    Returns enriched text or None if local LLM unavailable (use original).
    """
    from pathlib import Path
    proj_name = Path(project).name if project else "general"

    prompt = get_prompt(
        "memory-enrichment",
        raw_pattern=content,
        project=proj_name,
        count=count,
    )

    result, layer = router.generate(
        prompt, allow_cloud=False, timeout=20.0
    )
    if result and len(result) < 300:  # sanity check — reject runaway output
        return result
    return None
