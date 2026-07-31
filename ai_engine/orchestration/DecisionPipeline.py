from ai_engine.reasoning.decision_engine import DecisionEngine


class DecisionPipeline:
    def __init__(self, decision_engine: DecisionEngine):
        self.decision_engine = decision_engine

    def run(self, requirements: str, context: str) -> str:
        return self.decision_engine.decide(requirements, context)