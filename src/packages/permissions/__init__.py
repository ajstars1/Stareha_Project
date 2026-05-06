import json
from pathlib import Path
from typing import Optional

PERMISSIONS_PATH = Path.home() / ".stareha" / "permissions.json"

DEFAULT_PERMISSIONS: dict = {
    "sources": {
        "terminal": {"enabled": False, "watch": False},
        "files": {"enabled": False, "paths": []},
        "claude_code": {"enabled": False},
        "browser": {"enabled": False},
        "app_usage": {"enabled": False},
    },
    "actions": {"approved": [], "blocked": []},
}


def _load() -> dict:
    if not PERMISSIONS_PATH.exists():
        return DEFAULT_PERMISSIONS.copy()
    with open(PERMISSIONS_PATH) as f:
        return json.load(f)


def _save(data: dict) -> None:
    PERMISSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PERMISSIONS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def can_collect(source: str, path: Optional[str] = None) -> bool:
    data = _load()
    src = data["sources"].get(source, {})
    if not src.get("enabled", False):
        return False
    if path and source == "files":
        allowed = src.get("paths", [])
        return any(path.startswith(p) for p in allowed)
    return True


def enable_source(source: str, path: Optional[str] = None, watch: bool = False) -> None:
    data = _load()
    if source not in data["sources"]:
        data["sources"][source] = {}
    data["sources"][source]["enabled"] = True
    if watch:
        data["sources"][source]["watch"] = True
    if path and source == "files":
        paths = data["sources"][source].get("paths", [])
        expanded = str(Path(path).expanduser())
        if expanded not in paths:
            paths.append(expanded)
        data["sources"][source]["paths"] = paths
    _save(data)


def disable_source(source: str) -> None:
    data = _load()
    if source in data["sources"]:
        data["sources"][source]["enabled"] = False
    _save(data)


def list_permissions() -> dict:
    return _load()
