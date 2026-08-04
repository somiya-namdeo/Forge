import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

QDRANT_PATH = BASE_DIR / "knowledge_base" / "vector_store"

COLLECTION_NAME = "forge_knowledge"

EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5"

TOP_K = 5

# --- Independent Dual-Groq Provider Configurations ---
# Decision Module LLM Settings (Groq Account #1)
DECISION_PROVIDER = os.getenv("DECISION_PROVIDER", "groq")
DECISION_MODEL = os.getenv("DECISION_MODEL", "llama-3.3-70b-versatile")
DECISION_API_KEY = os.getenv("DECISION_API_KEY", os.getenv("GROQ_API_KEY"))

# Evaluation Module LLM Settings (Groq Account #2)
EVALUATION_PROVIDER = os.getenv("EVALUATION_PROVIDER", "groq")
EVALUATION_MODEL = os.getenv("EVALUATION_MODEL", "llama-3.3-70b-versatile")
EVALUATION_API_KEY = os.getenv("EVALUATION_API_KEY")

# Legacy/Default fallback settings (maintained for backward compatibility)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", DECISION_API_KEY)

LLM_PROVIDER = os.getenv("LLM_PROVIDER", DECISION_PROVIDER)

LLM_MODEL = os.getenv("LLM_MODEL", DECISION_MODEL)

LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.2))

LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 4096))

LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", 60))