from ai_engine.reasoning.llm_engine import LLMEngine
from ai_engine.reasoning.prompts import tradeoff_prompt


class TradeoffAnalyzer:
    def __init__(self):
        self.llm = LLMEngine()

    def analyze(self, question: str, context: str) -> str:
        prompt = tradeoff_prompt(question, context)
        return self.llm.generate(prompt)