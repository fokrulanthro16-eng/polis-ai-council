"""The interface every LLM backend must implement.

Keeping this to one method is deliberate: everything provider-specific
(SDK client construction, message formatting, model selection) is
hidden behind ``complete``, so services/llm_reasoning.py never needs to
know which provider is actually configured.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """A minimal chat-completion interface: one system prompt, one user
    prompt, one text response."""

    @abstractmethod
    def complete(self, system_prompt: str, user_prompt: str) -> str:
        """Return the model's raw text response for one agent turn."""
