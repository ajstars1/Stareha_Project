"""
Weak concept detector — Stage 4.

Deterministic signal analysis over events, memories, and user notes.
No LLM. Returns ranked list of weak areas for the guidance system to act on.

Signal hierarchy (highest to lowest weight):
  explicit_note  — user said "struggling with X"          → 0.95
  error_fix      — known error-fix memory for a tool       → 0.35 / occurrence
  repeated_fail  — same command failed 2+ times            → 0.20 / failure (cap 3)
  session_goal   — user stated a learning goal             → 0.10 (signals intent, not struggle)
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

from packages.core.db import Store


# ── Concept name extraction ───────────────────────────────────────────────────

_TOOL_CONCEPTS = {
    "npm": "Node.js / npm",
    "npx": "Node.js / npx",
    "pnpm": "pnpm",
    "bun": "Bun.js",
    "yarn": "Yarn",
    "python": "Python",
    "python3": "Python",
    "pip": "pip / Python packages",
    "pip3": "pip / Python packages",
    "git": "Git",
    "docker": "Docker",
    "kubectl": "Kubernetes",
    "cargo": "Rust / Cargo",
    "go": "Go",
    "make": "Make / build system",
    "gradle": "Gradle",
    "mvn": "Maven",
}


def _cmd_to_concept(cmd: str) -> str:
    """Map a raw command to a human-readable concept name."""
    base = cmd.strip().split()[0] if cmd.strip() else cmd
    if base in _TOOL_CONCEPTS:
        return _TOOL_CONCEPTS[base]
    # Include the sub-command for better specificity
    parts = cmd.strip().split()
    if len(parts) >= 2 and parts[0] in _TOOL_CONCEPTS:
        return f"{_TOOL_CONCEPTS[parts[0]]} ({' '.join(parts[1:3])})"
    return cmd[:40] if len(cmd) > 40 else cmd


def _extract_fail_cmd_from_memory(content: str) -> Optional[str]:
    """Extract the failing command from an error_fix memory's content string."""
    m = re.search(r'after `([^`]+)` fails', content)
    return m.group(1) if m else None


# ── Signal collection ─────────────────────────────────────────────────────────

def _signals_from_notes(store: Store) -> dict[str, dict]:
    """User notes tagged with 'struggling' → highest-weight signal."""
    weak: dict[str, dict] = {}
    try:
        rows = store._conn.execute(
            "SELECT content, tags FROM user_notes ORDER BY created_at DESC"
        ).fetchall()
    except Exception:
        return weak

    struggling_re = re.compile(
        r"(?:struggling|confused|don.t understand|stuck on|can.t figure out|hard time with)\s+(?:with\s+)?(.+)",
        re.IGNORECASE,
    )

    for row in rows:
        m = struggling_re.search(row[0])
        if not m:
            continue
        concept = m.group(1).strip().rstrip(".!?")
        if concept not in weak:
            weak[concept] = {"concept": concept, "score": 0.0, "signals": []}
        weak[concept]["score"] = max(weak[concept]["score"], 0.95)
        weak[concept]["signals"].append(f'You noted: "{row[0][:60]}"')

    return weak


def _signals_from_error_fix_memories(store: Store) -> dict[str, dict]:
    """error_fix memories → the failing command is a known weak area."""
    weak: dict[str, dict] = {}
    try:
        rows = store._conn.execute(
            "SELECT content, project, confidence FROM memories WHERE type='error_fix'"
        ).fetchall()
    except Exception:
        return weak

    for row in rows:
        fail_cmd = _extract_fail_cmd_from_memory(row[0])
        if not fail_cmd:
            continue
        concept = _cmd_to_concept(fail_cmd)
        if concept not in weak:
            weak[concept] = {"concept": concept, "score": 0.0, "signals": []}
        boost = 0.35 * row[2]  # scale by confidence of the memory
        weak[concept]["score"] = min(weak[concept]["score"] + boost, 0.95)
        proj = Path(row[1]).name if row[1] else None
        sig = f"Known error-fix pattern: `{fail_cmd}`"
        if proj:
            sig += f" in {proj}"
        if sig not in weak[concept]["signals"]:
            weak[concept]["signals"].append(sig)

    return weak


