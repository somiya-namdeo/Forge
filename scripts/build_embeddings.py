import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import BASE_DIR, EMBEDDING_MODEL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def build_embeddings(
    chunks_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    model_name: str = EMBEDDING_MODEL,
    batch_size: int = 32
) -> Tuple[Path, Path]:
    
    if chunks_path is None:
        chunks_path = BASE_DIR / "knowledge_base" / "chunks.json"

    if output_dir is None:
        output_dir = BASE_DIR / "knowledge_base"

    chunks_path = Path(chunks_path)
    output_dir = Path(output_dir)

    if not chunks_path.exists():
        logger.error(f"Chunks file not found at: {chunks_path}")
        raise FileNotFoundError(f"Input chunks file does not exist: {chunks_path}")

    logger.info("Loading chunks...")
    try:
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks: List[Dict[str, Any]] = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from {chunks_path}: {e}")
        raise ValueError(f"Invalid JSON format in chunks file: {e}") from e

    if not isinstance(chunks, list) or len(chunks) == 0:
        logger.error(f"Chunks file {chunks_path} is empty or not a list.")
        raise ValueError("Chunks list must not be empty.")

    logger.info(f"Loaded {len(chunks)} chunks.")

    texts = []
    metadata = []

    for i, chunk in enumerate(chunks):
        if "text" not in chunk:
            raise KeyError(f"Chunk at index {i} missing required key 'text'")
        texts.append(chunk["text"])
        metadata.append({
            "chunk_id": chunk.get("chunk_id"),
            "technology": chunk.get("technology"),
            "source": chunk.get("source"),
            "path": chunk.get("path"),
            "chunk_index": chunk.get("chunk_index"),
            "text": chunk.get("text"),
            "character_count": chunk.get("character_count")
        })

    logger.info(f"Loading embedding model '{model_name}'...")
    model = SentenceTransformer(model_name)

    logger.info("Generating embeddings...")
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True
    )

    logger.info(f"Embeddings shape: {embeddings.shape}")

    output_dir.mkdir(parents=True, exist_ok=True)
    embeddings_file = output_dir / "embeddings.npy"
    metadata_file = output_dir / "embedding_metadata.json"

    logger.info("Saving embeddings...")
    np.save(embeddings_file, embeddings)
    logger.info(f"Saved embeddings to {embeddings_file}")

    logger.info("Saving metadata...")
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved metadata to {metadata_file}")

    logger.info("Embedding generation complete.")
    return embeddings_file, metadata_file


def main() -> None:
    build_embeddings()


if __name__ == "__main__":
    main()
