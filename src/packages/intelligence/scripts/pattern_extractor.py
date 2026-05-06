"""
Deterministic pattern extractors — Stage 2 workflow memory.

No LLM. Pure analysis of events already in SQLite.

Extractors:
  command_frequency  — commands repeated 3+ times in a project
  command_sequences  — A → B pairs that consistently co-occur
  error_fix_pairs    — failed_cmd followed by recovery_cmd
  project_context    — detect stack from filesystem markers
"""
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

# Base commands too trivial to store a memory for
_TRIVIAL_BASES = {
    "ls", "ll", "la", "l", "clear", "exit", "logout", "history",
    "pwd", "echo", "cat", "man", "help", "which", "type", "alias",
    "ps", "top", "htop", "df", "du", "free", "date", "whoami", "id",
    "less", "more", "head", "tail", "touch", "mkdir", "rmdir",
    "cp", "mv", "rm", "ln", "chmod", "chown",
    "ssh", "scp", "rsync",
    "grep", "find", "awk", "sed", "cut", "sort", "uniq", "wc",
    "curl", "wget",
}

# Minimum observations before generating a candidate
_MIN_FREQ = 3
_MIN_SEQ = 3
_MIN_FIX = 2


def _cmd_base(cmd: str) -> str:
    parts = cmd.strip().split()
    return parts[0] if parts else ""


def _is_trivial(cmd: str) -> bool:
    base = _cmd_base(cmd)
    if not base:
        return True
    if base in _TRIVIAL_BASES:
        return True
    # Single character commands
    if len(base) <= 1:
        return True
    # cd with no interesting args
    if base == "cd":
        return True
    return False


def _short_project(project: Optional[str]) -> Optional[str]:
    return Path(project).name if project else None


def _confidence(count: int, *, base: float = 0.60, ceiling: float = 0.92,
                scale_at: int = 12) -> float:
    ratio = min(count / scale_at, 1.0)
    return round(base + (ceiling - base) * ratio, 2)


def _parse_event(event: dict) -> Optional[dict]:
    """Extract cmd, exit_code, ts from an event row. Returns None if unusable."""
    try:
        data = json.loads(event.get("content", "{}"))
    except (json.JSONDecodeError, TypeError):
        return None
    cmd = data.get("cmd", "").strip()
    if not cmd:
        return None
    return {
        "cmd": cmd,
        "exit": data.get("exit", 0),
        "ts": data.get("ts") or event.get("created_at", 0),
        "id": event["id"],
        "project": event.get("project"),
    }


# ── Extractor 1: Command frequency ──────────────────────────────────────────

def extract_command_frequency(events: list[dict]) -> list[dict]:
    """Commands run 3+ times in the same project → command_pattern candidate."""
    counts: Counter = Counter()
    evidence: dict = defaultdict(list)

    for e in events:
        if e.get("source") != "terminal":
            continue
        parsed = _parse_event(e)
        if not parsed or _is_trivial(parsed["cmd"]):
            continue
        key = (parsed["project"] or "", parsed["cmd"])
        counts[key] += 1
        evidence[key].append(parsed["id"])

    candidates = []
    seen = set()
    for (project, cmd), count in counts.most_common():
        if count < _MIN_FREQ:
            break
        k = (project, cmd)
        if k in seen:
            continue
        seen.add(k)

        proj_name = _short_project(project)
        if proj_name:
            content = f'In {proj_name}, you often run `{cmd}` ({count} times).'
        else:
            content = f'You often run `{cmd}` ({count} times).'

        candidates.append({
            "type": "command_pattern",
            "source": "terminal",
            "project": project or None,
            "content": content,
            "evidence_ids": json.dumps(evidence[k][:20]),
            "confidence": _confidence(count),
            "sensitivity": "normal",
            "model_used": "pattern_extractor",
        })

    return candidates


# ── Extractor 2: Command sequences (A → B) ──────────────────────────────────

