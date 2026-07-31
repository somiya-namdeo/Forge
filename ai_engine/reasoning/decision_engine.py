from ai_engine.reasoning.llm_engine import LLMEngine
from ai_engine.reasoning.prompts import decision_prompt


class DecisionEngine:
    def __init__(self):
        self.llm = LLMEngine()

    def decide(self, requirements: str, context: str) -> str:
        prompt = decision_prompt(requirements, context)
        return self.llm.generate(prompt)