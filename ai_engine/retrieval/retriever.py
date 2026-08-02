import logging
from typing import Any, Dict, List, Optional
from qdrant_client import QdrantClient

from ai_engine.retrieval.query_encoder import QueryEncoder
from app.core.config import COLLECTION_NAME, QDRANT_PATH, TOP_K

logger = logging.getLogger(__name__)


class RetrievalResult(str):
    """Structured retrieval result that acts as a string while preserving enriched chunk metadata.

    Inheriting from str ensures full backward compatibility with any callers expecting
    a plain text string output, while attaching a .chunks property containing all
    14 enriched metadata fields (chunk_id, technology, technology_id, category, organization,
    license, priority, update_frequency, source, url, path, chunk_index, text, character_count, score).
    """

    def __new__(cls, content: str, chunks: Optional[List[Dict[str, Any]]] = None):
        obj = super().__new__(cls, content)
        obj.chunks = chunks or []
        return obj

    @property
    def metadata(self) -> List[Dict[str, Any]]:
        """Return full list of enriched metadata dictionaries for retrieved chunks."""
        return [
            {k: v for k, v in chunk.items() if k != "text"}
            for chunk in self.chunks
        ]


class Retriever:
    """Retrieval component for vector similarity search over Qdrant."""

    def __init__(self) -> None:
        """Initialize QueryEncoder and Qdrant database client."""
        self.encoder = QueryEncoder()
        self.client = QdrantClient(path=str(QDRANT_PATH))

    def retrieve(self, query: str, limit: int = TOP_K) -> RetrievalResult:
        """Encode natural language query, search vector store, and return formatted context with enriched metadata.

        Args:
            query (str): Natural language input query string.
            limit (int): Maximum number of top results to retrieve.

        Returns:
            RetrievalResult: Formatted string representation containing context chunks,
                with attached `.chunks` property preserving full enriched metadata payloads.
        """
        embedding = self.encoder.encode(query)
        results = self.search(embedding, limit=limit)

        chunks: List[Dict[str, Any]] = []
        context_chunks: List[str] = []

        for point in results:
            payload = point.get("payload", {})
            if isinstance(payload, dict):
                chunk_data = {
                    "chunk_id": payload.get("chunk_id"),
                    "technology": payload.get("technology"),
                    "technology_id": payload.get("technology_id"),
                    "category": payload.get("category"),
                    "organization": payload.get("organization"),
                    "license": payload.get("license"),
                    "priority": payload.get("priority"),
                    "update_frequency": payload.get("update_frequency"),
                    "source": payload.get("source"),
                    "url": payload.get("url"),
                    "path": payload.get("path"),
                    "chunk_index": payload.get("chunk_index"),
                    "text": payload.get("text", ""),
                    "character_count": payload.get("character_count"),
                    "score": point.get("score"),
                }
                chunks.append(chunk_data)
                if chunk_data["text"]:
                    context_chunks.append(chunk_data["text"])

        content = (
            "\n\n".join(context_chunks)
            if context_chunks
            else "No specific context retrieved."
        )

        return RetrievalResult(content, chunks=chunks)

    def search(self, embedding: Any, limit: int = TOP_K) -> List[Dict[str, Any]]:
        """Execute raw vector search on Qdrant collection.

        Args:
            embedding (Any): Vector embedding array/list.
            limit (int): Maximum number of points to return.

        Returns:
            List[Dict[str, Any]]: List of result objects with similarity score and full metadata payload.
        """
        try:
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=embedding,
                limit=limit,
            ).points
        except Exception as e:
            logger.error(f"Error querying Qdrant collection '{COLLECTION_NAME}': {e}")
            return []

        return [
            {
                "score": float(point.score),
                "payload": point.payload or {},
            }
            for point in results
        ]

    def close(self) -> None:
        """Close connection to Qdrant storage."""
        self.client.close()