from sentence_transformers import SentenceTransformer
from app.core.config import EMBEDDING_MODEL
import numpy as np
import torch


class QueryEncoder:
    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        self.model.eval()

    def encode(self, query: str) -> np.ndarray:
        query = query.strip()

        if not query:
            raise ValueError("Query cannot be empty.")

        with torch.no_grad():
            embedding = self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True
            )

        return embedding