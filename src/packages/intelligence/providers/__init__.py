"""
Multi-provider LLM registry for Stareha.

Each provider implements the Provider protocol. get_provider(id) returns
a ready-to-use instance, or None if credentials aren't configured.
"""
from typing import Optional, Protocol, runtime_checkable

PROVIDER_IDS: dict[str, str] = {
    "claude_code_oauth": "Claude Code (claude.ai subscription)",
    "anthropic":         "Anthropic API key",
    "openai":            "OpenAI",
    "groq":              "Groq",
    "gemini":            "Google Gemini",
    "openai_compat":     "Custom OpenAI-compatible endpoint",
}


@runtime_checkable
class Provider(Protocol):
    PROVIDER_ID: str

    def is_available(self) -> bool: ...
    def generate(
        self,
        prompt: str,
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 1500,
    ) -> Optional[str]: ...
    def chat(
        self,
        messages: list[dict],
        *,
        model: str,
        system: Optional[str] = None,
        max_tokens: int = 2000,
    ) -> Optional[str]: ...
    def get_configured_model(self) -> str: ...


def get_provider(provider_id: str) -> Optional["Provider"]:
    """
    Return an instantiated provider for the given ID.
    Returns None if the provider is not configured/available.
    """
    try:
        if provider_id == "claude_code_oauth":
            from packages.intelligence.providers.claude_code_oauth import ClaudeCodeOAuthProvider
            return ClaudeCodeOAuthProvider()
        elif provider_id == "anthropic":
            from packages.intelligence.providers.anthropic_api import AnthropicApiProvider
            return AnthropicApiProvider()
        elif provider_id == "openai":
            from packages.intelligence.providers.openai_compat import OpenAICompatProvider
            return OpenAICompatProvider("openai")
        elif provider_id == "groq":
            from packages.intelligence.providers.openai_compat import OpenAICompatProvider
            return OpenAICompatProvider("groq")
        elif provider_id == "gemini":
            from packages.intelligence.providers.gemini import GeminiProvider
            return GeminiProvider()
        elif provider_id == "openai_compat":
            from packages.intelligence.providers.openai_compat import OpenAICompatProvider
            return OpenAICompatProvider("openai_compat")
    except ImportError:
        pass
    return None
