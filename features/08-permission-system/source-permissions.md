# Source Permissions

**Status:** Concept  
**Stage:** 1

---

## Source Permission Table

| Source | Permission key | What it allows | Default |
|--------|---------------|----------------|---------|
| Terminal (history) | `terminal:read` | Read existing shell history file | Off |
| Terminal (live) | `terminal:watch` | Observe commands as they run via shell hook | Off |
| Files | `files:watch:<path>` | Watch specific directory for file changes | Off |
| Claude Code | `claude_code:read` | Read Claude Code conversation history + CLAUDE.md | Off |
| Browser | `browser:read` | Receive data from browser extension | Off |
| App usage | `app_usage:read` | See list of running application names | Off |

---

## Enabling Sources

```bash
# Enable terminal
stareha permissions add terminal

# Enable terminal (live observation via shell hook)
stareha permissions add terminal --watch

# Enable file watching for specific path
stareha permissions add files ~/projects/agent-os
stareha permissions add files ~/projects/stareha

# Enable Claude Code history
stareha permissions add claude-code

# List all enabled permissions
stareha permissions list

# Disable a source
stareha permissions remove terminal
stareha permissions remove files ~/projects/agent-os
```

---

## What Each Source Can and Cannot See

### `terminal:read`
**Can see:** command text, exit code, working directory, timestamp
**Cannot see:** environment variables (filtered), passwords (redacted), stdin/stdout beyond command itself

### `terminal:watch`
**Can see:** same as terminal:read, plus live commands as they run
**Cannot see:** interactive sessions (SSH, vim, psql sessions are not captured)

### `files:watch:<path>`
**Can see:** file path (relative to project), file extension, when it was saved
**Cannot see:** file contents, diff, line numbers

### `claude_code:read`
**Can see:** conversation summaries, decisions mentioned, tasks, CLAUDE.md content
**Cannot see:** raw conversation text (summarized only), any files discussed (only references)

### `browser:read`
**Can see:** page title, domain, topic estimate, time spent
**Cannot see:** page contents, form data, passwords, financial pages

### `app_usage:read`
**Can see:** application name (e.g., "code", "firefox", "terminal")
**Cannot see:** window titles, what's open inside the app, keystrokes

---

## Permission Revocation

When a source is disabled:
1. Collector stops immediately
2. No new events from that source
3. Existing memories from that source remain (user must delete manually if desired)
4. Future learning runs skip that source

---

## Related Files
- [Permission System](README.md)
- [Action Permissions](action-permissions.md)
- [Permission Flow](../../_flows/permission-flow.md)
