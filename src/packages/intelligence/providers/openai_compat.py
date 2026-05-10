"""
OpenAI-compatible provider -- handles OpenAI, Groq, and custom endpoints.

All three use identical API structure (/v1/chat/completions) with an Authorization
Bearer token. The provider_id passed to __init__ selects which config sub-dict
and base URL to use.
"""
import os
from typing import Optional


_ENDPOINTS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "groq":   "https://api.groq.com/openai/v1",
}

_ENV_VARS: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "groq":   "GROQ_API_KEY",
    "openai_compat": "OPENAI_COMPAT_API_KEY",
}

_DEFAULT_MODELS: dict[str, str] = {
    "openai": "gpt-4o-mini",
    "groq":   "llama3-8b-8192",
    "openai_compat": "",
}

_VALID_PROVIDER_IDS = frozenset({"openai", "groq", "openai_compat"})


class OpenAICompatProvider:
    def __init__(self, provider_id: str) -> None:
        if provider_id not in _VALID_PROVIDER_IDS:
            raise ValueError(f"provider_id must be one of {sorted(_VALID_PROVIDER_IDS)}, got {provider_id!r}")
        self.PROVIDER_ID: str = provider_id

    def _get_credentials(self) -> tuple[str, str]:
        """Return (api_key, base_url). Empty strings if not configured."""
        env_var = _ENV_VARS.get(self.PROVIDER_ID, "")
        api_key = os.environ.get(env_var, "")

        if not api_key:
            try:
                from packages.core.config import load_config
                pconf = load_config().provider_configs.get(self.PROVIDER_ID, {})  # type: ignore[attr-defined]
                api_key = pconf.get("api_key", "")
            except Exception:
                pass

        if self.PROVIDER_ID == "openai_compat":
            base_url = ""
            try:
                from packages.core.config import load_config
                base_url = load_config().provider_configs.get("openai_compat", {}).get("base_url", "")  # type: ignore[attr-defined]
            except Exception:
                pass
        else:
            base_url = _ENDPOINTS[self.PROVIDER_ID]

        return api_key, base_url

    def get_configured_model(self) -> str:
        try:
            from packages.core.config import load_config
            pconf = load_config().provider_configs.get(self.PROVIDER_ID, {})  # type: ignore[attr-defined]
            return pconf.get("model", "") or _DEFAULT_MODELS.get(self.PROVIDER_ID, "")
        except Exception:
            return _DEFAULT_MODELS.get(self.PROVIDER_ID, "")

    def is_available(self) -> bool:
        api_key, base_url = self._get_credentials()
        if not api_key:
            return False
        if self.PROVIDER_ID == "openai_compat" and not base_url:
            return False
        return True

    def _call_api(self, messages: list[dict], *, model: str, max_tokens: int) -> Optional[str]:
        """Make a /chat/completions call. Uses openai SDK if available, else httpx."""
        api_key, base_url = self._get_credentials()
        if not api_key or (self.PROVIDER_ID == "openai_compat" and not base_url):
            return None

        try:
            import openai
            client = openai.OpenAI(api_key=api_key, base_url=base_url or None)
            resp = client.chat.completions.create(
                model=model, messages=messages, max_tokens=max_tokens  # type: ignore[arg-type]
            )
            return resp.choices[0].message.content or None
        except ImportError:
            pass
        except Exception:
            return None

        try:
            import httpx
            url = f"{base_url}/chat/completions"
            resp = httpx.post(
                url,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": messages, "max_tokens": max_tokens},
                timeout=60.0,
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"] or None
        except Exception:
            return None

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 1500,
    ) -> Optional[str]:
        messages: list[dict] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self._call_api(messages, model=model, max_tokens=max_tokens)

    def chat(
        self,
        messages: list[dict],
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 2000,
    ) -> Optional[str]:
        full_messages = messages
        if system:
            full_messages = [{"role": "system", "content": system}] + messages
        return self._call_api(full_messages, model=model, max_tokens=max_tokens)
