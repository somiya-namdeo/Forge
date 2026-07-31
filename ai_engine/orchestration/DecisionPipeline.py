from typing import Any, Dict

from ai_engine.reasoning.decision_engine import DecisionEngine


class DecisionPipeline:
    """Orchestration pipeline delegating architectural decisions to the DecisionEngine."""

    def __init__(self, decision_engine: DecisionEngine) -> None:
        """Initialize DecisionPipeline with a DecisionEngine instance."""
        self.decision_engine = decision_engine

    def run(self, requirements: str, context: str) -> Dict[str, Any]:
        """Execute decision pipeline and return structured decision dict.

        Args:
            requirements (str): User system requirements.
            context (str): Retrieved context information.

        Returns:
            Dict[str, Any]: Structured decision result from DecisionEngine.
        """
        return self.decision_engine.decide(requirements, context)