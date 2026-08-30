"""Embedding service module providing singleton access to sentence embedding models."""

import logging
from typing import Optional
import numpy as np

from langchain_core.embeddings import Embeddings
from huggingface_hub import InferenceClient

from app.core.config import EMBEDDING_MODEL, HUGGINGFACEHUB_API_TOKEN

import threading

logger = logging.getLogger(__name__)

class HuggingFaceInferenceClientEmbeddings(Embeddings):
    """Custom LangChain embedding wrapper using the modern InferenceClient."""

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        if not api_key:
            logger.warning("HUGGINGFACEHUB_API_TOKEN is not set. Inference API may fail.")
        self.client = InferenceClient(
            model=model_name,
            provider="auto",
            api_key=api_key
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        try:
            res = self.client.feature_extraction(texts)
            if isinstance(res, np.ndarray):
                return res.tolist()
            return res
        except Exception as e:
            logger.error("Hugging Face API inference failed for documents: %s", str(e))
            raise RuntimeError(f"Hugging Face API feature_extraction failed: {str(e)}") from e

    def embed_query(self, text: str) -> list[float]:
        try:
            res = self.client.feature_extraction([text])
            if isinstance(res, np.ndarray):
                if res.ndim == 2:
                    return res.tolist()[0]
                return res.tolist()
            if isinstance(res, list):
                if len(res) > 0 and isinstance(res[0], list):
                    return res[0]
                return res
            raise ValueError(f"Unexpected response type from InferenceClient: {type(res)}")
        except Exception as e:
            logger.error("Hugging Face API inference failed for query: %s", str(e))
            raise RuntimeError(f"Hugging Face API feature_extraction failed: {str(e)}") from e

_embedding_model_instance: Optional[HuggingFaceInferenceClientEmbeddings] = None
_embedding_model_lock = threading.Lock()


def get_embedding_model() -> HuggingFaceInferenceClientEmbeddings:
    """Return singleton instance of HuggingFaceInferenceClientEmbeddings to prevent repeated model loading."""
    global _embedding_model_instance
    if _embedding_model_instance is None:
        with _embedding_model_lock:
            if _embedding_model_instance is None:
                logger.info("Initializing HuggingFaceInferenceClientEmbeddings singleton model: %s", EMBEDDING_MODEL)
                try:
                    _embedding_model_instance = HuggingFaceInferenceClientEmbeddings(
                        model_name=EMBEDDING_MODEL,
                        api_key=HUGGINGFACEHUB_API_TOKEN
                    )
                except Exception as e:
                    logger.error("Failed to initialize HuggingFaceInferenceClientEmbeddings: %s", str(e))
                    _embedding_model_instance = None
                    raise
    return _embedding_model_instance
