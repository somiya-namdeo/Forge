from qdrant_client import QdrantClient

from ai_engine.retrieval.query_encoder import QueryEncoder
from app.core.config import COLLECTION_NAME, QDRANT_PATH, TOP_K


class Retriever:
    """Retrieval component for vector similarity search over Qdrant."""

    def __init__(self) -> None:
        """Initialize QueryEncoder and Qdrant database client."""
        self.encoder = QueryEncoder()
        self.client = QdrantClient(path=str(QDRANT_PATH))

    # TODO:
    # Return a RetrievalResult model instead of a plain string
    # once source attribution and metadata are supported.
    def retrieve(self, query: str, limit: int = TOP_K) -> str:
        """Encode natural language query, search vector store, and return formatted context.

        Args:
            query (str): Natural language input query string.
            limit (int): Maximum number of top results to retrieve.

        Returns:
            str: Combined context text from matching document chunks.
        """
        embedding = self.encoder.encode(query)
        results = self.search(embedding, limit=limit)

        context_chunks = [
            point["payload"]["text"]
            for point in results
            if "payload" in point and "text" in point["payload"] and point["payload"]["text"]
        ]

        return (
            "\n\n".join(context_chunks)
            if context_chunks
            else "No specific context retrieved."
        )

    def search(self, embedding, limit: int = TOP_K):
        """Execute raw vector search on Qdrant collection.

        Args:
            embedding: Vector embedding array/list.
            limit (int): Maximum number of points to return.

        Returns:
            List[Dict]: List of result objects with score and payload.
        """
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=embedding,
            limit=limit,
        ).points

        return [
            {
                "score": point.score,
                "payload": point.payload,
            }
            for point in results
        ]

    def close(self) -> None:
        """Close connection to Qdrant storage."""
        self.client.close()