from ai_engine.reasoning.llm_engine import LLMEngine
from ai_engine.reasoning.prompts import reasoning_prompt


class ReasoningEngine:
    def __init__(self):
        self.llm = LLMEngine()

    def reason(self, query: str, context: str) -> str:
        prompt = reasoning_prompt(query, context)
        response = self.llm.generate(prompt)

        return response