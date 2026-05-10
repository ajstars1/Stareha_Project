"""
Stareha CLI — `stareha` command entry point.
Built with Click. All output via Rich.
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.core.config import load_config, save_config, ensure_dirs
from packages.core.db import Store
from packages.permissions import enable_source, list_permissions
from packages.intelligence.learning_runner import run_learning
from packages.intelligence.ledger import (
    what_did_you_learn, recent_runs, feedback_stats, get_rejection_counts,
)
from packages.memory.manager import (
    approve_candidate, reject_candidate, forget_memory,
    get_memory_why, list_memories, search_memories,
    get_sources, memory_stats,
)
from packages.guidance.briefing import format_briefing_cli
from packages.guidance.quiz import generate_quiz, run_quiz_interactive
from packages.guidance.prep import (
    prepare_guidance, get_pending, get_all_guidance,
    mark_delivered, mark_completed, add_note,
)
from packages.experience.continuation import build_continue_plan, format_continue_plan_cli
from packages.experience.home import build_home, format_home_cli
from packages.experience.learning_card import build_learning_card, format_learning_card_cli
from packages.experience.mode_presets import DEFAULT_MODE, MODE_PRESETS
from packages.experience.project_registry import remember_project
from packages.experience.project_resolver import resolve_project
from packages.experience.review_flow import review_notices

console = Console()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_store() -> Store:
    return Store(load_config().db_path)


def _pid_path() -> Path:
    return Path.home() / ".stareha" / "daemon.pid"


def _daemon_pid() -> int | None:
    p = _pid_path()
    if not p.exists():
        return None
    try:
        pid = int(p.read_text().strip())
        os.kill(pid, 0)  # check process exists
        return pid
    except (ValueError, ProcessLookupError, PermissionError):
        return None


def _systemctl(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["systemctl", "--user", *args], capture_output=True, text=True)


def _service_file_installed() -> bool:
    return (Path.home() / ".config" / "systemd" / "user" / "stareha.service").exists()


def _start_daemon_direct() -> bool:
    """Launch the daemon as a detached background process (no systemd required)."""
    daemon_script = Path(__file__).resolve().parents[1] / "daemon" / "main.py"
    if not daemon_script.exists():
        return False
    proc = subprocess.Popen(
        [sys.executable, str(daemon_script)],
        start_new_session=True,      # detach — survives when CLI exits
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # Give it a moment to write the PID file
    for _ in range(10):
        time.sleep(0.3)
        if _daemon_pid():
            return True
    return False


def _stop_daemon_direct() -> bool:
    """Kill the daemon process directly via its PID file."""
    pid = _daemon_pid()
    if not pid:
        return False
    try:
        import signal as _signal
        os.kill(pid, _signal.SIGTERM)
        return True
    except Exception:
        return False


def _load_raw_config() -> dict:
    """Return the raw config JSON dict (not the typed Config dataclass)."""
    from packages.core.config import CONFIG_PATH
    import json as _json
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return _json.load(f)
    return {}


def _uptime(pid: int) -> str:
    try:
        stat = Path(f"/proc/{pid}/stat").read_text().split()
        boot = float(Path("/proc/uptime").read_text().split()[0])
        start_ticks = int(stat[21])
        hz = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
        started_secs_ago = boot - (start_ticks / hz)
        m, s = divmod(int(started_secs_ago), 60)
        h, m = divmod(m, 60)
        return f"{h}h {m}m" if h else f"{m}m"
    except Exception:
        return "unknown"


# ── CLI root ──────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Stareha — your AI companion that learns how you work."""
    if ctx.invoked_subcommand is not None:
        return
    store = _get_store()
    try:
        console.print(format_home_cli(build_home(store)))
    finally:
        store.close()


# ── stareha setup ─────────────────────────────────────────────────────────────

@cli.command()
@click.pass_context
def setup(ctx):
    """Beginner setup for Stareha Learn."""
    console.print("\n[bold]Welcome to Stareha Learn.[/bold]")
    console.print("[dim]Setup takes about two minutes and keeps raw data local.[/dim]\n")

    ensure_dirs()

    console.print("[bold]How do you want to use Stareha first?[/bold]\n")
    console.print("1. Learner (Recommended)")
    console.print("   For programming, AI, technical skills, or project-based study.")
    console.print("2. Companion (Experimental)")
    console.print("   For broader work continuity and personal projects.")
    console.print("3. Researcher (Experimental)")
    console.print("   For reading, research sessions, notes, and synthesis.\n")
    mode_choice = click.prompt(
        "Choose mode",
        type=click.Choice(["1", "2", "3"], case_sensitive=False),
        default="1",
        show_default=True,
    )
    mode = {"1": "learner", "2": "companion", "3": "researcher"}[mode_choice]
    preset = MODE_PRESETS.get(mode, MODE_PRESETS[DEFAULT_MODE])
    if mode != DEFAULT_MODE:
        console.print("[yellow]This mode is experimental. Learner is the stable alpha path.[/yellow]")

    default_workspace = Path.home() / "projects"
    if not default_workspace.exists():
        default_workspace = Path.cwd()
    console.print("\n[bold]Where do you keep your learning projects?[/bold]")
    console.print("[dim]Use the parent folder, not one specific project.[/dim]")
    workspace = click.prompt(
        "Workspace folder",
        default=str(default_workspace),
        show_default=True,
    )
    workspace_path = str(Path(workspace).expanduser())

    console.print("\n[bold]What can Stareha use to understand your learning?[/bold]")
    console.print("[dim]Recommended: terminal commands, project file metadata, and manual notes.[/dim]")
    use_recommended = click.confirm("Use recommended local tracking?", default=True)
    if use_recommended:
        enable_source("terminal", watch=True)
        enable_source("files", path=workspace_path)
        _install_shell_hook()
    else:
        if click.confirm("Track terminal commands and exit codes?", default=True):
            enable_source("terminal", watch=True)
            _install_shell_hook()
        if click.confirm("Track project file activity metadata?", default=True):
            enable_source("files", path=workspace_path)

    config = load_config()
    watched_paths = list(dict.fromkeys([*config.watched_paths, workspace_path]))
    save_config({
        "mode": mode,
        "mode_status": preset["status"],
        "workspace_roots": [workspace_path],
        "watched_paths": watched_paths,
    })

    # ── LLM provider step ────────────────────────────────────────────────────
    console.print("\n[bold]How should Stareha generate insights?[/bold]\n")
    console.print("1. Claude Code  — Use your claude.ai Pro/Max subscription (recommended, no API key needed)")
    console.print("2. Anthropic    — Anthropic API key (console.anthropic.com)")
    console.print("3. OpenAI       — OpenAI API key (platform.openai.com)")
    console.print("4. Groq         — Groq API key — free tier available (console.groq.com)")
    console.print("5. Gemini       — Google Gemini API key (aistudio.google.com)")
    console.print("6. Custom       — Any OpenAI-compatible endpoint (Ollama cloud, vLLM, LM Studio, etc.)")
    console.print("7. Local only   — Use Ollama on this machine (no cloud)")
    console.print("8. Skip for now — Configure later with: stareha cloud-llm list\n")

    llm_choice = click.prompt(
        "Choose LLM provider",
        type=click.Choice(["1", "2", "3", "4", "5", "6", "7", "8"], case_sensitive=False),
        default="8",
        show_default=True,
    )

    if llm_choice == "1":
        try:
            from packages.intelligence.providers.claude_code_oauth import run_oauth_flow
            console.print("\n[dim]Opening browser for Claude Code OAuth...[/dim]")
            success = run_oauth_flow()
            if success:
                save_config({"cloud_provider": "claude_code_oauth"})
                console.print("[green]✓[/green] Claude Code connected and set as active provider.")
            else:
                console.print("[yellow]OAuth did not complete. Configure later with: stareha cloud-llm connect[/yellow]")
        except ImportError:
            console.print("[yellow]Claude Code OAuth not available in this build. Run: stareha cloud-llm connect[/yellow]")
    elif llm_choice in ("2", "3", "4", "5"):
        provider_map = {"2": "anthropic", "3": "openai", "4": "groq", "5": "gemini"}
        provider_id = provider_map[llm_choice]
        api_key = click.prompt(f"Enter your {provider_id.capitalize()} API key", hide_input=True)
        if api_key.strip():
            _raw_cfg = _load_raw_config()
            provider_cfgs = _raw_cfg.get("provider_configs", {})
            provider_cfgs[provider_id] = {"api_key": api_key.strip()}
            save_config({"provider_configs": provider_cfgs, "cloud_provider": provider_id})
            console.print(f"[green]✓[/green] {provider_id.capitalize()} API key saved and set as active provider.")
        else:
            console.print("[yellow]No key entered — skipped.[/yellow]")
    elif llm_choice == "6":
        base_url = click.prompt("Base URL (e.g. http://localhost:11434/v1)", default="http://localhost:11434/v1")
        api_key = click.prompt("API key (leave blank if not required)", default="", hide_input=True)
        model = click.prompt("Model name (e.g. llama3.2:3b)", default="llama3.2:3b")
        _raw_cfg = _load_raw_config()
        provider_cfgs = _raw_cfg.get("provider_configs", {})
        provider_cfgs["openai_compat"] = {
            "base_url": base_url.strip(),
            "api_key": api_key.strip(),
            "model": model.strip(),
        }
        save_config({"provider_configs": provider_cfgs, "cloud_provider": "openai_compat"})
        console.print("[green]✓[/green] Custom endpoint saved and set as active provider.")
    elif llm_choice == "7":
        console.print("[dim]Local Ollama selected. No cloud provider set.[/dim]")
        console.print("[dim]Make sure Ollama is running: ollama serve[/dim]")
    else:
        console.print("[dim]Skipped. Configure later with: stareha cloud-llm list[/dim]")

    # ─────────────────────────────────────────────────────────────────────────

    try:
        _install_systemd_service()
    except Exception:
        console.print("[dim]systemd user service not available; direct daemon start will be used.[/dim]")

    console.print("\n[bold green]Setup complete.[/bold green]")
    console.print("[dim]Restart your shell once so the terminal hook is active.[/dim]")

    if click.confirm("Start your first learning session now?", default=False):
        goal = click.prompt("What are you learning?")
        ctx.invoke(learn, goal=goal, project=None, force=False)
    else:
        console.print('\nStart later with: [bold]stareha learn "React forms"[/bold]\n')

    if not _daemon_pid():
        ctx.invoke(start)


