"""Resolves which LLM provider to use, based on POLIS_LLM_PROVIDER.

Returns ``None`` if no provider is configured, the selected provider's
package isn't installed, or its API key is missing -- callers (see
services/llm_reasoning.py and agents/base.py) treat ``None`` as "fall
back to the mock reasoning engine." This is the single seam that keeps
provider selection graceful: nothing here ever raises.
"""

from __future__ import annotations

import logging
from functools import lru_cache

from app.config import settings
from app.services.llm_providers.base import LLMProvider

_logger = logging.getLogger("polis.llm_providers")

_SUPPORTED_PROVIDERS = ("anthropic", "openai", "gemini")


def _build(name: str) -> LLMProvider:
    """Construct the named provider. Imports are local so an unused
    provider's SDK never needs to be installed (see requirements-llm.txt)."""
    if name == "anthropic":
        from app.services.llm_providers.anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    if name == "openai":
        from app.services.llm_providers.openai_provider import OpenAIProvider

        return OpenAIProvider()
    if name == "gemini":
        from app.services.llm_providers.gemini_provider import GeminiProvider

        return GeminiProvider()
    raise ValueError(f"Unsupported provider '{name}'")


@lru_cache(maxsize=1)
def get_provider() -> LLMProvider | None:
    """Build and cache the configured LLM provider, or None if unavailable.

    Cached because provider construction (SDK client setup) only needs to
    happen once per process; a failed attempt is also cached so repeated
    calls don't retry a provider that's known to be misconfigured.
    """
    name = settings.LLM_PROVIDER
    if not name:
        return None

    if name not in _SUPPORTED_PROVIDERS:
        _logger.warning(
            "Unknown POLIS_LLM_PROVIDER '%s' (expected one of: %s); "
            "falling back to mock reasoning.",
            name,
            ", ".join(_SUPPORTED_PROVIDERS),
        )
        return None

    try:
        return _build(name)
    except Exception:
        _logger.warning(
            "Failed to initialize LLM provider '%s'; falling back to mock reasoning. "
            "Check that its package is installed (see requirements-llm.txt) and its "
            "API key is set.",
            name,
            exc_info=True,
        )
        return None