def _signals_from_repeated_failures(store: Store) -> dict[str, dict]:
    """Events with exit != 0 — same base command failing 2+ times."""
    weak: dict[str, dict] = {}
    fail_counts: Counter = Counter()
    fail_signals: dict[str, list] = defaultdict(list)

    try:
        rows = store._conn.execute(
            "SELECT content, project FROM events WHERE source='terminal'"
        ).fetchall()
    except Exception:
        return weak

    for row in rows:
        try:
            data = json.loads(row[0])
        except Exception:
            continue
        exit_code = data.get("exit")
        if exit_code is None or exit_code == 0:
            continue
        cmd = data.get("cmd", "").strip()
        if not cmd:
            continue
        base = cmd.split()[0]
        fail_counts[base] += 1
        proj = Path(row[1]).name if row[1] else None
        sig = f"`{cmd[:40]}` failed (exit {exit_code})"
        if proj:
            sig += f" in {proj}"
        if sig not in fail_signals[base]:
            fail_signals[base].append(sig)

    for base, count in fail_counts.items():
        if count < 2:
            continue
        concept = _cmd_to_concept(base)
        if concept not in weak:
            weak[concept] = {"concept": concept, "score": 0.0, "signals": []}
        boost = min(count * 0.20, 0.60)
        weak[concept]["score"] = min(weak[concept]["score"] + boost, 0.90)
        for sig in fail_signals[base][:3]:
            if sig not in weak[concept]["signals"]:
                weak[concept]["signals"].append(sig)

    return weak


def _signals_from_session_goals(store: Store) -> dict[str, dict]:
    """Session goals ('learn X') → what the user is actively working on."""
    goals: dict[str, dict] = {}
    try:
        rows = store._conn.execute(
            "SELECT goal FROM sessions WHERE goal IS NOT NULL ORDER BY started_at DESC LIMIT 5"
        ).fetchall()
    except Exception:
        return goals

    learn_re = re.compile(r"(?:learn|study|practice|understand|explore)\s+(.+)", re.IGNORECASE)

    for row in rows:
        goal = row[0] or ""
        m = learn_re.search(goal)
        if not m:
            continue
        concept = m.group(1).strip().rstrip(".!?")
        if concept not in goals:
            goals[concept] = {"concept": concept, "score": 0.10, "signals": [f'Session goal: "{goal}"']}

    return goals


# ── Main entry point ──────────────────────────────────────────────────────────

def detect_weak_concepts(store: Store) -> list[dict]:
    """
    Run all signal collectors and merge results.
    Returns list of weak concepts sorted by score descending.
    """
    merged: dict[str, dict] = {}

    for collector in [
        _signals_from_notes,
        _signals_from_error_fix_memories,
        _signals_from_repeated_failures,
        _signals_from_session_goals,
    ]:
        for concept, data in collector(store).items():
            if concept not in merged:
                merged[concept] = {"concept": concept, "score": 0.0, "signals": []}
            merged[concept]["score"] = min(merged[concept]["score"] + data["score"], 0.95)
            for sig in data["signals"]:
                if sig not in merged[concept]["signals"]:
                    merged[concept]["signals"].append(sig)

    results = sorted(merged.values(), key=lambda x: x["score"], reverse=True)
    # Only surface concepts with meaningful score
    return [r for r in results if r["score"] >= 0.10]


def detect_strong_concepts(store: Store) -> list[str]:
    """
    Return concepts where the user seems proficient.
    (High-confidence command_pattern memories with no error signals.)
    """
    try:
        rows = store._conn.execute(
            "SELECT content FROM memories WHERE type='command_pattern' AND confidence >= 0.80"
        ).fetchall()
    except Exception:
        return []

    strong = []
    for row in rows:
        # Extract the command from "you often run `cmd`"
        m = re.search(r'run `([^`]+)`', row[0])
        if m:
            strong.append(_cmd_to_concept(m.group(1)))
    return list(dict.fromkeys(strong))  # deduplicate, preserve order
