"""
Google Gemini provider.

Uses google-generativeai SDK if installed; falls back to Gemini REST API via httpx.
Key from GEMINI_API_KEY env var or provider_configs.gemini.api_key in config.
"""
import os
from typing import Optional


class GeminiProvider:
    PROVIDER_ID = "gemini"

    def _api_key(self) -> str:
        key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("GOOGLE_API_KEY", "")
        if key:
            return key
        try:
            from packages.core.config import load_config
            return load_config().provider_configs.get("gemini", {}).get("api_key", "")  # type: ignore[attr-defined]
        except Exception:
            return ""

    def get_configured_model(self) -> str:
        try:
            from packages.core.config import load_config
            return load_config().provider_configs.get("gemini", {}).get("model", "gemini-1.5-flash")  # type: ignore[attr-defined]
        except Exception:
            return "gemini-1.5-flash"

    def is_available(self) -> bool:
        return bool(self._api_key())

    def _messages_to_gemini(
        self,
        messages: list[dict],
        system: Optional[str],
    ) -> tuple[Optional[str], list[dict]]:
        """Convert OpenAI-style messages to Gemini format. Returns (system_instruction, contents)."""
        sys_parts: list[str] = []
        if system:
            sys_parts.append(system)

        contents: list[dict] = []
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "system":
                sys_parts.append(content)
            elif role == "user":
                contents.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                contents.append({"role": "model", "parts": [{"text": content}]})

        sys_instruction = "\n".join(sys_parts) if sys_parts else None
        return sys_instruction, contents

    def _call_sdk(
        self,
        contents: list[dict],
        *,
        model: str,
        system: Optional[str],
        max_tokens: int,
    ) -> Optional[str]:
        """Use google-generativeai SDK."""
        try:
            import google.generativeai as genai  # type: ignore[import]
            genai.configure(api_key=self._api_key())
            gen_model = genai.GenerativeModel(
                model_name=model,
                system_instruction=system or None,
            )
            response = gen_model.generate_content(
                contents,
                generation_config={"max_output_tokens": max_tokens},
            )
            return response.text or None
        except ImportError:
            return None
        except Exception:
            return None

    def _call_rest(
        self,
        contents: list[dict],
        *,
        model: str,
        system: Optional[str],
        max_tokens: int,
    ) -> Optional[str]:
        """Use Gemini REST API via httpx."""
        try:
            import httpx
            api_key = self._api_key()
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            body: dict = {
                "contents": contents,
                "generationConfig": {"maxOutputTokens": max_tokens},
            }
            if system:
                body["systemInstruction"] = {"parts": [{"text": system}]}
            resp = httpx.post(url, json=body, timeout=60.0)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"] or None
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
        if not self._api_key():
            return None
        sys_inst, contents = self._messages_to_gemini([{"role": "user", "content": prompt}], system)
        result = self._call_sdk(contents, model=model, system=sys_inst, max_tokens=max_tokens)
        if result is None:
            result = self._call_rest(contents, model=model, system=sys_inst, max_tokens=max_tokens)
        return result

    def chat(
        self,
        messages: list[dict],
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 2000,
    ) -> Optional[str]:
        if not self._api_key():
            return None
        sys_inst, contents = self._messages_to_gemini(messages, system)
        result = self._call_sdk(contents, model=model, system=sys_inst, max_tokens=max_tokens)
        if result is None:
            result = self._call_rest(contents, model=model, system=sys_inst, max_tokens=max_tokens)
        return result
