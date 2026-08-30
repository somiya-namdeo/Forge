"""Embedding service module providing singleton access to sentence embedding models."""

import logging
from typing import Optional

from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

from app.core.config import EMBEDDING_MODEL, HUGGINGFACEHUB_API_TOKEN

import threading

logger = logging.getLogger(__name__)

_embedding_model_instance: Optional[HuggingFaceInferenceAPIEmbeddings] = None
_embedding_model_lock = threading.Lock()


def get_embedding_model() -> HuggingFaceInferenceAPIEmbeddings:
    """Return singleton instance of HuggingFaceInferenceAPIEmbeddings to prevent repeated model loading."""
    global _embedding_model_instance
    if _embedding_model_instance is None:
        with _embedding_model_lock:
            if _embedding_model_instance is None:
                logger.info("Initializing HuggingFaceInferenceAPIEmbeddings singleton model: %s", EMBEDDING_MODEL)
                try:
                    if not HUGGINGFACEHUB_API_TOKEN:
                        logger.warning("HUGGINGFACEHUB_API_TOKEN is not set. Inference API may fail.")
                    _embedding_model_instance = HuggingFaceInferenceAPIEmbeddings(
                        api_key=HUGGINGFACEHUB_API_TOKEN,
                        model_name=EMBEDDING_MODEL
                    )
                except Exception as e:
                    logger.error("Failed to initialize HuggingFaceInferenceAPIEmbeddings: %s", str(e))
                    _embedding_model_instance = None
                    raise
    return _embedding_model_instance
