# Linux Daemon

**Status:** Built  
**Stage:** 1

---

## What It Is

The Stareha Linux daemon runs as a systemd user service, enabling background event collection and learning without requiring the user to run anything manually.

---

## Systemd Service File

```ini
# ~/.config/systemd/user/stareha.service

[Unit]
Description=Stareha AI Companion Daemon
After=default.target

[Service]
Type=simple
ExecStart=%h/.local/bin/stareha daemon
Restart=on-failure
RestartSec=5
Environment=STAREHA_HOME=%h/.stareha

[Install]
WantedBy=default.target
```

---

## Install & Enable

```bash
# stareha init runs these automatically:
systemctl --user enable stareha
systemctl --user start stareha
```

---

## Commands

```bash
stareha start      # Tries systemd → falls back to direct subprocess launch
stareha stop       # systemctl stop (if available) + SIGTERM via PID file
stareha restart    # stop then start
stareha status     # Custom status: events, inbox, LLM availability, sources
```

### Start fallback logic

```
stareha start
  ↓
Is ~/.config/systemd/user/stareha.service installed?
  YES → systemctl --user start stareha
        Check PID file after 1.5s
        If PID exists → success
        Else → try direct launch
  NO  → direct launch
         subprocess.Popen([python3, daemon/main.py], start_new_session=True)
         Poll PID file for up to 3s
         If PID exists → success
```

Direct launch makes `stareha start` work on any Linux system, even without systemd
(containers, WSL, non-systemd distros).

### `stareha status` output

```
Stareha Daemon Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Daemon:        running (uptime: 3d 4h)
Learning:      active
Last run:      2026-05-06 at 08:30

Sources:
  terminal:    ✓ watching
  file_watch:  ✓ watching ~/projects/agent-os
  claude_code: ✓ enabled
  browser:     ✗ not enabled

Memory:
  Approved:    47
  Pending:     3 (run: stareha memory inbox)

Local LLM:    ✓ ollama running (llama3.2:3b)
Cloud LLM:    ✓ configured (claude-sonnet-4-6)
```

---

## Daemon Architecture

```
stareha daemon
├── Event Loop
│   ├── inotify watcher (file changes)
│   ├── HTTP server (receives shell hook events, port 7431)
│   ├── HTTP server (receives browser extension events, port 7432)
│   └── Scheduler (cron-like for learning runs)
├── Learning Runner
│   ├── Pattern extractor
│   ├── LLM caller (local or cloud)
│   └── Candidate writer
└── Guidance Preparer
    ├── Gap analyzer
    ├── Plan builder
    └── Briefing formatter
```

---

## Ports Used

| Port | Purpose |
|------|---------|
| 7431 | Shell hook event receiver |
| 7432 | Browser extension event receiver |

Both ports bind to localhost only. No external access.

---

## Data Directory

```
~/.stareha/
├── db.sqlite           # Event store + memories
├── permissions.json    # Source permissions
├── config.json         # User configuration
├── prompts/            # LLM prompt templates
├── guidance/           # Prepared guidance files
├── exercises/          # Generated exercises
└── logs/               # Daemon logs (rotated daily)
```

---

## Related Files
- [Daemon & Runtime](README.md)
- [Event Collectors](event-collectors.md)
- [Scheduler](scheduler.md)
