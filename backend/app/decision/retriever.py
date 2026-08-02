"""Knowledge retriever module for AI Architecture Recommendation Engine."""

import json
from pathlib import Path
from typing import Any

from app.core.config import BASE_DIR
from app.schemas.decision import DecisionRequest

_DEFAULT_KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"

# Mapping from common directory names or stems to standard logical category names
_CATEGORY_MAPPING: dict[str, str] = {
    "llms": "llm",
    "llm": "llm",
    "embeddings": "embedding",
    "embedding": "embedding",
    "vectordb": "vectordbs",
    "vectordbs": "vectordbs",
    "vector_db": "vectordbs",
    "vector_dbs": "vectordbs",
    "vector_store": "vectordbs",
    "rerankers": "reranker",
    "reranker": "reranker",
    "chunking": "chunking",
    "chunks": "chunking",
    "retrieval": "retrieval",
    "evaluation": "evaluation",
    "frameworks": "framework",
    "framework": "framework",
    "deployment": "deployment",
    "benchmarks": "benchmark",
    "benchmark": "benchmark",
    "best_practices": "best_practices",
    "finetuning": "finetuning",
    "fine_tuning": "finetuning",
    "prompting": "prompting",
}

# Technology directory classification dictionary for processed technology entities
_KNOWN_TECH_CATEGORIES: dict[str, str] = {
    # LLM
    "anthropic_claude": "llm",
    "deepseek": "llm",
    "google_gemini": "llm",
    "meta_llama": "llm",
    "mistral": "llm",
    "openai_gpt": "llm",
    "qwen": "llm",
    "vllm": "llm",
    "ollama": "llm",
    "llama_cpp": "llm",
    "litgpt": "llm",
    "sglang": "llm",
    "hugging_face_text_generation_inference_tgi": "llm",
    "cloudflare_workers_ai": "llm",
    "replicate": "llm",
    "lm_studio": "llm",
    "vertex_ai": "llm",
    "hugging_face_inference_endpoints": "llm",
    # Embedding
    "baai_bge_embeddings": "embedding",
    "e5_embeddings": "embedding",
    "nomic_embed": "embedding",
    "jina_embeddings": "embedding",
    "sentence_transformers": "embedding",
    # VectorDB
    "chroma": "vectordbs",
    "qdrant": "vectordbs",
    "milvus": "vectordbs",
    "pinecone": "vectordbs",
    "weaviate": "vectordbs",
    "faiss": "vectordbs",
    # Reranker
    "bge_reranker": "reranker",
    "cohere_rerank": "reranker",
    "cross_encoder": "reranker",
    "flashrank": "reranker",
    "jina_ai_reranker": "reranker",
    "llm_reranking": "reranker",
    "monot5": "reranker",
    "rankt5": "reranker",
    # Chunking
    "document_aware_chunking": "chunking",
    "fixed_size_chunking": "chunking",
    "hierarchical_chunking": "chunking",
    "paragraph_based_chunking": "chunking",
    "parent_child_chunking": "chunking",
    "recursive_chunking": "chunking",
    "semantic_chunking": "chunking",
    "sentence_based_chunking": "chunking",
    "sliding_window_chunking": "chunking",
    "token_based_chunking": "chunking",
    # Retrieval
    "colbert": "retrieval",
    "contextual_compression_retrieval": "retrieval",
    "crag": "retrieval",
    "dense_retrieval": "retrieval",
    "ensemble_retrieval": "retrieval",
    "graphrag": "retrieval",
    "hyde": "retrieval",
    "multi_query_retrieval": "retrieval",
    "parent_document_retrieval": "retrieval",
    "self_query_retrieval": "retrieval",
    "self_rag": "retrieval",
    # Framework
    "langchain": "framework",
    "llamaindex": "framework",
    "dspy": "framework",
    "haystack": "framework",
    "langgraph": "framework",
    "guidance": "framework",
    "lmql": "framework",
    "react": "framework",
    # Evaluation
    "arize_ai": "evaluation",
    "arize_phoenix": "evaluation",
    "deepeval": "evaluation",
    "langfuse": "evaluation",
    "langsmith": "evaluation",
    "mlflow_evaluation": "evaluation",
    "openai_evals": "evaluation",
    "promptfoo": "evaluation",
    "ragas": "evaluation",
    "trulens": "evaluation",
    # Fine-Tuning
    "axolotl": "finetuning",
    "llama_factory": "finetuning",
    "lora": "finetuning",
    "peft": "finetuning",
    "qlora": "finetuning",
    "trl": "finetuning",
    "unsloth": "finetuning",
    # Deployment
    "aws_sagemaker": "deployment",
    "azure_ai_foundry": "deployment",
    "bentoml": "deployment",
    "docker": "deployment",
    "docker_compose": "deployment",
    "fly_io": "deployment",
    "google_cloud_run": "deployment",
    "grafana": "deployment",
    "helm": "deployment",
    "hugging_face_spaces": "deployment",
    "k3s": "deployment",
    "kserve": "deployment",
    "kubernetes": "deployment",
    "mlserver": "deployment",
    "modal": "deployment",
    "nvidia_triton_inference_server": "deployment",
    "prometheus": "deployment",
    "railway": "deployment",
    "ray_serve": "deployment",
    "render": "deployment",
    "vercel": "deployment",
    "vercel_edge_functions": "deployment",
    "weights_biases": "deployment",
    # Prompting
    "chain_of_thought_cot": "prompting",
    "few_shot_prompting": "prompting",
    "graph_of_thoughts_got": "prompting",
    "one_shot_prompting": "prompting",
    "self_consistency": "prompting",
    "step_back_prompting": "prompting",
    "tree_of_thoughts_tot": "prompting",
    "zero_shot_prompting": "prompting",
}

