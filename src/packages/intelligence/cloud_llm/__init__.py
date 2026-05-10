"""
Cloud LLM dispatcher — delegates to the configured provider.

Supported providers: claude_code_oauth, anthropic, openai, groq, gemini, openai_compat.
Active provider is set via `cloud_provider` in ~/.stareha/config.json.

Privacy guarantee: callers must send only summaries, never raw events or file contents.
"""
import os
from typing import Optional

_DEFAULT_MODEL = "claude-haiku-4-5-20251001"


def _api_key() -> str:
    """Backward-compat: return Anthropic API key from env or config."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    try:
        from packages.core.config import load_config
        cfg = load_config()
        return (
            cfg.provider_configs.get("anthropic", {}).get("api_key", "")
            or cfg.cloud_llm_api_key
            or ""
        )
    except Exception:
        return ""


def _get_active_provider():
    """Return the active provider instance, or None."""
    try:
        from packages.core.config import load_config
        from packages.intelligence.providers import get_provider
        cfg = load_config()
        return get_provider(cfg.cloud_provider)
    except Exception:
        return None


def is_available() -> bool:
    """True if the active cloud provider has credentials configured."""
    provider = _get_active_provider()
    return provider is not None and provider.is_available()


def generate(
    prompt: str,
    *,
    model: str = _DEFAULT_MODEL,
    system: Optional[str] = None,
    max_tokens: int = 1500,
) -> Optional[str]:
    """
    Single-turn generation via the active provider.
    Returns None if unavailable or on error.
    """
    provider = _get_active_provider()
    if not provider or not provider.is_available():
        return None
    actual_model = model if model != _DEFAULT_MODEL else provider.get_configured_model()
    return provider.generate(prompt, model=actual_model, system=system, max_tokens=max_tokens)


def chat(
    messages: list[dict],
    *,
    model: str = _DEFAULT_MODEL,
    system: Optional[str] = None,
    max_tokens: int = 2000,
) -> Optional[str]:
    """
    Multi-turn chat. messages: [{"role": "user"|"assistant", "content": "..."}]
    Returns None if unavailable.
    """
    provider = _get_active_provider()
    if not provider or not provider.is_available():
        return None
    actual_model = model if model != _DEFAULT_MODEL else provider.get_configured_model()
    return provider.chat(messages, model=actual_model, system=system, max_tokens=max_tokens)
