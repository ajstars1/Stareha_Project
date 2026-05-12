"""Project registry backed by the existing metadata table."""

import json
import time

from packages.core.db import Store
from packages.experience.project_resolver import ProjectResolution

REGISTRY_KEY = "experience.project_registry"


def list_projects(store: Store) -> list[dict]:
    raw = store.get_meta(REGISTRY_KEY)
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        return []
    return data if isinstance(data, list) else []


def remember_project(store: Store, resolution: ProjectResolution | None) -> None:
    if resolution is None:
        return
    projects = list_projects(store)
    now = int(time.time())
    next_row = {
        "path": resolution.path,
        "name": resolution.name,
        "source": resolution.source,
        "confidence": resolution.confidence,
        "workspace_root": resolution.workspace_root,
        "last_active_at": now,
    }
    kept = [p for p in projects if p.get("path") != resolution.path]
    store.set_meta(REGISTRY_KEY, json.dumps([next_row, *kept][:50]))