_SPECIAL_DISPLAY_NAMES: dict[str, str] = {
    "openai_gpt": "OpenAI GPT",
    "anthropic_claude": "Anthropic Claude",
    "meta_llama": "Meta LLaMA",
    "baai_bge_embeddings": "BAAI BGE Embeddings",
    "bge_reranker": "BGE Reranker",
    "cohere_rerank": "Cohere Rerank",
    "google_gemini": "Google Gemini",
    "aws_sagemaker": "AWS SageMaker",
    "azure_ai_foundry": "Azure AI Foundry",
    "google_cloud_run": "Google Cloud Run",
    "fly_io": "Fly.io",
    "nvidia_triton_inference_server": "NVIDIA Triton Inference Server",
    "hugging_face_text_generation_inference_tgi": "Hugging Face TGI",
    "hugging_face_spaces": "Hugging Face Spaces",
    "hugging_face_inference_endpoints": "Hugging Face Endpoints",
    "cloudflare_workers_ai": "Cloudflare Workers AI",
    "vercel_edge_functions": "Vercel Edge Functions",
    "tree_of_thoughts_tot": "Tree of Thoughts (ToT)",
    "graph_of_thoughts_got": "Graph of Thoughts (GoT)",
    "chain_of_thought_cot": "Chain of Thought (CoT)",
}


