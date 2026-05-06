"""
Local LLM client — Ollama via HTTP.

Never blocks the CLI: check_timeout is short (2s), generation has
a configurable timeout that callers set based on urgency.

All callers must handle None return — Ollama may not be running.
"""
import json
from typing import Optional

import httpx

_CHECK_TIMEOUT = 2.0    # health-check timeout
_DEFAULT_TIMEOUT = 60.0  # generation timeout


def is_available(base_url: str = "http://localhost:11434") -> bool:
    """True if Ollama is reachable right now."""
    try:
        r = httpx.get(f"{base_url}/api/tags", timeout=_CHECK_TIMEOUT)
        return r.status_code == 200
    except Exception:
        return False


def list_models(base_url: str = "http://localhost:11434") -> list[str]:
    """Return names of locally available models. Empty list if unavailable."""
    try:
        r = httpx.get(f"{base_url}/api/tags", timeout=_CHECK_TIMEOUT)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return []


def generate(
    prompt: str,
    *,
    model: str = "llama3.2:3b",
    system: Optional[str] = None,
    base_url: str = "http://localhost:11434",
    timeout: float = _DEFAULT_TIMEOUT,
) -> Optional[str]:
    """
    Single-turn generation. Returns None if Ollama is unavailable or times out.

    Never raises — callers rely on None to detect failure.
    """
    payload: dict = {"model": model, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system
    try:
        r = httpx.post(f"{base_url}/api/generate", json=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("response", "").strip() or None
    except Exception:
        pass
    return None


def chat(
    messages: list[dict],
    *,
    model: str = "llama3.2:3b",
    base_url: str = "http://localhost:11434",
    timeout: float = _DEFAULT_TIMEOUT,
) -> Optional[str]:
    """
    Multi-turn chat. messages: [{"role": "user"|"assistant"|"system", "content": "..."}]
    Returns None if unavailable.
    """
    payload: dict = {"model": model, "messages": messages, "stream": False}
    try:
        r = httpx.post(f"{base_url}/api/chat", json=payload, timeout=timeout)
        if r.status_code == 200:
            return r.json().get("message", {}).get("content", "").strip() or None
    except Exception:
        pass
    return None


def pull(model: str, base_url: str = "http://localhost:11434") -> bool:
    """
    Pull a model. Streaming — prints progress dots. Returns True on success.
    Intended for CLI use only (can take minutes).
    """
    try:
        with httpx.stream(
            "POST", f"{base_url}/api/pull",
            json={"name": model}, timeout=600
        ) as r:
            for line in r.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                status = data.get("status", "")
                if "error" in data:
                    return False
                if status == "success":
                    return True
            return True
    except Exception:
        return False