# ── stareha init ──────────────────────────────────────────────────────────────

@cli.command()
def init():
    """First-time setup: enable sources, install shell hook, enable daemon."""
    console.print("\n[bold]Welcome to Stareha.[/bold]\n")
    console.print("Stareha learns from approved sources. Nothing is enabled by default.\n")

    ensure_dirs()

    # Terminal
    if click.confirm("Enable terminal history (reads shell history, observes commands)?", default=True):
        enable_source("terminal", watch=True)
        _install_shell_hook()
        console.print("[green]✓[/green] Terminal enabled")

    # Files
    if click.confirm("Enable file watching (watch specific project directories)?", default=False):
        path = click.prompt("  Project path to watch", default=str(Path.home() / "projects"))
        enable_source("files", path=path)
        console.print(f"[green]✓[/green] Watching {path}")

    # Claude Code
    from pathlib import Path as _P
    claude_dir = _P.home() / ".claude" / "projects"
    if claude_dir.exists():
        if click.confirm("Enable Claude Code history (reads AI session history from ~/.claude/)?", default=True):
            enable_source("claude_code")
            console.print("[green]✓[/green] Claude Code enabled")
    else:
        console.print("[dim]Claude Code not found — skipping (install Claude Code CLI to enable)[/dim]")

    # Browser history
    from packages.collectors.browser import _CHROME_PATHS, _find_firefox_profiles
    chrome_found = any(p.exists() for p in _CHROME_PATHS)
    firefox_found = bool(_find_firefox_profiles())
    browsers = []
    if chrome_found:
        browsers.append("Chrome/Chromium")
    if firefox_found:
        browsers.append("Firefox")

    if browsers:
        browser_str = " + ".join(browsers)
        if click.confirm(
            f"Enable browser history ({browser_str} — reads local SQLite, no extension needed)?",
            default=False
        ):
            enable_source("browser")
            console.print(f"[green]✓[/green] Browser history enabled ({browser_str})")
    else:
        console.print("[dim]No supported browser found — skipping[/dim]")

    # Install systemd service (optional)
    try:
        _install_systemd_service()
    except Exception:
        console.print("[dim]systemd not available — daemon will start directly[/dim]")

    console.print("\n[bold green]Setup complete.[/bold green] Run [bold]stareha start[/bold] to begin.")


def _install_shell_hook() -> None:
    from packages.collectors.terminal.hook_receiver import SHELL_HOOK_ZSH, SHELL_HOOK_BASH
    shell = os.environ.get("SHELL", "")
    if "zsh" in shell:
        rc = Path.home() / ".zshrc"
        hook = SHELL_HOOK_ZSH
    else:
        rc = Path.home() / ".bashrc"
        hook = SHELL_HOOK_BASH

    content = rc.read_text() if rc.exists() else ""
    if "_stareha_hook" not in content:
        with open(rc, "a") as f:
            f.write(f"\n{hook}\n")
        console.print(f"  [dim]Shell hook added to {rc}[/dim]")
    else:
        console.print(f"  [dim]Shell hook already in {rc}[/dim]")


def _install_systemd_service() -> None:
    service_src = Path(__file__).parent / "stareha.service"
    service_dst = Path.home() / ".config" / "systemd" / "user" / "stareha.service"
    service_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(service_src, service_dst)
    subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True)
    subprocess.run(["systemctl", "--user", "enable", "stareha"], capture_output=True)
    console.print("  [dim]Systemd service installed and enabled[/dim]")


# ── stareha start/stop/restart ────────────────────────────────────────────────

@cli.command()
def start():
    """Start the Stareha daemon (systemd if available, direct process otherwise)."""
    if _daemon_pid():
        console.print("[yellow]Daemon is already running.[/yellow]")
        return

    if _service_file_installed():
        _systemctl("start", "stareha")
        time.sleep(1.5)
        if _daemon_pid():
            console.print("[green]✓[/green] Stareha started (systemd).")
            return
        console.print("[dim]systemd start failed — trying direct launch...[/dim]")

    if _start_daemon_direct():
        console.print("[green]✓[/green] Stareha started.")
    else:
        console.print("[red]Failed to start daemon.[/red]")
        console.print("[dim]Run `stareha init` to set up systemd, or check Python path.[/dim]")


