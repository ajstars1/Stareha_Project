from dataclasses import dataclass
from pathlib import Path
import json

CONFIG_PATH = Path.home() / ".stareha" / "config.json"

DEFAULTS = {
    "db_path": "~/.stareha/db.sqlite",
    "permissions_path": "~/.stareha/permissions.json",
    "log_path": "~/.stareha/logs",
    "daemon_port": 7431,
    "browser_port": 7432,
    "watched_paths": [],
    "idle_threshold_seconds": 1800,
    "cloud_llm_model": "claude-sonnet-4-6",
    "local_llm_model": "llama3.2:3b",
    "local_llm_base_url": "http://localhost:11434",
}


@dataclass
class Config:
    db_path: Path
    permissions_path: Path
    log_path: Path
    daemon_port: int
    browser_port: int
    watched_paths: list[str]
    idle_threshold_seconds: int
    cloud_llm_model: str
    local_llm_model: str
    local_llm_base_url: str


def load_config() -> Config:
    raw = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            raw.update(json.load(f))
    return Config(
        db_path=Path(raw["db_path"]).expanduser(),
        permissions_path=Path(raw["permissions_path"]).expanduser(),
        log_path=Path(raw["log_path"]).expanduser(),
        daemon_port=int(raw["daemon_port"]),
        browser_port=int(raw["browser_port"]),
        watched_paths=raw["watched_paths"],
        idle_threshold_seconds=int(raw["idle_threshold_seconds"]),
        cloud_llm_model=raw["cloud_llm_model"],
        local_llm_model=raw["local_llm_model"],
        local_llm_base_url=raw["local_llm_base_url"],
    )


def save_config(updates: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            raw.update(json.load(f))
    raw.update(updates)
    with open(CONFIG_PATH, "w") as f:
        json.dump(raw, f, indent=2)


def ensure_dirs() -> None:
    config = load_config()
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    config.log_path.mkdir(parents=True, exist_ok=True)
