"""
Memory manager — user operations on candidates and approved memories.

All mutations go through here so provenance is always maintained.
"""
import json
import time
import uuid
from typing import Optional

from packages.core.db import Store


# ── ID resolution (supports short prefix matching) ────────────────────────────

def _resolve_id(store: Store, table: str, partial_id: str) -> str:
    """Resolve a partial or full ID from a table. Raises ValueError if not found or ambiguous."""
    if len(partial_id) == 36:
        return partial_id
    rows = store._conn.execute(
        f"SELECT id FROM {table} WHERE id LIKE ?", (f"{partial_id}%",)
    ).fetchall()
    if not rows:
        raise ValueError(f"Not found in {table}: {partial_id}")
    if len(rows) > 1:
        raise ValueError(f"Ambiguous ID prefix '{partial_id}' — {len(rows)} matches. Use more characters.")
    return rows[0][0]


# ── Candidate operations ──────────────────────────────────────────────────────

def approve_candidate(store: Store, candidate_id: str,
                      edited_content: Optional[str] = None) -> str:
    """Approve a pending candidate. Returns the new memory ID."""
    candidate_id = _resolve_id(store, "memory_candidates", candidate_id)
    row = store._conn.execute(
        "SELECT * FROM memory_candidates WHERE id=?", (candidate_id,)
    ).fetchone()
    if not row:
        raise ValueError(f"Candidate not found: {candidate_id}")
    if row["status"] != "pending":
        raise ValueError(f"Candidate already actioned (status: {row['status']})")

    content = edited_content or row["content"]
    user_edited = 1 if edited_content else 0
    now = int(time.time())
    mid = str(uuid.uuid4())

    store._conn.execute(
        """INSERT INTO memories
           (id, content, type, source, project, evidence_ids, model_used,
            confidence, sensitivity, user_edited, learning_run_id, approved_at, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            mid, content, row["type"], row["source"], row["project"],
            row["evidence_ids"], row["model_used"], row["confidence"],
            row["sensitivity"], user_edited,
            row["learning_run_id"] if "learning_run_id" in row.keys() else None,
            now, now,
        ),
    )
    # Sync to FTS index
    store._conn.execute(
        "INSERT INTO memories_fts(rowid, content) "
        "SELECT rowid, content FROM memories WHERE id=?",
        (mid,),
    )
    store._conn.execute(
        "UPDATE memory_candidates SET status='approved' WHERE id=?", (candidate_id,)
    )
    _record_feedback(store, candidate_id, "approved", edited_content)
    store._conn.commit()
    return mid


def reject_candidate(store: Store, candidate_id: str) -> None:
    """Reject a pending candidate."""
    candidate_id = _resolve_id(store, "memory_candidates", candidate_id)
    row = store._conn.execute(
        "SELECT id FROM memory_candidates WHERE id=?", (candidate_id,)
    ).fetchone()
    if not row:
        raise ValueError(f"Candidate not found: {candidate_id}")
    store._conn.execute(
        "UPDATE memory_candidates SET status='rejected' WHERE id=?", (candidate_id,)
    )
    _record_feedback(store, candidate_id, "rejected")
    store._conn.commit()


# ── Memory operations ─────────────────────────────────────────────────────────

def forget_memory(store: Store, memory_id: str) -> None:
    """Hard-delete an approved memory and remove it from the FTS index."""
    memory_id = _resolve_id(store, "memories", memory_id)
    row = store._conn.execute(
        "SELECT rowid, content FROM memories WHERE id=?", (memory_id,)
    ).fetchone()
    if not row:
        raise ValueError(f"Memory not found: {memory_id}")
    # Remove from FTS first (needs rowid and content)
    store._conn.execute(
        "INSERT INTO memories_fts(memories_fts, rowid, content) VALUES ('delete',?,?)",
        (row["rowid"], row["content"]),
    )
    store._conn.execute("DELETE FROM memories WHERE id=?", (memory_id,))
    store._conn.commit()


def get_memory_why(store: Store, memory_id: str) -> dict:
    """Return the memory plus the raw events that caused it."""
    memory_id = _resolve_id(store, "memories", memory_id)
    memory = store._conn.execute(
        "SELECT * FROM memories WHERE id=?", (memory_id,)
    ).fetchone()
    if not memory:
        raise ValueError(f"Memory not found: {memory_id}")

    evidence_ids: list[str] = json.loads(memory["evidence_ids"] or "[]")
    events: list[dict] = []
    if evidence_ids:
        ph = ",".join("?" * len(evidence_ids))
        rows = store._conn.execute(
            f"SELECT id, type, source, content, created_at FROM events WHERE id IN ({ph})",
            evidence_ids,
        ).fetchall()
        events = [dict(r) for r in rows]

    return {"memory": dict(memory), "events": events}


def list_memories(
    store: Store,
    project: Optional[str] = None,
    type: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 50,
) -> list[dict]:
    q = "SELECT * FROM memories WHERE 1=1"
    params: list = []
    if project:
        q += " AND project LIKE ?"
        params.append(f"%{project}%")
    if type:
        q += " AND type=?"
        params.append(type)
    if source:
        q += " AND source=?"
        params.append(source)
    q += " ORDER BY approved_at DESC LIMIT ?"
    params.append(limit)
    return [dict(r) for r in store._conn.execute(q, params).fetchall()]


def search_memories(store: Store, query: str, limit: int = 20) -> list[dict]:
    """FTS5 search, with LIKE fallback."""
    try:
        rows = store._conn.execute(
            """SELECT m.* FROM memories m
               JOIN memories_fts f ON m.rowid = f.rowid
               WHERE memories_fts MATCH ?
               ORDER BY rank LIMIT ?""",
            (query, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    except Exception:
        rows = store._conn.execute(
            "SELECT * FROM memories WHERE content LIKE ? ORDER BY approved_at DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
        return [dict(r) for r in rows]


def get_sources(store: Store, memory_id: str) -> list[dict]:
    """Return the raw events used as evidence for this memory."""
    memory_id = _resolve_id(store, "memories", memory_id)
    row = store._conn.execute(
        "SELECT evidence_ids FROM memories WHERE id=?", (memory_id,)
    ).fetchone()
    if not row:
        raise ValueError(f"Memory not found: {memory_id}")

    ids: list[str] = json.loads(row["evidence_ids"] or "[]")
    if not ids:
        return []
    ph = ",".join("?" * len(ids))
    rows = store._conn.execute(
        f"SELECT * FROM events WHERE id IN ({ph})", ids
    ).fetchall()
    return [dict(r) for r in rows]


def memory_stats(store: Store) -> dict:
    """Return counts broken down by source and type."""
    total = store._conn.execute("SELECT count(*) FROM memories").fetchone()[0]
    pending = store._conn.execute(
        "SELECT count(*) FROM memory_candidates WHERE status='pending'"
    ).fetchone()[0]
    rejected = store._conn.execute(
        "SELECT count(*) FROM memory_candidates WHERE status='rejected'"
    ).fetchone()[0]

    by_source = {
        r[0]: r[1]
        for r in store._conn.execute(
            "SELECT source, count(*) FROM memories GROUP BY source"
        ).fetchall()
    }
    by_type = {
        r[0]: r[1]
        for r in store._conn.execute(
            "SELECT type, count(*) FROM memories GROUP BY type"
        ).fetchall()
    }
    events_total = store.count_events()

    return {
        "total": total,
        "pending": pending,
        "rejected": rejected,
        "by_source": by_source,
        "by_type": by_type,
        "events_total": events_total,
    }


# ── Internal ──────────────────────────────────────────────────────────────────

def _record_feedback(store: Store, candidate_id: str, action: str,
                     edit_content: Optional[str] = None) -> None:
    store._conn.execute(
        "INSERT INTO memory_feedback (id, candidate_id, action, edit_content, feedback_at) "
        "VALUES (?,?,?,?,?)",
        (str(uuid.uuid4()), candidate_id, action, edit_content, int(time.time())),
    )
