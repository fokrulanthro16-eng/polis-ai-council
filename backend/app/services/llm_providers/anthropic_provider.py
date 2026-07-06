"""Anthropic (Claude) provider.

Requires the optional ``anthropic`` package -- see
backend/requirements-llm.txt. Not imported unless
POLIS_LLM_PROVIDER=anthropic is set (see services/llm_providers/factory.py),
so it never affects users who don't install it.
"""

from __future__ import annotations

from app.config import settings
from app.services.llm_providers.base import LLMProvider

_MAX_TOKENS = 512


class AnthropicProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.ANTHROPIC_API_KEY:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")

        import anthropic  # optional dependency; see requirements-llm.txt

        self._client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self._model = settings.ANTHROPIC_MODEL

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text