@cli.command()
def stop():
    """Stop the Stareha daemon."""
    if _service_file_installed():
        _systemctl("stop", "stareha")
    _stop_daemon_direct()
    console.print("[yellow]●[/yellow] Stareha stopped.")


@cli.command()
def restart():
    """Restart the Stareha daemon."""
    ctx = click.get_current_context()
    ctx.invoke(stop)
    time.sleep(0.5)
    ctx.invoke(start)


# ── stareha daemon (internal — called by systemd) ────────────────────────────

@cli.command(hidden=True)
def daemon():
    """Start daemon process (called by systemd — use `stareha start` instead)."""
    from apps.daemon.main import run
    run()


# ── stareha status ────────────────────────────────────────────────────────────

@cli.command()
def status():
    """Show daemon status, sources, and event counts."""
    pid = _daemon_pid()
    config = load_config()

    # Daemon status line
    if pid:
        uptime = _uptime(pid)
        console.print(f"[bold green]● Stareha[/bold green]  running (uptime: {uptime})")
    else:
        console.print("[bold red]● Stareha[/bold red]  stopped")

    console.rule(style="dim")

    # Sources
    perms = list_permissions()["sources"]
    src_table = Table(box=None, show_header=False, padding=(0, 2))
    src_table.add_column("source", style="dim")
    src_table.add_column("status")
    for name, cfg in perms.items():
        enabled = cfg.get("enabled", False)
        mark = "[green]✓[/green]" if enabled else "[dim]✗[/dim]"
        src_table.add_row(name, mark)
    console.print("[bold]Sources[/bold]")
    console.print(src_table)

    # Event + memory counts
    try:
        store = _get_store()
        today = int(time.time()) - 86400
        total = store.count_events()
        today_count = store.count_events(since=today)
        active = store.get_active_session()
        pending = store._conn.execute(
            "SELECT count(*) FROM memory_candidates WHERE status='pending'"
        ).fetchone()[0]
        mem_total = store._conn.execute("SELECT count(*) FROM memories").fetchone()[0]
        store.close()

        console.rule(style="dim")
        console.print(f"[bold]Events[/bold]    {total} total  {today_count} today")
        inbox_str = f"[yellow]{pending} pending[/yellow]" if pending else "[dim]0 pending[/dim]"
        console.print(f"[bold]Inbox[/bold]     {inbox_str}  ·  {mem_total} approved memories")
        if active:
            goal = active["goal"] or "no goal set"
            elapsed = int((time.time() - active["started_at"]) / 60)
            console.print(f"[bold]Session[/bold]   {goal} ({elapsed}m active)")
        else:
            console.print("[bold]Session[/bold]   none active")
    except Exception as e:
        console.print(f"[dim]DB not ready: {e}[/dim]")

    # Intelligence layer status
    console.rule(style="dim")
    try:
        from packages.intelligence.router import status as llm_status
        s = llm_status()
        local = s["local_llm"]
        cloud = s["cloud_llm"]
        if local["available"]:
            models = ", ".join(local["models"][:3]) or local["configured_model"]
            console.print(f"[bold]Local LLM[/bold]  [green]✓[/green] {local['base_url']} — {models}")
        else:
            console.print(f"[bold]Local LLM[/bold]  [dim]✗ Ollama not running — install at ollama.ai[/dim]")
        if cloud["available"]:
            console.print(f"[bold]Cloud LLM[/bold]  [green]✓[/green] {cloud['configured_model']}")
        else:
            console.print("[bold]Cloud LLM[/bold]  [dim]✗ set ANTHROPIC_API_KEY to enable[/dim]")
    except Exception:
        pass


# ── stareha session ───────────────────────────────────────────────────────────

@cli.group()
def session():
    """Manage learning/work sessions."""
    pass


@session.command("start")
@click.argument("goal", required=False)
def session_start(goal):
    """Start a tracked session. Shows any pending briefing first."""
    store = _get_store()
    if store.get_active_session():
        console.print("[yellow]A session is already active. Run `stareha session stop` first.[/yellow]")
        store.close()
        return

    # Show pending briefing before starting
    pending = get_pending(store, gtype="briefing")
    if pending:
        latest = pending[0]
        console.print(format_briefing_cli(latest["content"]))
        mark_delivered(store, latest["id"])

    session_id = store.start_session(goal=goal)
    store.close()
    msg = "Session started"
    if goal:
        msg += f": [bold]{goal}[/bold]"
    console.print(f"[green]✓[/green] {msg}")
    console.print("[dim]Run `stareha session stop` when done.[/dim]")


@session.command("stop")
def session_stop():
    """End the current session and trigger a learning run."""
    store = _get_store()
    active = store.get_active_session()
    if not active:
        console.print("[yellow]No active session.[/yellow]")
        store.close()
        return
    store.end_session(active["id"])
    elapsed = int((time.time() - active["started_at"]) / 60)
    console.print(f"[green]✓[/green] Session ended ({elapsed}m)")

    with console.status("[dim]Running learning pass...[/dim]"):
        written = run_learning(store, session_id=active["id"])
    if written:
        console.print(f"[dim]Learning: {written} new candidate(s) added to inbox.[/dim]")
    else:
        console.print("[dim]Learning: no new patterns found.[/dim]")

    # Session summary via local LLM (non-blocking — silently skipped if unavailable)
    from packages.intelligence.summarizer import summarize_session
    from packages.intelligence import local_llm as _llm
    from packages.core.config import load_config as _cfg
    if _llm.is_available(_cfg().local_llm_base_url):
        with console.status("[dim]Generating session summary...[/dim]"):
            summary = summarize_session(store, active["id"])
        if summary:
            console.print(f"\n[dim]Summary:[/dim] {summary}")
    store.close()


@cli.command()
@click.option("--review/--no-review", default=True, help="Review what Stareha noticed.")
def done(review):
    """Finish the current learning session and show a Learning Card."""
    store = _get_store()
    active = store.get_active_session()
    if not active:
        console.print("[yellow]No active learning session.[/yellow]")
        console.print('[dim]Start one with `stareha learn "React forms"`.[/dim]')
        store.close()
        return

    store.end_session(active["id"])
    elapsed = int((time.time() - active["started_at"]) / 60)
    console.print(f"[green]✓[/green] Learning session finished ({elapsed}m)")

    with console.status("[dim]Building your Learning Card...[/dim]"):
        written = run_learning(store, session_id=active["id"])
        prepare_guidance(store, session_id=active["id"])
        card = build_learning_card(store, active["id"])

    if card:
        console.print(format_learning_card_cli(card))
    if written:
        console.print(f"[dim]{written} new thing(s) noticed.[/dim]")

    if review:
        review_notices(
            store,
            console,
            since=active["started_at"],
            project=active["project"],
        )

    store.close()


@cli.command("continue")
def continue_cmd():
    """Resume from the last useful learning point."""
    store = _get_store()
    plan = build_continue_plan(store)
    store.close()

    if not plan:
        console.print("[dim]No previous learning session yet.[/dim]")
        console.print('[dim]Start with `stareha learn "React forms"`.[/dim]')
        return

    console.print(format_continue_plan_cli(plan))
    if plan.get("project"):
        console.print(f"[dim]Project path: {plan['project']}[/dim]")


@session.command("status")
def session_status():
    """Show current session."""
    store = _get_store()
    active = store.get_active_session()
    store.close()
    if not active:
        console.print("No active session.")
        return
    elapsed = int((time.time() - active["started_at"]) / 60)
    goal = active["goal"] or "no goal set"
    console.print(f"[bold]{goal}[/bold]  ({elapsed}m active)")


