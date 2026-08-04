"""Qdrant semantic retriever module for Forge AI engineering platform."""

import logging
import time
from typing import Any, Optional

from app.embeddings.embedding_service import get_embedding_model
from qdrant_client import QdrantClient

from app.core.config import COLLECTION_NAME, QDRANT_PATH, TOP_K
from app.schemas.decision import DecisionRequest

logger = logging.getLogger(__name__)


_qdrant_client_instance: Optional[QdrantClient] = None
_qdrant_retriever_instance: Optional["QdrantRetriever"] = None


def get_qdrant_client() -> QdrantClient:
    """Return singleton instance of QdrantClient to ensure single connection lifecycle."""
    global _qdrant_client_instance
    if _qdrant_client_instance is not None:
        try:
            inner_client = getattr(_qdrant_client_instance, "_client", None)
            if inner_client is not None and getattr(inner_client, "closed", False):
                _qdrant_client_instance = None
        except Exception:
            _qdrant_client_instance = None

    if _qdrant_client_instance is None:
        if not QDRANT_PATH.exists():
            raise RuntimeError(f"Qdrant storage path '{QDRANT_PATH}' does not exist.")
        try:
            logger.info("Initializing QdrantClient singleton at path: %s", QDRANT_PATH)
            _qdrant_client_instance = QdrantClient(path=str(QDRANT_PATH))
        except Exception as exc:
            err_str = str(exc).lower()
            if any(k in err_str for k in ("already accessed", "locked", "permission denied")):
                time.sleep(0.5)
                try:
                    _qdrant_client_instance = QdrantClient(path=str(QDRANT_PATH))
                except Exception as retry_exc:
                    raise RuntimeError(
                        f"Failed to initialize QdrantClient at '{QDRANT_PATH}' (storage locked by another process): {retry_exc}"
                    ) from retry_exc
            else:
                raise RuntimeError(f"Failed to initialize QdrantClient at '{QDRANT_PATH}': {exc}") from exc
    return _qdrant_client_instance


def get_qdrant_retriever() -> "QdrantRetriever":
    """Return singleton instance of QdrantRetriever."""
    global _qdrant_retriever_instance
    if _qdrant_retriever_instance is None:
        _qdrant_retriever_instance = QdrantRetriever()
    return _qdrant_retriever_instance


