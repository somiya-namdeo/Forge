"""Qdrant semantic retriever module for Forge AI engineering platform."""

from typing import Any

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from qdrant_client import QdrantClient

from app.core.config import COLLECTION_NAME, EMBEDDING_MODEL, QDRANT_PATH, TOP_K
from app.schemas.decision import DecisionRequest


class QdrantRetriever:
    """Semantic knowledge retriever backed by an existing local Qdrant collection."""

    def __init__(self, top_k: int = TOP_K) -> None:
        """Initialize QdrantRetriever with Qdrant client and embedding model singletons."""
        self.top_k = top_k

        if not QDRANT_PATH.exists():
            raise RuntimeError(f"Qdrant storage path '{QDRANT_PATH}' does not exist.")

        try:
            self._client = QdrantClient(path=str(QDRANT_PATH))
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize QdrantClient at '{QDRANT_PATH}': {exc}") from exc

        try:
            collections = [c.name for c in self._client.get_collections().collections]
        except Exception as exc:
            raise RuntimeError(f"Failed to inspect Qdrant collections at '{QDRANT_PATH}': {exc}") from exc

        if COLLECTION_NAME not in collections:
            raise ValueError(f"Collection '{COLLECTION_NAME}' does not exist in Qdrant at '{QDRANT_PATH}'.")

        try:
            self._embeddings = HuggingFaceBgeEmbeddings(model_name=EMBEDDING_MODEL)
        except Exception as exc:
            raise RuntimeError(f"Failed to load embedding model '{EMBEDDING_MODEL}': {exc}") from exc

    @staticmethod
    def _format_field_val(val: Any) -> str:
        """Format an arbitrary request field value into a clean string snippet."""
        if val is None:
            return ""
        if hasattr(val, "value"):
            return str(val.value)
        if isinstance(val, (list, tuple, set)):
            items = [str(i.value) if hasattr(i, "value") else str(i) for i in val if i]
            return ", ".join(items)
        return str(val).strip()

    def _build_search_query(self, request: DecisionRequest) -> str:
        """Construct a comprehensive semantic search query string from DecisionRequest attributes."""
        parts: list[str] = []

        fields_to_extract = (
            "project_name",
            "project_description",
            "deployment_target",
            "priority",
            "business_goal",
            "business_goals",
            "constraints",
            "functional_requirements",
            "non_functional_requirements",
            "preferred_llms",
            "preferred_llm",
            "preferred_vector_databases",
            "preferred_vector_db",
            "preferred_embedding_models",
            "preferred_embedding_model",
            "preferred_frameworks",
            "preferred_framework",
        )

        for field in fields_to_extract:
            val = getattr(request, field, None)
            formatted = self._format_field_val(val)
            if formatted:
                parts.append(f"{field.replace('_', ' ')}: {formatted}")

        query_text = " | ".join(parts)
        if not query_text.strip():
            query_text = f"{request.project_name} {request.project_description}"

        return query_text.strip()

    def retrieve(
        self,
        request: DecisionRequest,
        limit: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Retrieve relevant technology payload dictionaries from Qdrant grouped by category.

        Args:
            request (DecisionRequest): User decision request containing requirement parameters.
            limit (int | None): Optional limit on number of retrieved results. Defaults to TOP_K.

        Returns:
            dict[str, list[dict[str, Any]]]: Dictionary mapping candidate categories to lists
                of retrieved payload dictionaries.

        Raises:
            ValueError: If query embedding fails or search returns empty/invalid results.
            RuntimeError: If Qdrant communication encounters execution failures.
        """
        top_limit = limit or self.top_k

        query_text = self._build_search_query(request)
        if not query_text.strip():
            raise ValueError("Cannot execute Qdrant retrieval: constructed search query is empty.")

        try:
            query_vector = self._embeddings.embed_query(query_text)
        except Exception as exc:
            raise ValueError(f"Failed to generate embedding vector for query: {exc}") from exc

        if not query_vector:
            raise ValueError("Generated query embedding vector is empty.")

        try:
            try:
                raw_points = self._client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=query_vector,
                    limit=top_limit,
                ).points
            except Exception:
                raw_points = self._client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    limit=top_limit,
                )
        except Exception as exc:
            raise RuntimeError(
                f"Failed to execute Qdrant search against collection '{COLLECTION_NAME}': {exc}"
            ) from exc

        if not raw_points:
            raise ValueError(f"Qdrant search returned empty results for query '{query_text}'.")

        grouped_payloads: dict[str, list[dict[str, Any]]] = {}

        for point in raw_points:
            payload = getattr(point, "payload", None)
            if not payload or not isinstance(payload, dict):
                continue

            category = payload.get("category")
            if not category or not isinstance(category, str) or not category.strip():
                category = "general"
            else:
                category = category.strip().lower()

            if category not in grouped_payloads:
                grouped_payloads[category] = []

            grouped_payloads[category].append(payload.copy())

        if not grouped_payloads:
            raise ValueError(
                f"Qdrant search returned {len(raw_points)} points, but no valid payloads were found."
            )

        return grouped_payloads