# ── stareha what-did-you-learn ────────────────────────────────────────────────

@cli.command("what-did-you-learn")
@click.argument("period", default="today",
                type=click.Choice(["today", "yesterday", "session", "week"],
                                  case_sensitive=False))
def what_did_you_learn_cmd(period):
    """Show what Stareha observed and learned in a time period."""
    store = _get_store()
    data = what_did_you_learn(store, period)
    store.close()

    console.print(f"\n[bold]What did I learn {data['period']}?[/bold]\n")
    console.rule(style="dim")

    # Events
    if data["total_events"]:
        parts = "  ".join(
            f"{src}: {cnt}" for src, cnt in sorted(data["events_by_source"].items())
        )
        console.print(f"[bold]Events observed[/bold]  {data['total_events']}  ({parts})")
    else:
        console.print("[bold]Events observed[/bold]  0")

    # Learning runs
    runs = data["runs"]
    if runs:
        total_evts = sum(r.get("events_processed") or 0 for r in runs)
        total_cands = sum(r.get("candidates_generated") or 0 for r in runs)
        console.print(
            f"[bold]Learning runs[/bold]   {len(runs)} run(s) · "
            f"{total_evts} events processed · {total_cands} candidates generated"
        )
    else:
        console.print("[bold]Learning runs[/bold]   none")

    console.rule(style="dim")

    # Candidates
    candidates = data["candidates"]
    if candidates:
        console.print(f"\n[bold]Patterns found:[/bold]  {len(candidates)}\n")
        for c in candidates:
            status_mark = {
                "pending":  "[yellow]pending[/yellow]",
                "approved": "[green]approved ✓[/green]",
                "rejected": "[dim]rejected[/dim]",
            }.get(c["status"], c["status"])
            console.print(f"  [dim]{c['type']}[/dim]  {c['content']}")
            console.print(
                f"    [dim]confidence {c['confidence']:.2f} · {c['source']} · {status_mark}[/dim]"
            )
    else:
        console.print("\n[dim]No patterns extracted.[/dim]")

    # Approved memories
    approved = data["approved"]
    if approved:
        console.rule(style="dim")
        console.print(f"\n[bold]Memories approved:[/bold]  {len(approved)}\n")
        for m in approved:
            short_id = m["id"][:8]
            console.print(f"  [dim][{short_id}][/dim] {m['content']}")
    else:
        console.print(f"\n[dim]Memories approved: 0[/dim]")

    # Pending
    pending = data["pending_in_inbox"]
    console.rule(style="dim")
    if pending:
        console.print(
            f"\n[yellow]{pending} pending in inbox[/yellow] — "
            "run [bold]stareha memory inbox --review[/bold] to action them.\n"
        )
    else:
        console.print("\n[dim]Inbox empty.[/dim]\n")


# ── stareha ledger ─────────────────────────────────────────────────────────────

@cli.command()
@click.option("--limit", "-n", default=10, help="Max runs to show (default 10).")
def ledger(limit):
    """Show the full learning audit log — runs, feedback stats, blocked patterns."""
    store = _get_store()
    runs = recent_runs(store, limit=limit)
    fb = feedback_stats(store)
    rejections = get_rejection_counts(store)
    store.close()

    console.print(f"\n[bold]Learning Ledger[/bold]  (last {limit} runs)\n")
    console.rule(style="dim")

    if not runs:
        console.print("[dim]No learning runs yet. Run `stareha learn` to start.[/dim]")
    else:
        for r in runs:
            started = _fmt_ts(r["started_at"])
            evts = r.get("events_processed") or "-"
            cands = r.get("candidates_generated") or "-"
            status_mark = {
                "completed": "[green]completed[/green]",
                "running":   "[yellow]running[/yellow]",
                "failed":    "[red]failed[/red]",
            }.get(r["status"], r["status"])
            duration = ""
            if r.get("completed_at") and r.get("started_at"):
                secs = r["completed_at"] - r["started_at"]
                duration = f" ({secs}s)"
            console.print(
                f"  [dim]{started}[/dim]  events: {evts}  candidates: {cands}"
                f"  {status_mark}{duration}"
            )

    console.rule(style="dim")

    # Feedback stats
    if fb["total"]:
        rate = f"{int(fb['approval_rate'] * 100)}%" if fb["approval_rate"] is not None else "n/a"
        console.print(
            f"\n[bold]Feedback[/bold]  {fb['total']} total · "
            f"approved: {fb['approved']} · rejected: {fb['rejected']} · "
            f"edited: {fb['edited']} · approval rate: {rate}"
        )
    else:
        console.print("\n[bold]Feedback[/bold]  No feedback recorded yet.")

    # Rejection gates
    if rejections:
        console.print("\n[bold]Feedback gates[/bold]  (pattern types slowed by rejections)")
        from packages.intelligence.learning_runner import _REJECTION_BARS, _confidence_bar
        for (ptype, source), count in sorted(rejections.items(), key=lambda x: -x[1]):
            bar = _confidence_bar(count)
            if bar > 0:
                console.print(
                    f"  [dim]{ptype}[/dim] from {source}  rejected {count}×  "
                    f"→ confidence bar raised to {bar:.0%}"
                )
    else:
        console.print("\n[dim]No pattern types slowed by feedback.[/dim]")

    console.print()


def _fmt_ts(ts: int) -> str:
    import datetime
    return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


# ── stareha learn ─────────────────────────────────────────────────────────────

@cli.command()
@click.argument("goal", nargs=-1)
@click.option("--project", "project", default=None, help="Project path for this session.")
@click.option("--force", is_flag=True, help="Run extraction even if few events since last run.")
def learn(goal, project, force):
    """Start a learning session, or run extraction when no goal is provided."""
    if isinstance(goal, (tuple, list)):
        goal_text = " ".join(goal).strip()
    else:
        goal_text = (goal or "").strip()

    if goal_text:
        store = _get_store()
        active = store.get_active_session()
        if active:
            console.print("[yellow]A learning session is already active.[/yellow]")
            console.print("[dim]Run `stareha done` before starting another one.[/dim]")
            store.close()
            return

        resolution = resolve_project(project, store=store)
        remember_project(store, resolution)
        project_path = resolution.path if resolution else None
        if project_path and list_permissions()["sources"].get("files", {}).get("enabled"):
            enable_source("files", path=project_path)
            config = load_config()
            watched_paths = list(dict.fromkeys([*config.watched_paths, project_path]))
            save_config({"watched_paths": watched_paths})

        pending = get_pending(store, gtype="briefing")
        if pending:
            latest = pending[0]
            console.print(format_briefing_cli(latest["content"]))
            mark_delivered(store, latest["id"])

        store.start_session(goal=goal_text, type="learning", project=project_path)
        store.close()

        console.print(f"[green]✓[/green] Learning started: [bold]{goal_text}[/bold]")
        if resolution:
            console.print(
                f"[dim]Project: {resolution.name} "
                f"({resolution.source}, {resolution.confidence} confidence)[/dim]"
            )
        console.print("[dim]Work normally. Add notes with `stareha note \"...\"`.[/dim]")
        console.print("[dim]Finish with `stareha done`.[/dim]")
        return

    # Advanced/internal behavior: run a standalone learning pass.
    store = _get_store()
    with console.status("[dim]Analysing events...[/dim]"):
        written = run_learning(store, force=force)
    store.close()
    if written:
        console.print(f"[green]✓[/green] {written} new candidate(s) added to inbox.")
        console.print("[dim]Run `stareha memory inbox` to review.[/dim]")
    else:
        console.print("[dim]No new patterns found.[/dim]")