def extract_command_sequences(events: list[dict]) -> list[dict]:
    """A → B pairs that consistently co-occur within the same project."""
    by_project: dict[str, list] = defaultdict(list)

    for e in events:
        if e.get("source") != "terminal":
            continue
        parsed = _parse_event(e)
        if not parsed or _is_trivial(parsed["cmd"]):
            continue
        by_project[parsed["project"] or ""].append(parsed)

    candidates = []
    seen = set()

    for project, cmds in by_project.items():
        cmds.sort(key=lambda x: x["ts"])

        pair_counts: Counter = Counter()
        pair_evidence: dict = defaultdict(list)
        first_counts: Counter = Counter()

        for i in range(len(cmds) - 1):
            a, b = cmds[i]["cmd"], cmds[i + 1]["cmd"]
            if a == b:
                continue
            pair_counts[(a, b)] += 1
            pair_evidence[(a, b)].extend([cmds[i]["id"], cmds[i + 1]["id"]])
            first_counts[a] += 1

        for (a, b), count in pair_counts.most_common():
            if count < _MIN_SEQ:
                break
            ratio = count / max(first_counts[a], 1)
            if ratio < 0.55:
                continue
            pk = (project, a, b)
            if pk in seen:
                continue
            seen.add(pk)

            proj_name = _short_project(project)
            if proj_name:
                content = f'In {proj_name}, you usually run `{a}` then `{b}`.'
            else:
                content = f'You usually run `{a}` then `{b}`.'

            conf = _confidence(count)
            if ratio >= 0.80:
                conf = min(round(conf + 0.05, 2), 0.95)

            ev = list(dict.fromkeys(pair_evidence[(a, b)]))[:20]
            candidates.append({
                "type": "command_pattern",
                "source": "terminal",
                "project": project or None,
                "content": content,
                "evidence_ids": json.dumps(ev),
                "confidence": conf,
                "sensitivity": "normal",
                "model_used": "pattern_extractor",
            })

    return candidates


# ── Extractor 3: Error-fix pairs ─────────────────────────────────────────────

def extract_error_fix_pairs(events: list[dict]) -> list[dict]:
    """
    Detect: failing_cmd (exit != 0) → fix_cmd (exit == 0) within 15 minutes.
    Only works for live hook events (history scanner doesn't capture exit codes).
    """
    by_project: dict[str, list] = defaultdict(list)

    for e in events:
        if e.get("source") != "terminal":
            continue
        parsed = _parse_event(e)
        if not parsed:
            continue
        by_project[parsed["project"] or ""].append(parsed)

    candidates = []
    seen = set()

    for project, cmds in by_project.items():
        cmds.sort(key=lambda x: x["ts"])

        pair_counts: Counter = Counter()
        pair_evidence: dict = defaultdict(list)

        for i in range(len(cmds) - 1):
            fail = cmds[i]
            fix = cmds[i + 1]
            if fail["exit"] == 0:
                continue
            if fix["exit"] != 0:
                continue
            if fail["cmd"] == fix["cmd"]:
                continue
            # Must be within 15 minutes
            if (fix["ts"] or 0) - (fail["ts"] or 0) > 900:
                continue
            pair = (fail["cmd"], fix["cmd"])
            pair_counts[pair] += 1
            pair_evidence[pair].extend([fail["id"], fix["id"]])

        for (fail_cmd, fix_cmd), count in pair_counts.most_common():
            if count < _MIN_FIX:
                break
            pk = (project, fail_cmd, fix_cmd)
            if pk in seen:
                continue
            seen.add(pk)

            proj_name = _short_project(project)
            prefix = f"In {proj_name}, " if proj_name else ""
            content = (
                f'{prefix}`{fix_cmd}` resolves issues after `{fail_cmd}` fails'
                f' ({count} times).'
            )
            ev = list(dict.fromkeys(pair_evidence[(fail_cmd, fix_cmd)]))[:20]
            candidates.append({
                "type": "error_fix",
                "source": "terminal",
                "project": project or None,
                "content": content,
                "evidence_ids": json.dumps(ev),
                "confidence": _confidence(count, base=0.60, scale_at=8),
                "sensitivity": "normal",
                "model_used": "pattern_extractor",
            })

    return candidates


# ── Extractor 4: Project context ─────────────────────────────────────────────

def extract_project_context(events: list[dict]) -> list[dict]:
    """Detect project stack from filesystem markers for each unique project path."""
    projects: set[str] = set()
    for e in events:
        p = e.get("project")
        if p:
            projects.add(p)

    candidates = []
    for project in projects:
        path = Path(project)
        if not path.exists():
            continue

        stack_parts: list[str] = []

        pkg_json = path / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text())
                pkg_name = data.get("name", path.name)
                deps = list(data.get("dependencies", {}).keys())[:4]
                stack_parts.append(f"Node.js (package: {pkg_name})")
                if "next" in deps:
                    stack_parts.append("Next.js")
                if "react" in deps:
                    stack_parts.append("React")
                if "typescript" in data.get("devDependencies", {}):
                    stack_parts.append("TypeScript")
            except Exception:
                stack_parts.append("Node.js")

        if (path / "pyproject.toml").exists():
            stack_parts.append("Python (pyproject.toml)")
        elif (path / "requirements.txt").exists():
            stack_parts.append("Python")

        if (path / "go.mod").exists():
            stack_parts.append("Go")
        if (path / "Cargo.toml").exists():
            stack_parts.append("Rust")

        if not stack_parts:
            continue

        content = f'`{path.name}` is a {" + ".join(stack_parts)} project.'
        candidates.append({
            "type": "project_context",
            "source": "files",
            "project": str(project),
            "content": content,
            "evidence_ids": json.dumps([]),
            "confidence": 0.90,
            "sensitivity": "low",
            "model_used": "pattern_extractor",
        })

    return candidates


