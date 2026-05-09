# Connector: Terminal

**Status:** Concept  
**Stage:** 1  
**Permission required:** `terminal:read`, `terminal:watch`

---

## What It Is

The terminal connector reads from shell history and (optionally) observes commands as they run, to learn command patterns, project workflows, errors, and fixes.

This is the first connector built — the foundation of the MVP.

---

## Why It Matters

The terminal is where developers spend most of their active work time. Command patterns reveal:
- Which projects are active
- How builds and tests work
- What errors are repeating
- What workflows are established
- What commands are part of a sequence

---

## What It Reads

### Shell History Files
- `~/.zsh_history` (zsh)
- `~/.bash_history` (bash)
- `~/.fish_history` (fish)

History is read periodically or on session end.

### Live Command Observation (optional, `terminal:watch`)
A shell hook (`PROMPT_COMMAND` or zsh `precmd`) sends each command + exit code to Stareha in real time.

```bash
# Added to ~/.zshrc by stareha setup or advanced stareha init
stareha_hook() {
  stareha event command \
    --cmd "$1" \
    --exit-code "$?" \
    --pwd "$PWD" \
    --timestamp "$(date +%s)"
}
precmd_functions+=(stareha_hook)
```

---

## Events Generated

| Event type | When generated | Data captured |
|------------|---------------|--------------|
| `command_run_success` | Command exits 0 | cmd, pwd, project, timestamp |
| `command_run_error` | Command exits non-0 | cmd, exit code, pwd, project, timestamp |
| `command_sequence` | Two commands in sequence | cmd_a, cmd_b, project |
| `error_fix_pair` | Error followed by success | failed_cmd, fix_cmd, project |

---

## Pattern Extraction (Scripts)

| Pattern | Detection method | Memory type |
|---------|-----------------|-------------|
| Build before test | `npm run build` precedes `npm test` 3+ times | `command_sequence` |
| Repeated error | Same non-zero exit command 3+ times | `error_pattern` |
| Fix pattern | Error command → modified command → success | `error_fix` |
| Project setup | `git clone`, `npm install`, `cp .env.example` in sequence | `project_setup` |
| Frequent command | Same command 5+ times in a project | `command_habit` |

---

## Redaction

Before any command is stored:
- Strip secrets: `export API_KEY=...`, `curl -H "Authorization: Bearer sk-..."` → masked
- Strip passwords: `sudo`, `psql -U user -p password` → password masked
- Strip tokens in URLs: `https://api.example.com?token=abc` → token masked
- Keep: command name, flags, file paths, exit code, project

Redaction regex patterns (examples):
```
/\b(sk-[a-zA-Z0-9]{20,})\b/  → [REDACTED_API_KEY]
/(-p|--password)\s+\S+/       → [REDACTED_PASSWORD]
/Bearer\s+[a-zA-Z0-9._-]+/    → Bearer [REDACTED_TOKEN]
```

---

## Example Memories Generated

```
In AgentOS, you run npm run build before npm test.
Source: terminal | Evidence: 8 occurrences | Confidence: 0.84
```

```
npm cache clean --force fixes install errors in agent-os.
Source: terminal | Evidence: error→fix pair 3× | Confidence: 0.78
```

---

## Project Association

Commands are associated with projects by checking `$PWD` against:
1. Known git repositories (detected by `.git` presence)
2. User-configured project paths
3. Package.json / pyproject.toml presence

---

## Related Files
- [Connectors Overview](README.md)
- [Terminal Memory](../../02-workflow-memory/terminal-memory.md)
- [Intelligence Policy Flow](../../../_flows/intelligence-policy-flow.md) — scripts layer
