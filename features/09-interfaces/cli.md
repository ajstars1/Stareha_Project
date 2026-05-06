# Interface: CLI

**Status:** Concept  
**Stage:** 1  
**Priority:** Build this first.

---

## What It Is

The `stareha` CLI is the primary interface for MVP. All Stareha features are accessible via command line.

---

## Command Map

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

### Learning & Guidance

```bash
stareha what-did-you-learn today      # Today's session summary
stareha what-did-you-learn yesterday  # Yesterday's session summary
stareha prep tomorrow                 # Prepare next-session guidance
stareha prep now                      # Force guidance preparation
stareha learn now                     # Force learning run
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
stareha quiz <concept>               # Start a quiz
stareha exercise <id>                # View an exercise
stareha exercise complete <id>       # Mark exercise done
stareha exercise skip <id>           # Skip exercise
stareha exercise list                # List pending exercises
```

### Talking Mode

```bash
stareha talk                         # Open cloud LLM conversation mode
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
stareha init                         # First-time setup wizard
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

The shell hook is added to `~/.zshrc` (or `~/.bashrc`) by `stareha init`:

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