# ── stareha memory ────────────────────────────────────────────────────────────

@cli.group()
def memory():
    """Manage Stareha's memory."""
    pass


@memory.command("inbox")
@click.option("--review", is_flag=True, help="Interactive review mode — act on each candidate.")
def memory_inbox(review):
    """Show pending memory candidates. Use --review for interactive approval."""
    store = _get_store()
    rows = store._conn.execute(
        "SELECT * FROM memory_candidates WHERE status='pending' ORDER BY confidence DESC"
    ).fetchall()

    if not rows:
        console.print("[dim]Inbox empty — no pending candidates.[/dim]")
        store.close()
        return

    console.print(f"\n[bold]Memory Inbox[/bold] — {len(rows)} pending\n")

    for i, row in enumerate(rows, 1):
        short_id = row["id"][:8]
        console.print(f"[bold]{i}.[/bold] [[dim]{short_id}[/dim]]")
        console.print(f"   {row['content']}")
        console.print(
            f"   [dim]type: {row['type']}  source: {row['source']}  "
            f"confidence: {row['confidence']:.2f}  sensitivity: {row['sensitivity']}[/dim]"
        )

        if review:
            action = click.prompt(
                "   Action",
                type=click.Choice(["a", "r", "e", "s"], case_sensitive=False),
                default="s",
                show_default=True,
                prompt_suffix=" (a)pprove (r)eject (e)dit (s)kip: ",
            )
            if action == "a":
                mid = approve_candidate(store, row["id"])
                console.print(f"   [green]✓ Approved → memory {mid[:8]}[/green]")
            elif action == "r":
                reject_candidate(store, row["id"])
                console.print("   [yellow]✗ Rejected[/yellow]")
            elif action == "e":
                new_content = click.edit(row["content"])
                if new_content and new_content.strip() != row["content"]:
                    mid = approve_candidate(store, row["id"], new_content.strip())
                    console.print(f"   [green]✓ Edited and approved → memory {mid[:8]}[/green]")
                else:
                    console.print("   [dim]No change — skipped.[/dim]")
        console.print()

    store.close()

    if not review:
        console.print(
            "[dim]Use `stareha memory review` for interactive approval, or "
            "`stareha memory approve/reject <id>` individually.[/dim]"
        )


@memory.command("review")
def memory_review():
    """Interactive inbox review — shorthand for `stareha memory inbox --review`."""
    ctx = click.get_current_context()
    ctx.invoke(memory_inbox, review=True)


@memory.command("approve")
@click.argument("candidate_id")
def memory_approve(candidate_id):
    """Approve a memory candidate by ID."""
    store = _get_store()
    try:
        mid = approve_candidate(store, candidate_id)
        console.print(f"[green]✓[/green] Approved → memory [{mid[:8]}]")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        store.close()


@memory.command("reject")
@click.argument("candidate_id")
def memory_reject(candidate_id):
    """Reject a memory candidate by ID."""
    store = _get_store()
    try:
        reject_candidate(store, candidate_id)
        console.print("[yellow]✗[/yellow] Rejected.")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        store.close()


@memory.command("edit")
@click.argument("candidate_id")
@click.option("--content", "-c", default=None, help="New content (opens editor if omitted).")
def memory_edit(candidate_id, content):
    """Edit a candidate's content and approve it."""
    store = _get_store()
    try:
        from packages.memory.manager import _resolve_id
        candidate_id = _resolve_id(store, "memory_candidates", candidate_id)
        row = store._conn.execute(
            "SELECT * FROM memory_candidates WHERE id=?", (candidate_id,)
        ).fetchone()
        if not row:
            console.print(f"[red]Candidate not found:[/red] {candidate_id}")
            return
        new_content = content or click.edit(row["content"])
        if not new_content or new_content.strip() == row["content"]:
            console.print("[dim]No change — skipped.[/dim]")
            return
        mid = approve_candidate(store, candidate_id, new_content.strip())
        console.print(f"[green]✓[/green] Edited and approved → memory [{mid[:8]}]")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        store.close()


@memory.command("forget")
@click.argument("memory_id")
@click.option("--yes", is_flag=True, help="Skip confirmation prompt.")
def memory_forget(memory_id, yes):
    """Permanently delete an approved memory."""
    store = _get_store()
    try:
        from packages.memory.manager import _resolve_id
        resolved = _resolve_id(store, "memories", memory_id)
        row = store._conn.execute(
            "SELECT content FROM memories WHERE id=?", (resolved,)
        ).fetchone()
        if not row:
            console.print(f"[red]Memory not found:[/red] {memory_id}")
            return
        memory_id = resolved
        console.print(f"[dim]{row['content']}[/dim]")
        if not yes and not click.confirm("Delete this memory permanently?", default=False):
            console.print("[dim]Cancelled.[/dim]")
            return
        forget_memory(store, memory_id)
        console.print("[yellow]✓[/yellow] Memory deleted.")
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
    finally:
        store.close()


@memory.command("why")
@click.argument("memory_id")
def memory_why(memory_id):
    """Show why a memory was learned — full provenance and evidence trail."""
    store = _get_store()
    try:
        result = get_memory_why(store, memory_id)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        store.close()
        return
    store.close()

    m = result["memory"]
    events = result["events"]

    console.print(f"\n[bold]Memory[/bold] [{m['id'][:8]}]")
    console.print(f'  "{m["content"]}"')
    console.rule(style="dim")
    console.print(f"[dim]type: {m['type']}  source: {m['source']}  "
                  f"confidence: {m['confidence']:.2f}  "
                  f"model: {m['model_used']}[/dim]")
    if m.get("project"):
        from pathlib import Path as P
        console.print(f"[dim]project: {P(m['project']).name}[/dim]")

    import datetime
    approved = datetime.datetime.fromtimestamp(m["approved_at"]).strftime("%Y-%m-%d %H:%M")
    console.print(f"[dim]approved: {approved}[/dim]")

    if m.get("user_edited"):
        console.print("[dim]user-edited: yes[/dim]")

    console.rule("[dim]Evidence[/dim]", style="dim")
    if not events:
        console.print("[dim]No raw events linked (project_context candidates have no event IDs).[/dim]")
    else:
        for e in events[:10]:
            try:
                data = json.loads(e["content"])
                cmd = data.get("cmd", e["content"])
            except Exception:
                cmd = e["content"]
            console.print(f"  [dim]·[/dim] {cmd[:80]}")
        if len(events) > 10:
            console.print(f"  [dim]... and {len(events) - 10} more[/dim]")


@memory.command("list")
@click.option("--project", "-p", default=None, help="Filter by project name.")
@click.option("--type", "-t", "mem_type", default=None, help="Filter by type.")
@click.option("--source", "-s", default=None, help="Filter by source.")
@click.option("--limit", "-n", default=30, help="Max results (default 30).")
def memory_list(project, mem_type, source, limit):
    """List approved memories."""
    store = _get_store()
    rows = list_memories(store, project=project, type=mem_type, source=source, limit=limit)
    store.close()

    if not rows:
        console.print("[dim]No memories found.[/dim]")
        return

    console.print(f"\n[bold]Memories[/bold] — {len(rows)} results\n")
    for m in rows:
        short_id = m["id"][:8]
        from pathlib import Path as P
        proj = P(m["project"]).name if m.get("project") else "-"
        console.print(f"[dim][{short_id}][/dim] [{m['type']}] {m['content']}")
        console.print(f"   [dim]project: {proj}  confidence: {m['confidence']:.2f}[/dim]")
        console.print()


