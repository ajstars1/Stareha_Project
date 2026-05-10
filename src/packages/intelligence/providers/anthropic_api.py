"""
Anthropic API key provider.
Uses ANTHROPIC_API_KEY env var or provider_configs.anthropic.api_key from config.
"""
import os
from typing import Optional


class AnthropicApiProvider:
    PROVIDER_ID = "anthropic"

    def _api_key(self) -> str:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if key:
            return key
        try:
            from packages.core.config import load_config
            cfg = load_config()
            return (
                cfg.provider_configs.get("anthropic", {}).get("api_key", "")
                or getattr(cfg, "cloud_llm_api_key", "")
                or ""
            )
        except Exception:
            return ""

    def get_configured_model(self) -> str:
        try:
            from packages.core.config import load_config
            return (
                load_config()
                .provider_configs.get("anthropic", {})
                .get("model", "claude-haiku-4-5-20251001")
            )
        except Exception:
            return "claude-haiku-4-5-20251001"

    def is_available(self) -> bool:
        return bool(self._api_key())

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 1500,
    ) -> Optional[str]:
        api_key = self._api_key()
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
        self,
        messages: list[dict],
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 2000,
    ) -> Optional[str]:
        api_key = self._api_key()
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
