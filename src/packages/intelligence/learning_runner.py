"""
Learning runner — orchestrates pattern extraction and writes candidates to DB.

Every call creates a learning_run record for full provenance.
Rejection feedback raises the confidence threshold for frequently-rejected
pattern types, so Stareha stops proposing patterns the user ignores.
"""
import time
import uuid

from packages.core.db import Store
from packages.intelligence.ledger import (
    complete_run,
    create_run,
    fail_run,
    get_rejection_counts,
)
from packages.intelligence.scripts.pattern_extractor import run_all

LAST_RUN_KEY = "last_learning_run"
MIN_EVENTS = 5

# Feedback thresholds: if a (type, source) pair has been rejected this many times,
# only candidates with confidence above this bar pass through.
_REJECTION_BARS = {
    3: 0.75,
    6: 0.85,
    10: 0.95,  # essentially blocked
}


def _confidence_bar(rejection_count: int) -> float:
    """Return the minimum confidence required given how often this type has been rejected."""
    for threshold in sorted(_REJECTION_BARS, reverse=True):
        if rejection_count >= threshold:
            return _REJECTION_BARS[threshold]
    return 0.0  # no bar if not rejected enough times


def _load_events(store: Store, since: int | None = None) -> list[dict]:
    q = (
        "SELECT id, type, source, project, content, session_id, created_at "
        "FROM events WHERE 1=1"
    )
    params: list = []
    if since:
        q += " AND created_at >= ?"
        params.append(since)
    return [dict(r) for r in store._conn.execute(q, params).fetchall()]


def _existing_dedup_keys(store: Store) -> set[tuple]:
    # Block: pending (not yet reviewed) + approved (already accepted)
    # Allow re-surfacing rejected patterns — the user may have changed their mind
    rows = store._conn.execute(
        "SELECT type, source, project, content FROM memory_candidates "
        "WHERE status IN ('pending', 'approved')"
    ).fetchall()
    return {
        (r[0] or "", r[1] or "", r[2] or "", (r[3] or "")[:80])
        for r in rows
    }


def _enrich_candidates(candidates: list[dict]) -> None:
    """
    Optionally enrich script-generated candidate content with local LLM.
    Mutates candidates in-place. Silently skips if local LLM unavailable.
    Only enriches command_pattern and error_fix types (scripts output is terse).
    """
    from packages.core.config import load_config
    from packages.intelligence import local_llm
    config = load_config()
    if not local_llm.is_available(config.local_llm_base_url):
        return

    from packages.intelligence.summarizer import enrich_memory_candidate
    for c in candidates:
        if c.get("type") not in ("command_pattern", "error_fix"):
            continue
        import json as _json
        evidence = _json.loads(c.get("evidence_ids", "[]"))
        enriched = enrich_memory_candidate(
            c["content"], c.get("project"), len(evidence)
        )
        if enriched:
            c["content"] = enriched
            c["model_used"] = "local_llm"


def _filter_and_write_candidates(store: Store, candidates: list[dict], run_id: str,
                                 existing: set[tuple], rejection_counts: dict[tuple[str, str], int],
                                 now: int) -> int:
    """Filter candidates based on feedback thresholds and write them to DB."""
    written = 0
    for c in candidates:
        # Feedback gate: skip if confidence is below the bar for this (type, source)
        pair = (c.get("type") or "", c.get("source") or "")
        bar = _confidence_bar(rejection_counts.get(pair, 0))
        if c["confidence"] < bar:
            continue

        dedup = (
            c.get("type") or "",
            c.get("source") or "",
            c.get("project") or "",
            (c.get("content") or "")[:80],
        )
        if dedup in existing:
            continue
        existing.add(dedup)

        store._conn.execute(
            """INSERT INTO memory_candidates
               (id, content, type, source, project, evidence_ids, model_used,
                confidence, sensitivity, status, learning_run_id, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?)""",
            (
                str(uuid.uuid4()),
                c["content"],
                c["type"],
                c["source"],
                c.get("project"),
                c["evidence_ids"],
                c["model_used"],
                c["confidence"],
                c["sensitivity"],
                run_id,
                now,
            ),
        )
        written += 1
    return written


def run_learning(store: Store, *, force: bool = False,
                 session_id: str | None = None) -> int:
    """
    Run pattern extraction, write new candidates.
    Returns count of candidates written.

    Each call is logged in learning_runs for provenance.
    Rejection history gates which candidates are accepted.
    """
    since_raw = store.get_meta(LAST_RUN_KEY)
    since = int(since_raw) if since_raw and not force else None

    events = _load_events(store, since)
    if len(events) < MIN_EVENTS and not force:
        return 0

    run_id = create_run(store, session_id=session_id)

    try:
        candidates = run_all(events)
    except Exception:
        fail_run(store, run_id)
        raise

    if not candidates:
        complete_run(store, run_id, len(events), 0)
        store.set_meta(LAST_RUN_KEY, str(int(time.time())))
        return 0

    rejection_counts = get_rejection_counts(store)
    existing = _existing_dedup_keys(store)
    now = int(time.time())

    # Attempt local LLM enrichment if Ollama is available (non-blocking)
    _enrich_candidates(candidates)

    written = _filter_and_write_candidates(
        store, candidates, run_id, existing, rejection_counts, now
    )

    store._conn.commit()
    complete_run(store, run_id, len(events), written)
    store.set_meta(LAST_RUN_KEY, str(now))
    return written
