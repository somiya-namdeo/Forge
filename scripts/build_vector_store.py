import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import BASE_DIR, COLLECTION_NAME, QDRANT_PATH

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def build_vector_store(
    embeddings_path: Optional[Path] = None,
    metadata_path: Optional[Path] = None,
    qdrant_path: Optional[Path] = None,
    collection_name: Optional[str] = None
) -> int:
    
    if embeddings_path is None:
        embeddings_path = BASE_DIR / "knowledge_base" / "embeddings.npy"

    if metadata_path is None:
        metadata_path = BASE_DIR / "knowledge_base" / "embedding_metadata.json"

    if qdrant_path is None:
        qdrant_path = QDRANT_PATH

    if collection_name is None:
        collection_name = COLLECTION_NAME

    embeddings_path = Path(embeddings_path)
    metadata_path = Path(metadata_path)
    qdrant_path = Path(qdrant_path)

    if not embeddings_path.exists():
        logger.error(f"Embeddings file not found: {embeddings_path}")
        raise FileNotFoundError(f"Embeddings file does not exist: {embeddings_path}")

    if not metadata_path.exists():
        logger.error(f"Metadata file not found: {metadata_path}")
        raise FileNotFoundError(f"Metadata file does not exist: {metadata_path}")

    logger.info("Loading embeddings...")
    try:
        embeddings: np.ndarray = np.load(embeddings_path)
    except Exception as e:
        logger.error(f"Failed to load embeddings from {embeddings_path}: {e}")
        raise ValueError(f"Corrupted or invalid numpy embeddings file: {e}") from e

    if embeddings.ndim != 2 or embeddings.shape[0] == 0:
        logger.error(f"Invalid embeddings shape: {embeddings.shape}")
        raise ValueError(f"Embeddings array must be 2D non-empty array, got shape {embeddings.shape}")

    logger.info("Loading metadata...")
    try:
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata: List[Dict[str, Any]] = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse metadata JSON from {metadata_path}: {e}")
        raise ValueError(f"Invalid metadata JSON file: {e}") from e

    if len(embeddings) != len(metadata):
        logger.error(
            f"Dimension mismatch: {len(embeddings)} embeddings vs {len(metadata)} metadata items."
        )
        raise ValueError(
            f"Embedding count ({len(embeddings)}) does not match metadata count ({len(metadata)})."
        )

    vector_size = embeddings.shape[1]
    logger.info(f"Loaded {len(embeddings)} vectors of dimension {vector_size}.")

    qdrant_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Initializing Qdrant client at {qdrant_path}...")
    try:
        client = QdrantClient(path=str(qdrant_path))
    except Exception as e:
        logger.error(f"Failed to initialize QdrantClient at {qdrant_path}: {e}")
        raise RuntimeError(f"Qdrant initialization error: {e}") from e

    logger.info("Creating Qdrant collection...")
    if client.collection_exists(collection_name):
        logger.info(f"Collection '{collection_name}' already exists. Recreating safely...")
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )
    logger.info(f"Collection '{collection_name}' created successfully.")

    points = [
        PointStruct(
            id=idx,
            vector=vector.tolist(),
            payload=meta
        )
        for idx, (vector, meta) in enumerate(zip(embeddings, metadata))
    ]

    logger.info("Uploading vectors...")
    try:
        client.upsert(
            collection_name=collection_name,
            points=points
        )
    except Exception as e:
        logger.error(f"Failed to upload points to Qdrant collection '{collection_name}': {e}")
        raise RuntimeError(f"Qdrant upload failure: {e}") from e

    collection_info = client.get_collection(collection_name=collection_name)
    total_vectors = collection_info.points_count

    try:
        client.close()
    except Exception:
        pass

    logger.info("Upload complete.")
    logger.info(f"Total vectors: {total_vectors}")

    return total_vectors


def main() -> None:
    build_vector_store()


if __name__ == "__main__":
    main()
