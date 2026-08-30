from app.embeddings.embedding_service import get_embedding_model
import numpy as np


class QueryEncoder:
    def __init__(self):
        self.model = get_embedding_model()

    def encode(self, query: str) -> np.ndarray:
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        embedding_list = self.model.embed_query(query)
        embedding = np.array(embedding_list, dtype=np.float32)

        # Ensure normalized like the original implementation
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding