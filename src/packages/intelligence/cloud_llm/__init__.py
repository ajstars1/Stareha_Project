"""
Cloud LLM client — Anthropic Claude.

Used ONLY when:
  - User explicitly requests it (stareha talk)
  - allow_cloud=True is passed to the router AND no local option succeeded
  - Context sent is ALWAYS summaries only — never raw events or file contents

Privacy guarantee: callers are responsible for sending only processed summaries.
"""
import os
from typing import Optional


def is_available() -> bool:
    """True if ANTHROPIC_API_KEY is set."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))


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
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
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
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
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
