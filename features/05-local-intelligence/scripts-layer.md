# Scripts Layer

**Status:** Concept  
**Stage:** 1

---

## What It Is

The scripts layer is the first and preferred intelligence layer — deterministic programs that extract patterns from user activity without any LLM involvement.

---

## Why It Is First

- Zero cost
- Zero latency (runs in-process)
- Zero privacy risk
- Zero hallucination risk
- Fully auditable

If a script can do the job, it should.

---

## What Scripts Handle

| Task | Script approach |
|------|----------------|
| File change detection | inotify watch → event emission |
| Git status | `git status --porcelain` parsing |
| Command frequency | SQLite COUNT query on event store |
| Command failure detection | Exit code comparison |
| Secret redaction | Regex pattern matching |
| Browser domain stats | URL parsing + domain extraction |
| App usage counting | `/proc` process list parsing |
| Event classification | Rule table lookup (source + type → class) |
| Importance scoring | Formula: frequency + error + signal |
| Deduplication | SHA256 hash comparison |
| Sequence detection | Sliding window over ordered events |
| Error-fix pairing | Error event + subsequent success within 5 commands |
| Project detection | Walk up to `.git`, read `package.json` |

---

## Script Examples

### Command Frequency

```python
def command_frequency(project: str, since: datetime) -> dict[str, int]:
    return db.execute(
        "SELECT cmd, COUNT(*) as count FROM events "
        "WHERE project = ? AND created_at > ? "
        "GROUP BY cmd ORDER BY count DESC",
        (project, since.timestamp())
    ).fetchall()
```

### Sequence Detection

```python
def detect_sequences(events: list[Event], min_occurrences=3) -> list[Sequence]:
    pairs = {}
    for i in range(len(events) - 1):
        if events[i].project == events[i+1].project:
            key = (events[i].cmd, events[i+1].cmd)
            pairs[key] = pairs.get(key, 0) + 1
    return [Sequence(a, b, count) for (a, b), count in pairs.items()
            if count >= min_occurrences]
```

### Importance Score

```python
def importance_score(event: Event, frequency: int, is_error_fix: bool, is_explicit: bool) -> float:
    score = 0.3  # base
    if frequency >= 3:
        score += min(frequency * 0.05, 0.3)
    if is_error_fix:
        score += 0.25
    if is_explicit:
        score = max(score, 0.9)
    if event.cmd in TRIVIAL_COMMANDS:
        score -= 0.2
    return min(score, 1.0)
```

---

## TRIVIAL_COMMANDS (Ignore List)

Commands too common to be meaningful:

```python
TRIVIAL_COMMANDS = {
    'ls', 'll', 'la', 'pwd', 'cd', 'clear', 'echo',
    'cat', 'grep', 'find', 'which', 'man', 'help',
    'history', 'env', 'export', 'source', 'exit'
}
```

---

## Related Files
- [Local Intelligence](README.md)
- [Intelligence Policy Flow](../../_flows/intelligence-policy-flow.md)
- [Redaction](redaction.md)
