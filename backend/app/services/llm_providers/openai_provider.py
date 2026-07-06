"""OpenAI provider.

Requires the optional ``openai`` package -- see
backend/requirements-llm.txt. Not imported unless
POLIS_LLM_PROVIDER=openai is set (see services/llm_providers/factory.py),
so it never affects users who don't install it.
"""

from __future__ import annotations

from app.config import settings
from app.services.llm_providers.base import LLMProvider


class OpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set")

        import openai  # optional dependency; see requirements-llm.txt

        self._client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self._model = settings.OPENAI_MODEL

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""
