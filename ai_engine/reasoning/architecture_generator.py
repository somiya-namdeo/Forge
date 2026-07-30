from ai_engine.reasoning.llm_engine import LLMEngine
from ai_engine.reasoning.prompts import architecture_prompt

class ArchitectureGenerator:
    def __init__(self):
        self.llm = LLMEngine()

    def generate(self, requirements: str, context: str) -> str:
        prompt = architecture_prompt(requirements, context)
        response = self.llm.generate(prompt)

        return response