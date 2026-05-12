"""Resolve the active project without scanning the full workspace."""

import json
from dataclasses import dataclass
from pathlib import Path

from packages.core.config import CONFIG_PATH
from packages.core.db import Store

MANIFEST_FILES = (
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "requirements.txt",
)


@dataclass
class ProjectResolution:
    path: str
    name: str
    source: str
    confidence: str
    workspace_root: str | None = None


def _as_dir(path: Path) -> Path:
    return path.parent if path.is_file() else path


def _nearest_with_child(start: Path, child: str) -> Path | None:
    p = _as_dir(start.resolve())
    for candidate in (p, *p.parents):
        if (candidate / child).exists():
            return candidate
    return None


def _nearest_manifest(start: Path) -> Path | None:
    p = _as_dir(start.resolve())
    for candidate in (p, *p.parents):
        if any((candidate / name).exists() for name in MANIFEST_FILES):
            return candidate
    return None


def _read_workspace_roots() -> list[Path]:
    if not CONFIG_PATH.exists():
        return []
    try:
        with open(CONFIG_PATH) as f:
            raw = json.load(f)
    except Exception:
        return []
    roots = raw.get("workspace_roots") or raw.get("watched_paths") or []
    return [Path(p).expanduser().resolve() for p in roots if p]


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _workspace_project(path: Path, roots: list[Path]) -> tuple[Path, Path] | None:
    resolved = path.resolve()
    for root in roots:
        if not _inside(resolved, root):
            continue
        rel = resolved.relative_to(root)
        if not rel.parts:
            return root, root
        return root / rel.parts[0], root
    return None


def _recent_event_project(store: Store | None) -> str | None:
    if store is None:
        return None
    row = store._conn.execute(
        "SELECT project FROM events WHERE project IS NOT NULL "
        "ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    return row["project"] if row else None


def _resolution(path: Path, source: str, confidence: str,
                workspace_root: Path | None = None) -> ProjectResolution:
    resolved = _as_dir(path).expanduser().resolve()
    return ProjectResolution(
        path=str(resolved),
        name=resolved.name,
        source=source,
        confidence=confidence,
        workspace_root=str(workspace_root) if workspace_root else None,
    )


def resolve_project(
    explicit_project: str | None = None,
    *,
    cwd: str | None = None,
    store: Store | None = None,
) -> ProjectResolution | None:
    """Resolve a project from explicit path, cwd, git/manifest roots, or recent use."""
    roots = _read_workspace_roots()

    if explicit_project:
        explicit = Path(explicit_project).expanduser()
        root = _nearest_with_child(explicit, ".git") or _nearest_manifest(explicit) or explicit
        workspace = next((r for r in roots if _inside(root, r)), None)
        return _resolution(root, "explicit", "high", workspace)

    current = Path(cwd or Path.cwd()).expanduser().resolve()
    git_root = _nearest_with_child(current, ".git")
    if git_root:
        workspace = next((r for r in roots if _inside(git_root, r)), None)
        return _resolution(git_root, "git", "high", workspace)

    manifest_root = _nearest_manifest(current)
    if manifest_root:
        workspace = next((r for r in roots if _inside(manifest_root, r)), None)
        return _resolution(manifest_root, "manifest", "medium", workspace)

    workspace_match = _workspace_project(current, roots)
    if workspace_match:
        project, workspace = workspace_match
        return _resolution(project, "workspace", "medium", workspace)

    recent = _recent_event_project(store)
    if recent:
        return _resolution(Path(recent), "recent_activity", "low")

    if current.exists():
        return _resolution(current, "cwd", "low")

    return None
