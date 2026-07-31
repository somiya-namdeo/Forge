from ai_engine.reasoning.llm_engine import LLMEngine
from ai_engine.reasoning.prompts import recommendation_prompt


class RecommendationEngine:
    def __init__(self):
        self.llm = LLMEngine()

    def recommend(
        self,
        requirements: str,
        architecture: str,
        tradeoffs: str,
    ) -> str:

        prompt = recommendation_prompt(
            requirements=requirements,
            architecture=architecture,
            tradeoffs=tradeoffs,
        )

        return self.llm.generate(prompt)