"""Embedding service module providing singleton access to sentence embedding models."""

import logging
from typing import Optional

from langchain_community.embeddings import HuggingFaceBgeEmbeddings

from app.core.config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

_embedding_model_instance: Optional[HuggingFaceBgeEmbeddings] = None


def get_embedding_model() -> HuggingFaceBgeEmbeddings:
    """Return singleton instance of HuggingFaceBgeEmbeddings to prevent repeated model loading."""
    global _embedding_model_instance
    if _embedding_model_instance is None:
        logger.info("Initializing HuggingFaceBgeEmbeddings singleton model: %s", EMBEDDING_MODEL)
        _embedding_model_instance = HuggingFaceBgeEmbeddings(model_name=EMBEDDING_MODEL)
    return _embedding_model_instance
