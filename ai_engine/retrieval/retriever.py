from qdrant_client import QdrantClient

from app.core.config import COLLECTION_NAME, QDRANT_PATH, TOP_K


class Retriever:
    def __init__(self):
        self.client = QdrantClient(path=str(QDRANT_PATH))

    def search(self, embedding, limit: int = TOP_K):
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

    def close(self):
        self.client.close()