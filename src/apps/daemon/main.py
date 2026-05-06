"""
Stareha daemon entry point.
Runs as a systemd user service.
PID file: ~/.stareha/daemon.pid
"""
import os
import signal
import sys
import threading
import time
from pathlib import Path

# Add src/ to path so packages resolve
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.core.config import load_config, ensure_dirs
from packages.core.db import Store
from packages.permissions import can_collect, list_permissions
from packages.collectors.terminal.history_scanner import scan_history
from packages.collectors.terminal.hook_receiver import start_receiver
from packages.collectors.files.watcher import start_watcher
from packages.collectors.claude_code import scan_claude_code
from packages.collectors.browser import scan_browser_history

PID_PATH = Path.home() / ".stareha" / "daemon.pid"


def _write_pid() -> None:
    PID_PATH.parent.mkdir(parents=True, exist_ok=True)
    PID_PATH.write_text(str(os.getpid()))


def _clear_pid() -> None:
    PID_PATH.unlink(missing_ok=True)


def _handle_shutdown(store: Store) -> None:
    def _handler(sig, frame):
        store.close()
        _clear_pid()
        sys.exit(0)
    signal.signal(signal.SIGTERM, _handler)
    signal.signal(signal.SIGINT, _handler)


def run() -> None:
    ensure_dirs()
    config = load_config()
    store = Store(config.db_path)

    _write_pid()
    _handle_shutdown(store)

    threads: list[threading.Thread] = []
    stop_event = threading.Event()

    # Scan all permitted sources on start
    if can_collect("terminal"):
        imported = scan_history(store)
        print(f"[stareha] terminal: {imported} history events", flush=True)

    if can_collect("claude_code"):
        imported = scan_claude_code(store)
        print(f"[stareha] claude_code: {imported} sessions", flush=True)

    if can_collect("browser"):
        imported = scan_browser_history(store)
        print(f"[stareha] browser: {imported} history events", flush=True)

    # Start live hook receiver
    if can_collect("terminal"):
        t = start_receiver(store, port=config.daemon_port)
        threads.append(t)
        print(f"[stareha] hook receiver on port {config.daemon_port}", flush=True)

    # Start file watchers for permitted paths
    watched = [
        p for p in config.watched_paths
        if can_collect("files", p)
    ]
    if watched:
        t = start_watcher(watched, store, stop_event)
        threads.append(t)
        print(f"[stareha] watching {len(watched)} path(s)", flush=True)

    print("[stareha] daemon running", flush=True)

    # Keep alive — systemd will restart on exit
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()
        store.close()
        _clear_pid()


if __name__ == "__main__":
    run()
