"""Google Gemini provider.

Requires the optional ``google-generativeai`` package -- see
backend/requirements-llm.txt. Not imported unless
POLIS_LLM_PROVIDER=gemini is set (see services/llm_providers/factory.py),
so it never affects users who don't install it.
"""

from __future__ import annotations

from app.config import settings
from app.services.llm_providers.base import LLMProvider


class GeminiProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set")

        import google.generativeai as genai  # optional dependency; see requirements-llm.txt

        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._genai = genai
        self._model_name = settings.GEMINI_MODEL

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        # system_instruction varies per agent, so the model wrapper is built
        # per call; this constructs a lightweight client-side object only,
        # it does not make a network call by itself.
        model = self._genai.GenerativeModel(
            self._model_name, system_instruction=system_prompt
        )
        response = model.generate_content(user_prompt)
        return response.text
