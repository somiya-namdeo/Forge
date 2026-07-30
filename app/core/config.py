import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

QDRANT_PATH = BASE_DIR / "vector_store" / "qdrant"

COLLECTION_NAME = "forge_knowledge"

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

TOP_K = 5

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.2))

LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 4096))

LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 60))