@memory.command("search")
@click.argument("query")
def memory_search(query):
    """Full-text search across approved memories."""
    store = _get_store()
    rows = search_memories(store, query)
    store.close()

    if not rows:
        console.print(f"[dim]No memories match: {query}[/dim]")
        return

    console.print(f"\n[bold]Search:[/bold] {query} — {len(rows)} results\n")
    for m in rows:
        short_id = m["id"][:8]
        console.print(f"[dim][{short_id}][/dim] {m['content']}")
        console.print()


@memory.command("sources")
@click.argument("memory_id")
def memory_sources(memory_id):
    """Show raw events that are evidence for a memory."""
    store = _get_store()
    try:
        events = get_sources(store, memory_id)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        store.close()
        return
    store.close()

    if not events:
        console.print("[dim]No linked events (project_context memories have no event IDs).[/dim]")
        return

    console.print(f"\n[bold]Sources for[/bold] [{memory_id[:8]}] — {len(events)} events\n")
    for e in events:
        try:
            data = json.loads(e["content"])
            cmd = data.get("cmd", e["content"])
        except Exception:
            cmd = e["content"]
        import datetime
        ts = datetime.datetime.fromtimestamp(e["created_at"]).strftime("%Y-%m-%d %H:%M")
        console.print(f"  [dim]{ts}[/dim]  {cmd[:80]}")


@memory.command("stats")
def memory_stats_cmd():
    """Show memory counts and breakdown by source and type."""
    store = _get_store()
    stats = memory_stats(store)
    store.close()

    console.print(f"[bold]Memories[/bold]   {stats['total']} approved  "
                  f"{stats['pending']} pending in inbox  "
                  f"{stats['rejected']} rejected")
    console.print(f"[bold]Events[/bold]     {stats['events_total']} total in ledger")

    if stats["by_source"]:
        parts = "  ".join(f"{s}: {c}" for s, c in sorted(stats["by_source"].items()))
        console.print(f"[bold]By source[/bold]  {parts}")

    if stats["by_type"]:
        parts = "  ".join(f"{t}: {c}" for t, c in sorted(stats["by_type"].items()))
        console.print(f"[bold]By type[/bold]    {parts}")


# ── stareha prep / brief / quiz / note ───────────────────────────────────────

@cli.command()
@click.option("--quiz", is_flag=True, help="Also generate a quiz for the top weak concept.")
def prep(quiz):
    """Prepare guidance for the next session — briefing + optional quiz."""
    store = _get_store()
    with console.status("[dim]Analysing and preparing guidance...[/dim]"):
        ids = prepare_guidance(store, with_quiz=quiz)
    items = get_all_guidance(store)
    store.close()

    console.print(f"\n[green]✓[/green] {len(ids)} item(s) prepared.\n")
    for item in items:
        if item["id"] in ids:
            console.print(f"  [dim][{item['type']}][/dim] {item['title']}")
            if item["type"] == "briefing":
                console.print(format_briefing_cli(item["content"]))
            elif item["type"] == "quiz":
                q = item["content"]
                console.print(
                    f"  [dim]Topic: {q.get('topic')}  ·  "
                    f"{len(q.get('questions', []))} questions  ·  "
                    f"generated by: {item.get('generated_by', '?')}[/dim]"
                )
                console.print("  Run: [bold]stareha quiz[/bold] to start\n")


@cli.command()
def brief():
    """Show the latest prepared briefing."""
    store = _get_store()
    pending = get_pending(store, gtype="briefing")
    if not pending:
        # Fall back to most recent delivered
        rows = store._conn.execute(
            "SELECT * FROM prepared_guidance WHERE type='briefing' "
            "ORDER BY prepared_at DESC LIMIT 1"
        ).fetchall()
        if rows:
            import json as _json
            r = dict(rows[0])
            r["content"] = _json.loads(r["content"])
            pending = [r]
    store.close()

    if not pending:
        console.print("[dim]No briefing prepared yet. Run `stareha prep` first.[/dim]")
        return

    console.print(format_briefing_cli(pending[0]["content"]))


@cli.command()
@click.option("--cloud", is_flag=True, help="Allow Claude fallback if local LLM is unavailable.")
@click.argument("topic", required=False)
def quiz(topic, cloud):
    """Run an interactive quiz — on a topic or from the latest prepared quiz."""
    store = _get_store()

    if topic:
        # Generate on the fly for the requested topic
        with console.status("[dim]Generating quiz...[/dim]"):
            quiz_data = generate_quiz(topic, n=5, allow_cloud=cloud)
    else:
        # Use latest prepared quiz
        pending_q = get_pending(store, gtype="quiz")
        if pending_q:
            quiz_data = pending_q[0]["content"]
            guidance_id = pending_q[0]["id"]
        else:
            console.print("[dim]No quiz prepared. Run `stareha prep --quiz` or `stareha quiz <topic>`.[/dim]")
            store.close()
            return
        guidance_id = pending_q[0]["id"]

    store.close()

    # Run interactive quiz
    results = run_quiz_interactive(quiz_data, console)

    # Save results back if from prepared guidance
    if not topic and "guidance_id" in dir():
        store = _get_store()
        quiz_data["results"] = results
        from packages.guidance.prep import update_content
        update_content(store, guidance_id, quiz_data)
        mark_completed(store, guidance_id)
        store.close()


@cli.command()
@click.argument("text", nargs=-1)
def note(text):
    """Add a manual note — e.g. `stareha note \"struggling with async/await\"`."""
    if isinstance(text, (tuple, list)):
        note_text = " ".join(text).strip()
    else:
        note_text = (text or "").strip()
    if not note_text:
        console.print("[yellow]Write a note after the command.[/yellow]")
        console.print('[dim]Example: `stareha note "I am confused about controlled inputs"`[/dim]')
        return

    store = _get_store()
    active = store.get_active_session()
    add_note(
        store,
        note_text,
        session_id=active["id"] if active else None,
        project=active["project"] if active else None,
    )
    store.close()
    console.print(f"[green]✓[/green] Note saved. This will inform your next guidance.")
    if active:
        console.print("[dim]Linked to the current learning session.[/dim]")
    else:
        console.print(f"[dim]Tip: run `stareha prep` to regenerate your briefing.[/dim]")


# ── stareha local-llm ────────────────────────────────────────────────────────

@cli.group("local-llm")
def local_llm_group():
    """Manage the local LLM (Ollama) integration."""
    pass


