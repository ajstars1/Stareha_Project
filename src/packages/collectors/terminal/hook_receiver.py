"""
Live terminal hook receiver.
Listens on localhost:7431 for commands sent by the shell hook.
Shell hook is installed to ~/.zshrc by `stareha init`.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

from packages.shared.redact import redact_sensitive_text
from packages.permissions import can_collect

SHELL_HOOK_ZSH = """
# Stareha shell integration — added by `stareha init`
_stareha_hook() {
  local cmd="$1" exit_code="$?" pwd="$PWD"
  (curl -sf -X POST http://localhost:7431/event \\
    -H 'Content-Type: application/json' \\
    -d "{\\"type\\":\\"command\\",\\"cmd\\":\\"$cmd\\",\\"exit\\":$exit_code,\\"pwd\\":\\"$pwd\\",\\"ts\\":$(date +%s)}" \\
    >/dev/null 2>&1 &)
}
precmd_functions+=(_stareha_hook)
""".strip()

SHELL_HOOK_BASH = """
# Stareha shell integration — added by `stareha init`
_stareha_hook() {
  curl -sf -X POST http://localhost:7431/event \\
    -H 'Content-Type: application/json' \\
    -d "{\\"type\\":\\"command\\",\\"cmd\\":\\"$BASH_COMMAND\\",\\"exit\\":$?,\\"pwd\\":\\"$PWD\\",\\"ts\\":$(date +%s)}" \\
    2>/dev/null &
}
trap '_stareha_hook' DEBUG
""".strip()


class _HookHandler(BaseHTTPRequestHandler):
    store = None  # injected at startup

    def do_POST(self):
        if self.path != "/event":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
            _handle_event(data, self.store)
            self.send_response(200)
        except Exception:
            self.send_response(400)
        self.end_headers()

    def log_message(self, *args):
        pass  # silence default HTTP logs


def _handle_event(data: dict, store) -> None:
    if store is None:
        return

    cmd = data.get("cmd", "").strip()
    if not cmd:
        return

    if not can_collect("terminal"):
        return
    cmd = redact_sensitive_text(cmd)

    store.write_event(
        type="command_run",
        source="terminal",
        content=json.dumps({
            "cmd": cmd,
            "exit": data.get("exit", 0),
            "pwd": data.get("pwd", ""),
            "ts": data.get("ts"),
        }),
        project=_detect_project(data.get("pwd", "")),
        redacted=True,
    )


def _detect_project(pwd: str) -> Optional[str]:
    from pathlib import Path
    import subprocess
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=pwd, capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def start_receiver(store, port: int = 7431) -> threading.Thread:
    _HookHandler.store = store
    server = HTTPServer(("127.0.0.1", port), _HookHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return t
