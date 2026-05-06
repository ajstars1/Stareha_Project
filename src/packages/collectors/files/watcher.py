"""
File system watcher using inotify-simple.
Watches permitted project directories for file saves.
Never stores file contents — only path, extension, timestamp.

Copy pattern from: official_claude_code/src/utils/FileWatcher.ts
"""
import json
import threading
from pathlib import Path
from typing import Optional

from packages.permissions import can_collect

try:
    import inotify_simple
    INOTIFY_AVAILABLE = True
except ImportError:
    INOTIFY_AVAILABLE = False


def _detect_project(path: str) -> Optional[str]:
    """Walk up directory tree to find git root."""
    p = Path(path)
    for parent in [p, *p.parents]:
        if (parent / ".git").exists():
            return str(parent)
    return None


def watch(paths: list[str], store, stop_event: Optional[threading.Event] = None) -> None:
    """
    Blocking file watcher. Run in a daemon thread.
    Fires 'file_edit' events on IN_CLOSE_WRITE (file saved).
    """
    if not INOTIFY_AVAILABLE:
        raise RuntimeError("inotify-simple not installed. Run: uv add inotify-simple")

    inotify = inotify_simple.INotify()
    watch_flags = inotify_simple.flags.CLOSE_WRITE | inotify_simple.flags.CREATE

    wd_to_path: dict[int, str] = {}

    for path in paths:
        expanded = str(Path(path).expanduser())
        if not can_collect("files", expanded):
            continue
        wd = inotify.add_watch(expanded, watch_flags)
        wd_to_path[wd] = expanded

    stop = stop_event or threading.Event()

    while not stop.is_set():
        events = inotify.read(timeout=1000)  # 1s timeout to check stop_event
        for event in events:
            flags = inotify_simple.flags.from_mask(event.mask)
            if inotify_simple.flags.CLOSE_WRITE not in flags:
                continue

            dir_path = wd_to_path.get(event.wd, "")
            if not dir_path or not event.name:
                continue

            file_path = str(Path(dir_path) / event.name)
            ext = Path(event.name).suffix

            # Skip hidden files and common noise
            if event.name.startswith(".") or ext in {".swp", ".tmp", ".pyc"}:
                continue

            project = _detect_project(dir_path)

            store.write_event(
                type="file_edit",
                source="files",
                content=json.dumps({
                    "path": file_path,
                    "name": event.name,
                    "ext": ext,
                }),
                project=project,
                redacted=False,
            )


def start_watcher(paths: list[str], store, stop_event: Optional[threading.Event] = None) -> threading.Thread:
    t = threading.Thread(
        target=watch,
        args=(paths, store, stop_event),
        daemon=True,
        name="stareha-file-watcher",
    )
    t.start()
    return t