@local_llm_group.command("status")
def local_llm_status():
    """Show Ollama availability, models, and config."""
    from packages.intelligence.router import status as llm_status
    from packages.intelligence.prompts import list_prompts
    s = llm_status()
    local = s["local_llm"]
    cloud = s["cloud_llm"]

    console.print("\n[bold]Intelligence Policy Status[/bold]\n")
    console.rule("[dim]Layer 2: Local LLM (Ollama)[/dim]", style="dim")
    if local["available"]:
        console.print(f"[green]✓ Available[/green]  {local['base_url']}")
        console.print(f"  Configured model: {local['configured_model']}")
        models = local["models"]
        if models:
            console.print(f"  Available models: {', '.join(models)}")
        else:
            console.print(f"  [yellow]No models pulled yet.[/yellow]  Run: stareha local-llm pull {local['configured_model']}")
    else:
        console.print("[dim]✗ Ollama not running[/dim]")
        console.print("  Install: curl -fsSL https://ollama.ai/install.sh | sh")
        console.print(f"  Then:    ollama pull {local['configured_model']}")

    console.rule("[dim]Layer 3: Cloud LLM (Claude)[/dim]", style="dim")
    if cloud["available"]:
        console.print(f"[green]✓ Available[/green]  {cloud['configured_model']}")
    else:
        console.print("[dim]✗ Not configured[/dim]")
        console.print("  Set ANTHROPIC_API_KEY to enable cloud LLM fallback")

    console.rule("[dim]Prompt templates[/dim]", style="dim")
    for p in list_prompts():
        src = "[green]custom[/green]" if p["source"] == "custom" else "[dim]bundled[/dim]"
        console.print(f"  {src}  {p['name']}")
    console.print("\n  Edit: [dim]~/.stareha/prompts/<name>.txt[/dim]")
    console.print("  Export defaults: stareha local-llm prompts\n")


@local_llm_group.command("pull")
@click.argument("model", default=None, required=False)
def local_llm_pull(model):
    """Pull a model into Ollama (e.g. llama3.2:3b, mistral:7b)."""
    from packages.intelligence import local_llm as _llm
    from packages.core.config import load_config as _cfg
    config = _cfg()
    target = model or config.local_llm_model

    if not _llm.is_available(config.local_llm_base_url):
        console.print("[red]Ollama is not running.[/red] Start it first: ollama serve")
        return

    console.print(f"Pulling [bold]{target}[/bold]... (this may take several minutes)")
    ok = _llm.pull(target, base_url=config.local_llm_base_url)
    if ok:
        console.print(f"[green]✓[/green] {target} ready.")
    else:
        console.print(f"[red]Failed to pull {target}.[/red] Check: ollama pull {target}")


@local_llm_group.command("prompts")
def local_llm_prompts():
    """Export default prompt templates to ~/.stareha/prompts/ for editing."""
    from packages.intelligence.prompts import export_defaults, list_prompts, _PROMPTS_DIR
    export_defaults()
    console.print(f"[green]✓[/green] Default prompts written to {_PROMPTS_DIR}\n")
    for p in list_prompts():
        console.print(f"  {p['name']}.txt")
    console.print("\nEdit any file to customise how Stareha generates summaries and quizzes.")


# ── stareha talk ──────────────────────────────────────────────────────────────

@cli.command()
@click.option("--cloud", is_flag=True, help="Allow cloud LLM (Claude) — uses ANTHROPIC_API_KEY.")
def talk(cloud):
    """
    Conversational mode — ask Stareha about your work and learning.

    Context: approved memories only (no raw events sent to any LLM).
    Local LLM is used by default; --cloud enables Claude.
    """
    from packages.intelligence import router
    from packages.memory.manager import list_memories as _list_mems

    store = _get_store()
    memories = _list_mems(store, limit=20)
    store.close()

    if not memories and not cloud:
        console.print("[dim]No approved memories yet — run `stareha learn` and approve some candidates first.[/dim]")
        return

    # Build context from memories (summaries only — never raw events)
    mem_lines = "\n".join(f"- {m['content']}" for m in memories[:15])
    system = f"""You are Stareha, a local-first AI companion for developers.
You have access to this user's approved work memories:

{mem_lines}

Answer concisely. Reference specific memories when relevant.
If you don't know something, say so. Never invent details."""

    llm_s = router.status()
    local_ok = llm_s["local_llm"]["available"]
    cloud_ok = llm_s["cloud_llm"]["available"] and cloud

    if not local_ok and not cloud_ok:
        console.print("[dim]No LLM available.[/dim]")
        if not local_ok:
            console.print("  Start Ollama: [bold]ollama serve[/bold]")
        if not cloud_ok:
            console.print("  Or use: [bold]stareha talk --cloud[/bold]  (requires ANTHROPIC_API_KEY)")
        return

    layer_info = []
    if local_ok:
        layer_info.append(f"local ({llm_s['local_llm']['configured_model']})")
    if cloud_ok:
        layer_info.append("cloud (Claude)")
    console.print(f"\n[bold]Stareha[/bold]  [dim]using: {', '.join(layer_info)}[/dim]")
    console.print("[dim]Type your message. Ctrl+C or blank line to exit.[/dim]\n")

    history: list[dict] = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Exited talk mode.[/dim]")
            break
        if not user_input:
            console.print("[dim]Exited talk mode.[/dim]")
            break

        history.append({"role": "user", "content": user_input})

        with console.status("[dim]Thinking...[/dim]"):
            result, used_layer = router.chat(
                history, system=system, allow_cloud=cloud, timeout=60.0
            )

        if result:
            history.append({"role": "assistant", "content": result})
            console.print(f"\n[bold]Stareha[/bold] [dim]({used_layer})[/dim]:")
            console.print(result)
            console.print()
        else:
            console.print("[dim]No response — LLM may be busy or unavailable.[/dim]")
            break


# ── stareha permissions ───────────────────────────────────────────────────────

@cli.group()
def permissions():
    """Manage data source permissions."""
    pass


@permissions.command("list")
def permissions_list():
    """Show all current permissions."""
    perms = list_permissions()
    console.print_json(json.dumps(perms, indent=2))


@permissions.command("add")
@click.argument("source")
@click.argument("path", required=False)
def permissions_add(source, path):
    """Enable a data source."""
    enable_source(source, path=path)
    msg = f"[green]✓[/green] Enabled: {source}"
    if path:
        msg += f" → {path}"
    console.print(msg)


# ── stareha cloud-llm ────────────────────────────────────────────────────────

PROVIDER_IDS: dict[str, str] = {
    "claude_code_oauth": "Claude Code (claude.ai subscription)",
    "anthropic":         "Anthropic API key",
    "openai":            "OpenAI",
    "groq":              "Groq",
    "gemini":            "Google Gemini",
    "openai_compat":     "Custom OpenAI-compatible endpoint",
}


def _provider_is_configured(provider_id: str, provider_configs: dict) -> bool:
    cfg = provider_configs.get(provider_id, {})
    if provider_id == "claude_code_oauth":
        return bool(cfg.get("access_token"))
    if provider_id == "openai_compat":
        return bool(cfg.get("base_url"))
    return bool(cfg.get("api_key"))


@cli.group("cloud-llm")
def cloud_llm_group():
    """Manage cloud LLM providers (Anthropic, OpenAI, Groq, Gemini, and more)."""
    pass


@cloud_llm_group.command("list")
def cloud_llm_list():
    """Show all 6 providers with configuration status."""
    raw = _load_raw_config()
    active = raw.get("cloud_provider", "")
    provider_configs = raw.get("provider_configs", {})

    table = Table(title="Cloud LLM Providers", box=None, show_lines=False, padding=(0, 2))
    table.add_column("Provider", style="bold")
    table.add_column("Display Name")
    table.add_column("Status")
    table.add_column("Active")

    for pid, display in PROVIDER_IDS.items():
        configured = _provider_is_configured(pid, provider_configs)
        status_str = "[green]configured ✓[/green]" if configured else "[dim]not configured —[/dim]"
        active_str = "[yellow]★[/yellow]" if pid == active else ""
        table.add_row(pid, display, status_str, active_str)

    console.print()
    console.print(table)
    console.print()
    if not active:
        console.print("[dim]No active provider. Run: stareha cloud-llm use <provider>[/dim]")
    else:
        console.print(f"[dim]Active: {active}. Switch with: stareha cloud-llm use <provider>[/dim]")
    console.print()


