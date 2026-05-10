"""
Cloud LLM client — Anthropic Claude.

Used ONLY when:
  - User explicitly requests it (stareha talk)
  - allow_cloud=True is passed to the router AND no local option succeeded
  - Context sent is ALWAYS summaries only — never raw events or file contents

Privacy guarantee: callers are responsible for sending only processed summaries.
"""
import json
import os
import time
from pathlib import Path
from typing import Optional

_CLAUDE_CODE_CREDENTIALS = Path.home() / ".claude" / ".credentials.json"


def _oauth_token() -> Optional[str]:
    """Return a valid Claude Code OAuth access token if available and not expired."""
    if not _CLAUDE_CODE_CREDENTIALS.exists():
        return None
    try:
        data = json.loads(_CLAUDE_CODE_CREDENTIALS.read_text())
        oauth = data.get("claudeAiOauth", {})
        token = oauth.get("accessToken")
        expires_at_ms = oauth.get("expiresAt", 0)
        # expiresAt is in milliseconds; keep 120s buffer
        if token and expires_at_ms > time.time() * 1000 + 120_000:
            return token
        return None
    except Exception:
        return None


def _api_key() -> str:
    """Return Anthropic API key from env var or config file."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    try:
        from packages.core.config import load_config
        cfg = load_config()
        # New multi-provider structure
        anthropic_cfg = cfg.llm_providers.get("anthropic", {})
        if anthropic_cfg.get("api_key"):
            return anthropic_cfg["api_key"]
        # Legacy fallback
        return cfg.cloud_llm_api_key or ""
    except Exception:
        return ""


def _get_client():
    """Return an authenticated Anthropic client — OAuth preferred, API key fallback."""
    try:
        import anthropic
        token = _oauth_token()
        if token:
            return anthropic.Anthropic(auth_token=token)
        key = _api_key()
        if key:
            return anthropic.Anthropic(api_key=key)
    except Exception:
        pass
    return None


def is_available() -> bool:
    """True if any credential (OAuth token or API key) is present and valid."""
    return bool(_oauth_token()) or bool(_api_key())


def generate(
    prompt: str,
    *,
    model: str = "claude-haiku-4-5-20251001",
    system: Optional[str] = None,
    max_tokens: int = 1500,
) -> Optional[str]:
    """
    Single-turn generation via Anthropic Claude.
    Returns None if unavailable or on error.
    """
    client = _get_client()
    if not client:
        return None
    try:
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        return resp.content[0].text.strip() or None
    except Exception:
        return None


def chat(
    messages: list[dict],
    *,
    model: str = "claude-haiku-4-5-20251001",
    system: Optional[str] = None,
    max_tokens: int = 2000,
) -> Optional[str]:
    """
    Multi-turn chat. messages: [{"role": "user"|"assistant", "content": "..."}]
    Returns None if unavailable.
    """
    client = _get_client()
    if not client:
        return None
    try:
        kwargs: dict = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
        return resp.content[0].text.strip() or None
    except Exception:
        return None
