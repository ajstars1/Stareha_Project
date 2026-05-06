"""
Intelligence policy router — Stage 5.

Single entry point for all LLM tasks. Enforces the three-layer policy:

  Layer 1: Scripts  — handled by callers before reaching here
  Layer 2: Local LLM (Ollama) — private, free, preferred
  Layer 3: Cloud LLM (Claude) — only when allow_cloud=True and local failed

Usage:
    result, layer = router.generate(prompt, system=system, allow_cloud=True)
    if result is None:
        # All layers unavailable — use fallback / scripts output
"""
from typing import Literal, Optional

from packages.core.config import load_config
from packages.intelligence import local_llm, cloud_llm

Layer = Literal["local_llm", "cloud_llm", "none"]


def generate(
    prompt: str,
    *,
    system: Optional[str] = None,
    allow_cloud: bool = False,
    local_model: Optional[str] = None,
    cloud_model: Optional[str] = None,
    timeout: float = 60.0,
) -> tuple[Optional[str], Layer]:
    """
    Run a generation task through the intelligence policy.

    Returns (result, layer_used):
      - layer_used is "local_llm", "cloud_llm", or "none"
      - result is None when all available layers fail

    Privacy contract:
      - prompt must contain only summaries / processed data
      - never pass raw events, file contents, or secrets
    """
    config = load_config()

    # Layer 2: Local LLM
    lmodel = local_model or config.local_llm_model
    base_url = config.local_llm_base_url

    if local_llm.is_available(base_url):
        result = local_llm.generate(
            prompt, model=lmodel, system=system,
            base_url=base_url, timeout=timeout,
        )
        if result:
            return result, "local_llm"

    # Layer 3: Cloud LLM (explicit opt-in only)
    if allow_cloud and cloud_llm.is_available():
        cmodel = cloud_model or "claude-haiku-4-5-20251001"
        result = cloud_llm.generate(prompt, model=cmodel, system=system)
        if result:
            return result, "cloud_llm"

    return None, "none"


def chat(
    messages: list[dict],
    *,
    system: Optional[str] = None,
    allow_cloud: bool = False,
    local_model: Optional[str] = None,
    cloud_model: Optional[str] = None,
    timeout: float = 120.0,
) -> tuple[Optional[str], Layer]:
    """
    Multi-turn chat through the policy.
    Same fallback behaviour as generate().
    """
    config = load_config()

    lmodel = local_model or config.local_llm_model
    base_url = config.local_llm_base_url

    if local_llm.is_available(base_url):
        full_messages = messages
        if system:
            full_messages = [{"role": "system", "content": system}] + messages
        result = local_llm.chat(full_messages, model=lmodel,
                                base_url=base_url, timeout=timeout)
        if result:
            return result, "local_llm"

    if allow_cloud and cloud_llm.is_available():
        cmodel = cloud_model or "claude-haiku-4-5-20251001"
        result = cloud_llm.chat(messages, model=cmodel, system=system)
        if result:
            return result, "cloud_llm"

    return None, "none"


def status() -> dict:
    """
    Return the current availability of each intelligence layer.
    Used by `stareha status` and `stareha local-llm status`.
    """
    config = load_config()
    base_url = config.local_llm_base_url

    local_ok = local_llm.is_available(base_url)
    models = local_llm.list_models(base_url) if local_ok else []
    cloud_ok = cloud_llm.is_available()

    return {
        "local_llm": {
            "available": local_ok,
            "base_url": base_url,
            "models": models,
            "configured_model": config.local_llm_model,
        },
        "cloud_llm": {
            "available": cloud_ok,
            "configured_model": config.cloud_llm_model,
        },
    }
