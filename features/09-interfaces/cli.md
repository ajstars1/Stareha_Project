# Interface: CLI

**Status:** Built
**Stage:** 1–5.5
**Priority:** Primary MVP interface.

---

## What It Is

The `stareha` CLI is the primary interface for MVP. It has two layers:

- Beginner product flow: human learning actions such as `setup`, `learn`, `note`, `done`, and `continue`.
- Advanced controls: daemon, sessions, memory, ledger, permissions, and LLM tooling.

---

## Command Map

### Beginner Learning Flow

```bash
stareha                                # Home screen
stareha setup                          # Beginner first-run setup
stareha learn "<goal>"                 # Start a learning session
stareha learn "<goal>" --project <path> # Start with explicit project
stareha note "<text>"                  # Add note to active session/project
stareha done                           # End session, show Learning Card, review notices
stareha done --no-review               # End session without interactive review
stareha continue                       # Resume from last useful point
```

The beginner flow hides internal terms like daemon, memory candidates, ledger, and prepared guidance until the user asks for them.

### Daemon

```bash
stareha start                         # Start daemon
stareha stop                          # Stop daemon
stareha restart                       # Restart daemon
stareha status                        # Full status report
```

### Session Management

```bash
stareha session start "<goal>"        # Begin tagged learning/work session
stareha session stop                  # End session, trigger learning run
stareha session status                # Current session info
```

These commands remain available for advanced/manual control. New learner-facing flows should use `stareha learn "<goal>"` and `stareha done`.

### Learning & Guidance

```bash
stareha what-did-you-learn today      # Today's session summary
stareha what-did-you-learn yesterday  # Yesterday's session summary
stareha prep                          # Prepare next-session guidance
stareha prep --quiz                   # Prepare guidance plus quiz
stareha learn                         # Advanced: force learning run on new events
stareha learn --force                 # Advanced: force learning run on all events
stareha ledger                        # Learning run audit log
```

### Memory Management

```bash
stareha memory inbox                  # Review pending candidates
stareha memory approve <id>           # Accept a memory
stareha memory reject <id>            # Discard a candidate
stareha memory edit <id>              # Edit and approve a memory
stareha memory why <id>               # Show full provenance
stareha memory sources <id>           # Show raw evidence events
stareha memory forget <id>            # Delete a memory
stareha memory list                   # List all approved memories
stareha memory search <query>         # Search memories
stareha memory stats                  # Memory counts and breakdown
stareha memory export                 # Export all memories
stareha memory reset --confirm        # Delete everything
```

### Permissions

```bash
stareha permissions list              # Show all permissions
stareha permissions add terminal      # Enable terminal source
stareha permissions add files <path>  # Enable file watching at path
stareha permissions add claude-code   # Enable Claude Code import
stareha permissions remove <source>   # Disable a source
stareha permissions allow "<action>"  # Pre-approve an action
stareha permissions block "<action>"  # Block an action
stareha permissions list-actions      # Show action permissions
```

### Quiz & Exercises

```bash
stareha quiz <concept>               # Start a local/script-backed quiz
stareha quiz --cloud <concept>       # Explicitly allow Claude fallback
stareha exercise <id>                # View an exercise
stareha exercise complete <id>       # Mark exercise done
stareha exercise skip <id>           # Skip exercise
stareha exercise list                # List pending exercises
```

### Talking Mode

```bash
stareha talk                         # Open local LLM conversation mode
stareha talk --cloud                 # Explicitly allow Claude fallback
```

### Profile

```bash
stareha profile                      # View learning profile
stareha profile goals                # View/edit goals
stareha note "<text>"                # Add manual context note
```

### Configuration

```bash
stareha config list                  # Show all config
stareha config set <key> <value>     # Set config value
stareha config redact add <pattern>  # Add custom redaction pattern
stareha setup                        # Beginner first-time setup wizard
stareha init                         # Advanced legacy setup wizard
```

### Utilities

```bash
stareha usage cloud                  # Cloud LLM usage stats
stareha actions log                  # Action history
stareha pause                        # Pause learning
stareha resume                       # Resume learning
stareha import claude-code           # Force Claude Code import
```

---

## CLI Design Principles

1. Every command produces readable human output, not JSON (unless `--json` flag)
2. Destructive commands require `--confirm`
3. Long outputs are paginated
4. All commands work without the daemon running (will warn + explain)
5. `--help` on every command

---

## Terminal Integration

The shell hook is added to `~/.zshrc` or `~/.bashrc` by `stareha setup` or the advanced `stareha init`:

```bash
# Stareha shell integration
stareha_hook() {
  stareha event command \
    --cmd "$1" --exit-code "$?" \
    --pwd "$PWD" --ts "$(date +%s)" 2>/dev/null
}
precmd_functions+=(stareha_hook)
```

---

## Related Files
- [Interfaces Overview](README.md)
- [MVP](../../product/mvp.md) — full MVP command list
- [Memory Commands](../06-memory-governance/memory-commands.md)