class KnowledgeRetriever:
    """Retriever responsible for discovering, parsing, and normalizing technology candidates from disk."""

    def __init__(self, knowledge_dir: str | Path | None = None) -> None:
        """Initialize KnowledgeRetriever with target knowledge base directory."""
        self.knowledge_dir = (
            _DEFAULT_KNOWLEDGE_DIR
            if knowledge_dir is None
            else Path(knowledge_dir).resolve()
        )
        self._cache: dict[str, list[dict[str, Any]]] | None = None

    def refresh_cache(self) -> None:
        """Invalidate internal lazy-loaded knowledge base cache."""
        self._cache = None

    @staticmethod
    def _format_display_name(raw_name: str) -> str:
        """Format raw technology identifier into human-readable display name."""
        lowered = raw_name.strip().lower()
        if lowered in _SPECIAL_DISPLAY_NAMES:
            return _SPECIAL_DISPLAY_NAMES[lowered]

        words = raw_name.replace("_", " ").replace("-", " ").split()
        capitalized = []
        for w in words:
            wl = w.lower()
            if wl in ("ai", "db", "rag", "cot", "got", "tot", "llm", "gpt", "tgi", "api", "cpu", "gpu"):
                capitalized.append(w.upper())
            else:
                capitalized.append(w.capitalize())
        return " ".join(capitalized)

    @staticmethod
    def _normalize_category(raw_category: str) -> str:
        """Map raw category string to standard logical category name using _CATEGORY_MAPPING."""
        lowered = raw_category.strip().lower()
        return _CATEGORY_MAPPING.get(lowered, lowered)

    def _infer_category(self, file_path: Path) -> str:
        """Determine logical category for a JSON knowledge file dynamically from path and content hints."""
        try:
            rel_parts = [p.lower() for p in file_path.relative_to(self.knowledge_dir).parts]
        except ValueError:
            rel_parts = [p.lower() for p in file_path.parts]

        # 1. Direct parent directory under knowledge_base (excluding 'processed')
        if len(rel_parts) > 1 and rel_parts[0] != "processed":
            top_dir = rel_parts[0]
            if top_dir in _CATEGORY_MAPPING:
                return _CATEGORY_MAPPING[top_dir]
            return top_dir

        # 2. Technology folder inside 'processed/<tech_name>/...'
        if len(rel_parts) > 2 and rel_parts[0] == "processed":
            tech_dir = rel_parts[1]
            if tech_dir in _KNOWN_TECH_CATEGORIES:
                return _KNOWN_TECH_CATEGORIES[tech_dir]

        # 3. Filename stem matching or keyword inference
        stem = file_path.stem.lower()
        if stem in _CATEGORY_MAPPING:
            return _CATEGORY_MAPPING[stem]

        rel_str = "/".join(rel_parts)
        if "embed" in stem or "embed" in rel_str:
            return "embedding"
        if "rerank" in stem or "rerank" in rel_str:
            return "reranker"
        if "vector" in stem or "vector" in rel_str or "chroma" in rel_str or "qdrant" in rel_str:
            return "vectordb"
        if "chunk" in stem or "chunk" in rel_str:
            return "chunking"
        if "eval" in stem or "eval" in rel_str:
            return "evaluation"
        if "retriev" in stem or "rag" in rel_str:
            return "retrieval"
        if "llm" in stem or "gpt" in rel_str or "claude" in rel_str:
            return "llm"

        return stem

    @staticmethod
    def _parse_json_file(file_path: Path) -> list[dict[str, Any]]:
        """Safely parse a JSON file returning list of entity dictionaries."""
        if not file_path.exists() or not file_path.is_file():
            return []

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                return [item for item in data if isinstance(item, dict)]

            if isinstance(data, dict):
                entries = (
                    data.get("entries")
                    or data.get("items")
                    or data.get("data")
                    or data.get("candidates")
                )
                if isinstance(entries, list):
                    return [item for item in entries if isinstance(item, dict)]
                return [data]
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            return []

        return []

    def _load_knowledge_base(self) -> dict[str, list[dict[str, Any]]]:
        """Recursively discover and parse all JSON files in knowledge_dir into normalized categories."""
        if self._cache is not None:
            return self._cache

        raw_category_candidates: dict[str, dict[str, dict[str, Any]]] = {}

        if not self.knowledge_dir.exists() or not self.knowledge_dir.is_dir():
            self._cache = {}
            return self._cache

        # Scan all JSON files recursively (excluding individual chunk files and chunks directory)
        for json_file in sorted(self.knowledge_dir.rglob("*.json")):
            if "chunks" in json_file.parts or json_file.name in ("chunks.json", "embedding_metadata.json"):
                continue

            file_inferred_category = self._infer_category(json_file)
            parsed_entities = self._parse_json_file(json_file)

            for entity in parsed_entities:
                # Skip raw text chunk items
                if "chunk_id" in entity or "chunk_index" in entity:
                    continue

                # Use category stored inside entity metadata if available, falling back to file inference
                entity_cat = entity.get("category")
                if entity_cat and isinstance(entity_cat, str) and entity_cat.strip():
                    category = self._normalize_category(entity_cat)
                else:
                    category = file_inferred_category

                if category not in raw_category_candidates:
                    raw_category_candidates[category] = {}

                # Extended technology identifier extraction lookup order
                tech_id = (
                    entity.get("canonical_name")
                    or entity.get("display_name")
                    or entity.get("model_name")
                    or entity.get("technology")
                    or entity.get("id")
                    or entity.get("name")
                )
                if not tech_id or not isinstance(tech_id, str):
                    if json_file.parent != self.knowledge_dir and json_file.parent.name != "processed":
                        tech_id = json_file.parent.name
                    else:
                        tech_id = json_file.stem

                tech_key = str(tech_id).strip().lower()

                # Prefer explicit display metadata before formatting fallback
                explicit_display = (
                    entity.get("display_name")
                    or entity.get("canonical_name")
                    or entity.get("name")
                )
                if explicit_display and isinstance(explicit_display, str):
                    display_name = explicit_display.strip()
                else:
                    display_name = self._format_display_name(str(tech_id))

                if tech_key not in raw_category_candidates[category]:
                    raw_category_candidates[category][tech_key] = {
                        "id": tech_key,
                        "name": display_name,
                        "category": category,
                        "technology": tech_key,
                    }

                # Merge metadata fields from parsed JSON file
                existing = raw_category_candidates[category][tech_key]
                for k, v in entity.items():
                    if k not in existing or existing[k] is None:
                        existing[k] = v

        # Convert to category -> list[dict] mapping sorted deterministically
        kb_result: dict[str, list[dict[str, Any]]] = {}
        for category, tech_dict in sorted(raw_category_candidates.items()):
            sorted_candidates = [
                tech_dict[k] for k in sorted(tech_dict.keys())
            ]
            if sorted_candidates:
                kb_result[category] = sorted_candidates

        self._cache = kb_result
        return kb_result

    def retrieve(self, request: DecisionRequest) -> dict[str, list[dict[str, Any]]]:
        """Retrieve candidate technology entities grouped by category.

        Args:
            request (DecisionRequest): Input parameters detailing project requirements,
                constraints, and deployment goals. Retained for signature consistency.

        Returns:
            dict[str, list[dict[str, Any]]]: Dictionary mapping candidate categories to lists
                of normalized knowledge base technology candidates.
        """
        _ = request
        kb = self._load_knowledge_base()
        return {category: [item.copy() for item in candidates] for category, candidates in kb.items()}
