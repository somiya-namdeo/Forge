"""
Decision service module bridging FastAPI routes with the AI reasoning engine.
"""

from ai_engine.orchestration.DecisionPipeline import DecisionPipeline
from ai_engine.reasoning.decision_engine import DecisionEngine
from ai_engine.retrieval.retriever import Retriever
from app.schemas.request import DecisionRequest
from app.schemas.response import DecisionResponse


class DecisionService:
    """Orchestration service bridging API requests with AI retrieval and reasoning."""

    # TODO:
    # Replace direct class instantiation with dependency injection
    # if the project grows to support multiple implementations.
    def __init__(self) -> None:
        """Initialize AI engine components."""
        self.retriever = Retriever()
        self.decision_engine = DecisionEngine()
        self.pipeline = DecisionPipeline(self.decision_engine)

    def generate_decision(self, request: DecisionRequest) -> DecisionResponse:
        """Generate architectural decision and recommendation from project requirements.

        Args:
            request (DecisionRequest): Input payload containing project_description.

        Returns:
            DecisionResponse: Structured architecture, tradeoffs, recommendation, and confidence.

        Raises:
            RuntimeError: If an error occurs during retrieval or pipeline execution.
        """
        try:
            query = request.project_description.strip()
            if not query:
                raise ValueError("Project description cannot be empty.")

            # 1. High-level natural language retrieval
            context = self.retriever.retrieve(query)

            # 2. High-level pipeline execution returning structured result dict
            result = self.pipeline.run(query, context)

            # 3. Convert structured result into DecisionResponse
            return DecisionResponse(
                architecture=result.get("architecture", ""),
                tradeoffs=result.get("tradeoffs", ""),
                recommendation=result.get("recommendation", ""),
                confidence=result.get("confidence", 1.0),
            )
        except Exception as exc:
            raise RuntimeError(
                "Failed to generate architectural decision."
            ) from exc
