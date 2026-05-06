"""
Learning Ledger — Stage 3 trust layer.

Responsibilities:
  - Create and complete learning_run records
  - Compute what-did-you-learn summaries for any time period
  - Analyse feedback to gate future candidate confidence
  - Provide the full audit view for `stareha ledger`
"""
import time
import uuid
from datetime import date, datetime, timedelta
from typing import Optional

from packages.core.db import Store


# ── Learning run lifecycle ────────────────────────────────────────────────────

def create_run(store: Store, session_id: Optional[str] = None) -> str:
    run_id = str(uuid.uuid4())
    store._conn.execute(
        """INSERT INTO learning_runs
           (id, session_id, started_at, status, model_used)
           VALUES (?, ?, ?, 'running', 'pattern_extractor')""",
        (run_id, session_id, int(time.time())),
    )
    store._conn.commit()
    return run_id


def complete_run(store: Store, run_id: str, events_processed: int,
                 candidates_generated: int) -> None:
    store._conn.execute(
        """UPDATE learning_runs
           SET completed_at=?, events_processed=?, candidates_generated=?, status='completed'
           WHERE id=?""",
        (int(time.time()), events_processed, candidates_generated, run_id),
    )
    store._conn.commit()


def fail_run(store: Store, run_id: str) -> None:
    store._conn.execute(
        "UPDATE learning_runs SET completed_at=?, status='failed' WHERE id=?",
        (int(time.time()), run_id),
    )
    store._conn.commit()


# ── Feedback analysis ─────────────────────────────────────────────────────────

def get_rejection_counts(store: Store) -> dict[tuple[str, str], int]:
    """
    Return rejection count per (type, source) pair.
    Used by the learning runner to raise the confidence bar for
    pattern types the user keeps rejecting.
    """
    rows = store._conn.execute(
        """SELECT mc.type, mc.source, count(*) AS cnt
           FROM memory_feedback mf
           JOIN memory_candidates mc ON mf.candidate_id = mc.id
           WHERE mf.action = 'rejected'
           GROUP BY mc.type, mc.source""",
    ).fetchall()
    return {(r[0], r[1]): r[2] for r in rows}


def feedback_stats(store: Store) -> dict:
    total = store._conn.execute("SELECT count(*) FROM memory_feedback").fetchone()[0]
    if not total:
        return {"total": 0, "approved": 0, "rejected": 0, "edited": 0, "approval_rate": None}
    by_action = {
        r[0]: r[1]
        for r in store._conn.execute(
            "SELECT action, count(*) FROM memory_feedback GROUP BY action"
        ).fetchall()
    }
    approved = by_action.get("approved", 0)
    rejected = by_action.get("rejected", 0)
    edited   = by_action.get("edited", 0)
    return {
        "total": total,
        "approved": approved,
        "rejected": rejected,
        "edited": edited,
        "approval_rate": round((approved + edited) / total, 2) if total else None,
    }


# ── What-did-you-learn summary ────────────────────────────────────────────────

def _period_bounds(store: Store, period: str) -> tuple[int, Optional[int], str]:
    """Return (since_ts, until_ts_or_None, human_label) for the requested period."""
    now = int(time.time())
    today_start = int(datetime.combine(date.today(), datetime.min.time()).timestamp())

    if period == "today":
        return today_start, None, f"today ({date.today().strftime('%Y-%m-%d')})"

    if period == "yesterday":
        yesterday = date.today() - timedelta(days=1)
        return (
            int(datetime.combine(yesterday, datetime.min.time()).timestamp()),
            today_start,
            f"yesterday ({yesterday.strftime('%Y-%m-%d')})",
        )

    if period == "week":
        week_start = today_start - 7 * 86400
        return week_start, None, "this week"

    # "session" — use most recently ended session
    last = store._conn.execute(
        "SELECT * FROM sessions WHERE status='ended' ORDER BY ended_at DESC LIMIT 1"
    ).fetchone()
    if last:
        goal = last["goal"] or "unnamed"
        label = f'session "{goal}" ({_fmt_dur(now - last["started_at"])})'
        return last["started_at"], last["ended_at"] or now, label

    return today_start, None, "today (no session found)"


def _fmt_dur(seconds: int) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h {m}m" if h else f"{m}m"


def what_did_you_learn(store: Store, period: str = "today") -> dict:
    """
    Build the data for `stareha what-did-you-learn`.
    Returns a dict with: period, events_by_source, candidates, approved, runs, pending.
    """
    since, until, label = _period_bounds(store, period)

    def _q(base: str, col: str, extra_params: list) -> list:
        q = f"{base} AND {col} >= ?"
        params = extra_params + [since]
        if until is not None:
            q += f" AND {col} < ?"
            params.append(until)
        return params, q

    # Events
    params, q = _q(
        "SELECT source, count(*) AS cnt FROM events WHERE 1=1", "created_at", []
    )
    q += " GROUP BY source"
    events_by_source = {r[0]: r[1] for r in store._conn.execute(q, params).fetchall()}
    total_events = sum(events_by_source.values())

    # Candidates generated in period
    params, q = _q("SELECT * FROM memory_candidates WHERE 1=1", "created_at", [])
    q += " ORDER BY confidence DESC"
    candidates = [dict(r) for r in store._conn.execute(q, params).fetchall()]

    # Memories approved in period
    params, q = _q("SELECT * FROM memories WHERE 1=1", "approved_at", [])
    q += " ORDER BY approved_at DESC"
    approved = [dict(r) for r in store._conn.execute(q, params).fetchall()]

    # Learning runs in period
    params, q = _q("SELECT * FROM learning_runs WHERE 1=1", "started_at", [])
    q += " ORDER BY started_at DESC"
    runs = [dict(r) for r in store._conn.execute(q, params).fetchall()]

    pending = store._conn.execute(
        "SELECT count(*) FROM memory_candidates WHERE status='pending'"
    ).fetchone()[0]

    return {
        "period": label,
        "total_events": total_events,
        "events_by_source": events_by_source,
        "candidates": candidates,
        "approved": approved,
        "runs": runs,
        "pending_in_inbox": pending,
    }


# ── Audit view ────────────────────────────────────────────────────────────────

def recent_runs(store: Store, limit: int = 10) -> list[dict]:
    rows = store._conn.execute(
        "SELECT * FROM learning_runs ORDER BY started_at DESC LIMIT ?", (limit,)
    ).fetchall()
    return [dict(r) for r in rows]