# ── Browser extractors ────────────────────────────────────────────────────────

def extract_research_topics(events: list[dict]) -> list[dict]:
    """
    Frequent browser searches → research_topic candidates.
    Groups search queries and domain visits to identify what the user is researching.
    """
    from collections import Counter
    search_counts: Counter = Counter()
    search_evidence: dict = defaultdict(list)

    domain_counts: Counter = Counter()
    domain_evidence: dict = defaultdict(list)

    for e in events:
        if e.get("source") != "browser":
            continue
        try:
            data = json.loads(e.get("content", "{}"))
        except Exception:
            continue

        if e.get("type") == "browser_search":
            query = data.get("query", "").strip().lower()
            if query and len(query) > 2:
                search_counts[query] += 1
                search_evidence[query].append(e["id"])

        elif e.get("type") == "browser_visit":
            url = data.get("url", "")
            title = data.get("title", "")
            try:
                from urllib.parse import urlparse
                domain = urlparse(url).netloc.lstrip("www.")
                if domain and "." in domain:
                    domain_counts[domain] += 1
                    domain_evidence[domain].append(e["id"])
            except Exception:
                pass

    candidates = []
    seen = set()

    # Repeated search queries (3+)
    for query, count in search_counts.most_common():
        if count < 3:
            break
        if query in seen:
            continue
        seen.add(query)
        content = f'You searched for "{query}" {count} times.'
        candidates.append({
            "type": "research_topic",
            "source": "browser",
            "project": None,
            "content": content,
            "evidence_ids": json.dumps(search_evidence[query][:10]),
            "confidence": _confidence(count, base=0.65),
            "sensitivity": "normal",
            "model_used": "pattern_extractor",
        })

    # Frequently visited domains (5+)
    for domain, count in domain_counts.most_common():
        if count < 5:
            break
        if domain in seen:
            continue
        seen.add(domain)
        content = f'You frequently visit {domain} ({count} times).'
        candidates.append({
            "type": "research_topic",
            "source": "browser",
            "project": None,
            "content": content,
            "evidence_ids": json.dumps(domain_evidence[domain][:10]),
            "confidence": _confidence(count, base=0.60, scale_at=20),
            "sensitivity": "low",
            "model_used": "pattern_extractor",
        })

    return candidates


def extract_claude_code_patterns(events: list[dict]) -> list[dict]:
    """
    Claude Code sessions → decision and project_context candidates.
    Surfaces what topics were discussed most.
    """
    from collections import Counter
    topic_counts: Counter = Counter()
    topic_evidence: dict = defaultdict(list)

    for e in events:
        if e.get("source") != "claude_code":
            continue
        try:
            data = json.loads(e.get("content", "{}"))
        except Exception:
            continue

        project = data.get("project", "")
        first_msg = data.get("first_message", "").strip()
        if not first_msg or len(first_msg) < 10:
            continue

        # Use first 60 chars as the topic key
        topic_key = first_msg[:60].lower()
        topic_counts[topic_key] += 1
        topic_evidence[topic_key].append(e["id"])

    candidates = []
    seen = set()

    for topic, count in topic_counts.most_common():
        if count < 2:
            break
        if topic in seen:
            continue
        seen.add(topic)
        content = f'You repeatedly discussed with Claude: "{topic[:80]}" ({count} sessions).'
        candidates.append({
            "type": "decision",
            "source": "claude_code",
            "project": None,
            "content": content,
            "evidence_ids": json.dumps(topic_evidence[topic][:10]),
            "confidence": _confidence(count, base=0.65, scale_at=8),
            "sensitivity": "normal",
            "model_used": "pattern_extractor",
        })

    return candidates


# ── Entry point ───────────────────────────────────────────────────────────────

def run_all(events: list[dict]) -> list[dict]:
    """Run all extractors. Returns combined list of candidate dicts."""
    results: list[dict] = []
    results.extend(extract_command_frequency(events))
    results.extend(extract_command_sequences(events))
    results.extend(extract_error_fix_pairs(events))
    results.extend(extract_project_context(events))
    results.extend(extract_research_topics(events))
    results.extend(extract_claude_code_patterns(events))
    return results
