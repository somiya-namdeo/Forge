"""Knowledge retriever for the AI Architecture Recommendation Engine."""

from typing import Any

from app.retriever.qdrant_retriever import QdrantRetriever
from app.schemas.decision import DecisionRequest


class KnowledgeRetriever:
    """High-level knowledge retrieval interface.

    Delegates semantic retrieval to the Qdrant-backed retriever.
    """

    def __init__(self) -> None:
        """Initialize the semantic knowledge retriever."""
        self._retriever = QdrantRetriever()

    def refresh_cache(self) -> None:
        """Compatibility method retained for backward compatibility.

        Semantic retrieval is performed directly from Qdrant, so no
        in-memory cache needs to be refreshed.
        """
        return

    def retrieve(
        self,
        request: DecisionRequest,
    ) -> dict[str, list[dict[str, Any]]]:
        """Retrieve relevant knowledge for a decision request.

        Args:
            request: Decision request.

        Returns:
            Knowledge grouped by category.
        """
        return self._retriever.retrieve(request)