"""
Guidance prep orchestrator — Stage 4.

Coordinates detection, briefing, quiz, and exercise generation.
Stores results in prepared_guidance table.
Provides helpers for the CLI to retrieve and mark guidance.
"""
import json
import re
import time
import uuid
from typing import Optional

from packages.core.db import Store
from packages.guidance.detector import detect_weak_concepts
from packages.guidance.briefing import build_work_briefing, build_learning_briefing
from packages.guidance.quiz import generate_quiz


# ── Storage helpers ───────────────────────────────────────────────────────────

def _store_guidance(store: Store, gtype: str, title: str, content: dict,
                    generated_by: str = "scripts",
                    session_id: Optional[str] = None) -> str:
    gid = str(uuid.uuid4())
    store._conn.execute(
        """INSERT INTO prepared_guidance
           (id, type, title, content, status, generated_by, prepared_at, session_id)
           VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)""",
        (gid, gtype, title, json.dumps(content), generated_by, int(time.time()), session_id),
    )
    store._conn.commit()
    return gid


def get_pending(store: Store, gtype: Optional[str] = None) -> list[dict]:
    """Return pending guidance items, newest first."""
    q = "SELECT * FROM prepared_guidance WHERE status='pending'"
    params: list = []
    if gtype:
        q += " AND type=?"
        params.append(gtype)
    q += " ORDER BY prepared_at DESC"
    rows = store._conn.execute(q, params).fetchall()
    results = []
    for row in rows:
        r = dict(row)
        try:
            r["content"] = json.loads(r["content"])
        except Exception:
            pass
        results.append(r)
    return results


def get_all_guidance(store: Store, limit: int = 20) -> list[dict]:
    """Return all guidance items for the list view."""
    rows = store._conn.execute(
        "SELECT * FROM prepared_guidance ORDER BY prepared_at DESC LIMIT ?", (limit,)
    ).fetchall()
    results = []
    for row in rows:
        r = dict(row)
        try:
            r["content"] = json.loads(r["content"])
        except Exception:
            pass
        results.append(r)
    return results


def mark_delivered(store: Store, guidance_id: str) -> None:
    store._conn.execute(
        "UPDATE prepared_guidance SET status='delivered', delivered_at=? WHERE id=?",
        (int(time.time()), guidance_id),
    )
    store._conn.commit()


def mark_completed(store: Store, guidance_id: str) -> None:
    store._conn.execute(
        "UPDATE prepared_guidance SET status='completed' WHERE id=?", (guidance_id,)
    )
    store._conn.commit()


def mark_skipped(store: Store, guidance_id: str) -> None:
    store._conn.execute(
        "UPDATE prepared_guidance SET status='skipped' WHERE id=?", (guidance_id,)
    )
    store._conn.commit()


def update_content(store: Store, guidance_id: str, content: dict) -> None:
    store._conn.execute(
        "UPDATE prepared_guidance SET content=? WHERE id=?",
        (json.dumps(content), guidance_id),
    )
    store._conn.commit()


# ── Session context ───────────────────────────────────────────────────────────

def _is_learning_session(session: Optional[dict]) -> bool:
    if not session:
        return False
    goal = (session.get("goal") or "").lower()
    learn_words = ["learn", "study", "practice", "understand", "explore", "course"]
    return any(w in goal for w in learn_words)


def _last_session(store: Store) -> Optional[dict]:
    row = store._conn.execute(
        "SELECT * FROM sessions WHERE status='ended' ORDER BY ended_at DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None


# ── Main orchestrator ─────────────────────────────────────────────────────────

def prepare_guidance(store: Store, *, with_quiz: bool = False,
                     session_id: Optional[str] = None) -> list[str]:
    """
    Run the full guidance preparation pipeline.

    Steps:
      1. Detect weak concepts
      2. Build briefing (work or learning, based on last session goal)
      3. Optionally generate a quiz for the top weak concept

    Returns list of guidance IDs created.
    """
    created: list[str] = []
    last_session = _last_session(store)
    is_learning = _is_learning_session(last_session)

    # 1. Weak concept detection (always runs)
    weak = detect_weak_concepts(store)

    # 2. Briefing
    if is_learning:
        briefing = build_learning_briefing(store, weak)
        goal = last_session["goal"] if last_session else "learning"
        title = f"Learning Briefing: {goal}"
    else:
        briefing = build_work_briefing(store)
        proj = briefing.get("primary_project") or "work session"
        title = f"Work Briefing: {proj}"

    bid = _store_guidance(store, "briefing", title, briefing,
                          generated_by="scripts", session_id=session_id)
    created.append(bid)

    # 3. Quiz (optional, top weak concept)
    if with_quiz and weak:
        top = weak[0]
        context = top["signals"][0] if top.get("signals") else ""
        level = "struggling" if top["score"] >= 0.60 else "beginner"
        quiz = generate_quiz(
            top["concept"], level=level, n=5,
            context=context, signals=top.get("signals", []),
        )
        generated_by = quiz.pop("generated_by", "scripts")
        qtitle = f"Quiz: {top['concept']}"
        qid = _store_guidance(store, "quiz", qtitle, quiz,
                              generated_by=generated_by, session_id=session_id)
        created.append(qid)

    return created


# ── User notes ────────────────────────────────────────────────────────────────

def add_note(store: Store, text: str, tags: Optional[list[str]] = None) -> str:
    """Write a user_note event and store in user_notes table."""
    nid = str(uuid.uuid4())
    store._conn.execute(
        "INSERT INTO user_notes (id, content, tags, created_at) VALUES (?,?,?,?)",
        (nid, text, json.dumps(tags or []), int(time.time())),
    )
    # Also write as an event so it appears in ledger
    store.write_event(
        type="user_note",
        source="manual",
        content=json.dumps({"text": text, "tags": tags or []}),
        redacted=False,
    )
    store._conn.commit()
    return nid
