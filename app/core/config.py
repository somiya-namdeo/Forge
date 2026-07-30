from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

QDRANT_PATH = BASE_DIR / "vector_store" / "qdrant"

COLLECTION_NAME = "forge_knowledge"

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

TOP_K = 5
