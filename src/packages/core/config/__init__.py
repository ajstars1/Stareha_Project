from dataclasses import dataclass, field
from pathlib import Path
import json

CONFIG_PATH = Path.home() / ".stareha" / "config.json"

_DEFAULT_PROVIDER_CONFIGS: dict[str, dict] = {
    "anthropic":         {"api_key": "", "model": "claude-haiku-4-5-20251001"},
    "claude_code_oauth": {"access_token": "", "refresh_token": "", "expires_at": 0, "model": "claude-sonnet-4-6"},
    "openai":            {"api_key": "", "model": "gpt-4o-mini"},
    "groq":              {"api_key": "", "model": "llama3-8b-8192"},
    "gemini":            {"api_key": "", "model": "gemini-1.5-flash"},
    "openai_compat":     {"api_key": "", "base_url": "", "model": ""},
}

DEFAULTS: dict = {
    "db_path": "~/.stareha/db.sqlite",
    "permissions_path": "~/.stareha/permissions.json",
    "log_path": "~/.stareha/logs",
    "daemon_port": 7431,
    "browser_port": 7432,
    "watched_paths": [],
    "idle_threshold_seconds": 1800,
    "cloud_llm_model": "claude-sonnet-4-6",
    "cloud_llm_api_key": "",
    "local_llm_model": "llama3.2:3b",
    "local_llm_base_url": "http://localhost:11434",
    "cloud_provider": "anthropic",
    "provider_configs": _DEFAULT_PROVIDER_CONFIGS,
}


def _merge_provider_configs(stored: dict) -> dict:
    """Deep-merge stored provider_configs with defaults.

    New providers added in future code updates are preserved even if absent
    from the stored config file.
    """
    merged: dict[str, dict] = {}
    for pid, defaults in _DEFAULT_PROVIDER_CONFIGS.items():
        merged[pid] = dict(defaults)
        if pid in stored:
            merged[pid].update(stored[pid])
    # Preserve any extra providers the user added manually.
    for pid, pconf in stored.items():
        if pid not in merged:
            merged[pid] = dict(pconf)
    return merged


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
    cloud_llm_api_key: str
    local_llm_model: str
    local_llm_base_url: str
    cloud_provider: str
    provider_configs: dict = field(default_factory=dict)


def load_config() -> Config:
    raw: dict = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            raw.update(json.load(f))

    provider_configs = _merge_provider_configs(raw.get("provider_configs", {}))

    # Backward-compat: migrate old top-level api key into anthropic provider config.
    old_key = raw.get("cloud_llm_api_key", "")
    if old_key and not provider_configs["anthropic"].get("api_key"):
        provider_configs["anthropic"]["api_key"] = old_key

    return Config(
        db_path=Path(raw["db_path"]).expanduser(),
        permissions_path=Path(raw["permissions_path"]).expanduser(),
        log_path=Path(raw["log_path"]).expanduser(),
        daemon_port=int(raw["daemon_port"]),
        browser_port=int(raw["browser_port"]),
        watched_paths=raw["watched_paths"],
        idle_threshold_seconds=int(raw["idle_threshold_seconds"]),
        cloud_llm_model=raw["cloud_llm_model"],
        cloud_llm_api_key=raw.get("cloud_llm_api_key", ""),
        local_llm_model=raw["local_llm_model"],
        local_llm_base_url=raw["local_llm_base_url"],
        cloud_provider=raw.get("cloud_provider", "anthropic"),
        provider_configs=provider_configs,
    )


def save_config(updates: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    raw: dict = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            raw.update(json.load(f))

    # Deep-merge provider_configs so a single-provider update doesn't wipe others.
    if "provider_configs" in updates:
        existing_pc: dict = raw.get("provider_configs", {})
        incoming_pc: dict = updates.pop("provider_configs")
        for pid, pconf in incoming_pc.items():
            existing_pc.setdefault(pid, {}).update(pconf)
        raw["provider_configs"] = existing_pc

    raw.update(updates)
    with open(CONFIG_PATH, "w") as f:
        json.dump(raw, f, indent=2)


def ensure_dirs() -> None:
    config = load_config()
    config.db_path.parent.mkdir(parents=True, exist_ok=True)
    config.log_path.mkdir(parents=True, exist_ok=True)
