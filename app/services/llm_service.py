"""Centralized LLM service for Forge."""

from langchain_openai import ChatOpenAI

from app.core.config import DECISION_API_KEY, DECISION_MODEL, LLM_MAX_TOKENS


class LLMService:
    """Reusable LLM wrapper used across Forge Decision Module (Groq)."""

    def __init__(self) -> None:
        self._llm = ChatOpenAI(
            model=DECISION_MODEL,
            api_key=DECISION_API_KEY,
            base_url="https://api.groq.com/openai/v1",
            temperature=0.2,
            max_tokens=LLM_MAX_TOKENS,
            max_retries=0,
            request_timeout=10.0,
        )

    def generate(self, prompt: str, json_mode: bool = False) -> str:
        """Generate a text response from the LLM."""
        kwargs = {}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        response = self._llm.invoke(prompt, **kwargs)
        return response.content.strip()

    def reason(self, prompt: str, json_mode: bool = False) -> str:
        """Generate reasoning response."""
        return self.generate(prompt, json_mode=json_mode)

    def summarize(self, prompt: str) -> str:
        """Generate summary response."""
        return self.generate(prompt)