@cloud_llm_group.command("status")
def cloud_llm_status():
    """Show the active provider, model, and credential status."""
    raw = _load_raw_config()
    active = raw.get("cloud_provider", "")
    provider_configs = raw.get("provider_configs", {})

    console.print()
    if not active:
        console.print("[yellow]No active cloud LLM provider.[/yellow]")
        console.print("[dim]Run `stareha cloud-llm list` to see all providers.[/dim]")
        console.print()
        return

    display = PROVIDER_IDS.get(active, active)
    configured = _provider_is_configured(active, provider_configs)
    cred_str = "[green]credentials present[/green]" if configured else "[red]not configured[/red]"
    cfg = provider_configs.get(active, {})
    model = cfg.get("model", "[dim]default[/dim]")

    console.print(f"[bold]Active provider:[/bold]  {active}  ({display})")
    console.print(f"[bold]Model:[/bold]            {model}")
    console.print(f"[bold]Credentials:[/bold]      {cred_str}")

    if active == "openai_compat" and cfg.get("base_url"):
        console.print(f"[bold]Base URL:[/bold]         {cfg['base_url']}")

    console.print()
    console.print("[dim]Run `stareha cloud-llm list` to see all providers.[/dim]")
    console.print()


@cloud_llm_group.command("use")
@click.argument("provider")
def cloud_llm_use(provider):
    """Set the active cloud LLM provider."""
    if provider not in PROVIDER_IDS:
        valid = ", ".join(PROVIDER_IDS.keys())
        console.print(f"[red]Unknown provider:[/red] {provider}")
        console.print(f"[dim]Valid providers: {valid}[/dim]")
        raise SystemExit(1)

    raw = _load_raw_config()
    provider_configs = raw.get("provider_configs", {})
    save_config({"cloud_provider": provider})
    console.print(f"[green]✓[/green] Active provider set to: {provider}  ({PROVIDER_IDS[provider]})")

    if not _provider_is_configured(provider, provider_configs):
        if provider == "claude_code_oauth":
            console.print("[dim]Run `stareha cloud-llm connect` to authenticate with Claude Code.[/dim]")
        else:
            console.print(f"[dim]Run `stareha cloud-llm set-key {provider}` to add credentials.[/dim]")


@cloud_llm_group.command("set-key")
@click.argument("provider")
@click.argument("key", required=False)
def cloud_llm_set_key(provider, key):
    """Set the API key for a provider. Use `connect` for Claude Code OAuth."""
    if provider not in PROVIDER_IDS:
        valid = ", ".join(PROVIDER_IDS.keys())
        console.print(f"[red]Unknown provider:[/red] {provider}")
        console.print(f"[dim]Valid providers: {valid}[/dim]")
        raise SystemExit(1)

    if provider == "claude_code_oauth":
        console.print("[yellow]Claude Code uses OAuth, not an API key.[/yellow]")
        console.print("[dim]Run `stareha cloud-llm connect` to authenticate.[/dim]")
        return

    raw = _load_raw_config()
    provider_configs = raw.get("provider_configs", {})

    if provider == "openai_compat":
        base_url = click.prompt("Base URL (e.g. http://localhost:11434/v1)", default="http://localhost:11434/v1")
        api_key_val = key or click.prompt("API key (leave blank if not required)", default="", hide_input=True)
        model = click.prompt("Model name (e.g. llama3.2:3b)", default="llama3.2:3b")
        existing = provider_configs.get("openai_compat", {})
        existing.update({
            "base_url": base_url.strip(),
            "api_key": api_key_val.strip(),
            "model": model.strip(),
        })
        provider_configs["openai_compat"] = existing
    else:
        api_key_val = key or click.prompt(f"Enter {PROVIDER_IDS[provider]} API key", hide_input=True)
        if not api_key_val.strip():
            console.print("[yellow]No key entered — cancelled.[/yellow]")
            return
        existing = provider_configs.get(provider, {})
        existing["api_key"] = api_key_val.strip()
        provider_configs[provider] = existing

    save_config({"provider_configs": provider_configs})
    console.print(f"[green]✓[/green] Credentials saved for: {provider}  ({PROVIDER_IDS[provider]})")

    current_active = raw.get("cloud_provider", "")
    if current_active != provider:
        if click.confirm(f"Set {provider} as the active provider?", default=True):
            save_config({"cloud_provider": provider})
            console.print(f"[green]✓[/green] Active provider set to: {provider}")


@cloud_llm_group.command("connect")
def cloud_llm_connect():
    """Authenticate with Claude Code using OAuth (claude.ai subscription)."""
    try:
        from packages.intelligence.providers.claude_code_oauth import run_oauth_flow
    except ImportError:
        console.print("[red]Claude Code OAuth provider not available in this build.[/red]")
        console.print("[dim]This feature requires the claude_code_oauth provider package.[/dim]")
        return

    console.print("\n[bold]Claude Code OAuth[/bold]")
    console.print("[dim]This will open a browser window to authenticate with claude.ai.[/dim]\n")

    success = run_oauth_flow()

    if success:
        console.print("\n[green]✓[/green] Claude Code connected successfully.")
        raw = _load_raw_config()
        current_active = raw.get("cloud_provider", "")
        if current_active != "claude_code_oauth":
            if click.confirm("Set Claude Code as the active provider?", default=True):
                save_config({"cloud_provider": "claude_code_oauth"})
                console.print("[green]✓[/green] Active provider set to: claude_code_oauth")
    else:
        console.print("\n[red]OAuth flow did not complete.[/red]")
        console.print("[dim]Try again or check your claude.ai subscription.[/dim]")


@cloud_llm_group.command("clear")
@click.argument("provider")
def cloud_llm_clear(provider):
    """Clear stored credentials for a provider."""
    if provider not in PROVIDER_IDS:
        valid = ", ".join(PROVIDER_IDS.keys())
        console.print(f"[red]Unknown provider:[/red] {provider}")
        console.print(f"[dim]Valid providers: {valid}[/dim]")
        raise SystemExit(1)

    raw = _load_raw_config()
    provider_configs = raw.get("provider_configs", {})

    if not provider_configs.get(provider):
        console.print(f"[dim]No credentials stored for: {provider}[/dim]")
        return

    console.print(f"[bold]Provider:[/bold] {provider}  ({PROVIDER_IDS[provider]})")
    if not click.confirm("Clear stored credentials?", default=False):
        console.print("[dim]Cancelled.[/dim]")
        return

    provider_configs.pop(provider, None)
    save_config({"provider_configs": provider_configs})
    console.print(f"[green]✓[/green] Credentials cleared for: {provider}")

    current_active = raw.get("cloud_provider", "")
    if current_active == provider:
        save_config({"cloud_provider": ""})
        console.print("[yellow]Active provider unset (was this provider).[/yellow]")
        console.print("[dim]Run `stareha cloud-llm use <provider>` to set a new active provider.[/dim]")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cli()