class QdrantRetriever:
    """Semantic knowledge retriever backed by an existing local Qdrant collection."""

    def __init__(self, top_k: int = TOP_K) -> None:
        """Initialize QdrantRetriever with Qdrant client and embedding model singletons."""
        self.top_k = top_k
        self._client = get_qdrant_client()

        try:
            collections = [c.name for c in self._client.get_collections().collections]
        except Exception as exc:
            raise RuntimeError(f"Failed to inspect Qdrant collections at '{QDRANT_PATH}': {exc}") from exc

        if COLLECTION_NAME not in collections:
            raise ValueError(f"Collection '{COLLECTION_NAME}' does not exist in Qdrant at '{QDRANT_PATH}'.")

        try:
            self._embeddings = get_embedding_model()
        except Exception as exc:
            raise RuntimeError(f"Failed to load embedding model: {exc}") from exc

    @staticmethod
    def _format_value(val: Any) -> str:
        """Format an arbitrary Pydantic field value into a clean string representation."""
        if val is None:
            return ""
        if hasattr(val, "value"):
            return str(val.value)
        if isinstance(val, (list, tuple, set)):
            formatted_items = [str(i.value) if hasattr(i, "value") else str(i) for i in val if i]
            return ", ".join(formatted_items)
        if isinstance(val, dict):
            formatted_pairs = [f"{k}: {v}" for k, v in val.items() if v]
            return "; ".join(formatted_pairs)
        return str(val).strip()

    def _build_semantic_query(self, request: DecisionRequest) -> str:
        """Dynamically construct a semantic query string from all non-empty DecisionRequest fields."""
        data = request.model_dump(exclude_none=True)
        query_parts: list[str] = []

        for field_name, value in data.items():
            formatted = self._format_value(value)
            if formatted:
                clean_field = field_name.replace("_", " ").title()
                query_parts.append(f"{clean_field}: {formatted}")

        if request.preferred_llm:
            pref_low = request.preferred_llm.lower()
            if any(w in pref_low for w in ("llama", "meta")):
                query_parts.append("Preferred Foundation Model: Meta LLaMA 3 3.3 Llama")
            elif any(w in pref_low for w in ("gpt", "openai")):
                query_parts.append("Preferred Foundation Model: OpenAI GPT")
            elif any(w in pref_low for w in ("claude", "anthropic")):
                query_parts.append("Preferred Foundation Model: Anthropic Claude")
            elif "mistral" in pref_low or "mixtral" in pref_low:
                query_parts.append("Preferred Foundation Model: Mistral")
            elif "qwen" in pref_low:
                query_parts.append("Preferred Foundation Model: Qwen")
            elif "deepseek" in pref_low:
                query_parts.append("Preferred Foundation Model: DeepSeek")
            elif "gemini" in pref_low:
                query_parts.append("Preferred Foundation Model: Google Gemini")

        query_text = " | ".join(query_parts)
        if not query_text.strip():
            query_text = str(request)

        return query_text.strip()

    def retrieve(
        self,
        request: DecisionRequest,
        limit: int | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Retrieve relevant technology payloads from Qdrant grouped by category with similarity scores.

        Args:
            request (DecisionRequest): Input parameters detailing project requirements.
            limit (int | None): Optional limit on number of retrieved points. Defaults to TOP_K.

        Returns:
            dict[str, list[dict[str, Any]]]: Dictionary mapping candidate categories to lists
                of retrieved payload dictionaries including appended `_score` similarity scores.

        Raises:
            ValueError: If query embedding fails or search returns empty results.
            RuntimeError: If Qdrant communication encounters execution failures.
        """
        start_time = time.perf_counter()
        top_limit = limit or 150

        query_text = self._build_semantic_query(request)
        if not query_text.strip():
            raise ValueError("Cannot execute Qdrant retrieval: generated semantic search query is empty.")

        try:
            query_vector = self._embeddings.embed_query(query_text)
        except Exception as exc:
            raise ValueError(f"Failed to generate embedding vector for query: {exc}") from exc

        if not query_vector:
            raise ValueError("Generated query embedding vector is empty.")

        try:
            response = self._client.query_points(
                collection_name=COLLECTION_NAME,
                query=query_vector,
                limit=top_limit,
            )
            raw_points = response.points
        except Exception as exc:
            raise RuntimeError(
                f"Failed to execute Qdrant search against collection '{COLLECTION_NAME}': {exc}"
            ) from exc

        if not raw_points:
            raise ValueError(f"Qdrant search returned empty results for query '{query_text}'.")

        grouped_payloads: dict[str, list[dict[str, Any]]] = {}
        top_score: float = float(raw_points[0].score) if raw_points and hasattr(raw_points[0], "score") else 0.0

        for point in raw_points:
            payload = getattr(point, "payload", None)
            if not payload or not isinstance(payload, dict):
                continue

            tech_check = str(payload.get("technology") or payload.get("name") or payload.get("technology_id") or "").lower()
            if "deepeval" in tech_check:
                continue

            item_payload = payload.copy()
            item_payload["_score"] = float(point.score) if hasattr(point, "score") else 0.0

            category = item_payload.get("category")
            if not category or not isinstance(category, str) or not category.strip():
                category = "general"
            else:
                category = category.strip().lower()

            if category not in grouped_payloads:
                grouped_payloads[category] = []

            grouped_payloads[category].append(item_payload)

        if not grouped_payloads:
            raise ValueError(
                f"Qdrant search returned {len(raw_points)} points, but no valid payloads were found."
            )

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        total_docs = sum(len(items) for items in grouped_payloads.values())

        logger.info(
            "Qdrant retrieval completed | Collection=%s | Query=%s... | Latency=%sms | Documents=%d | TopScore=%.4f",
            COLLECTION_NAME,
            query_text[:60],
            elapsed_ms,
            total_docs,
            top_score,
        )

        return grouped_payloads

    def close(self) -> None:
        """Close the underlying Qdrant client connection."""
        global _qdrant_client_instance, _qdrant_retriever_instance
        try:
            self._client.close()
        except Exception:
            pass
        _qdrant_client_instance = None
        _qdrant_retriever_instance = None