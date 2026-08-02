"""Recommendation engine module for selecting optimal AI architecture components."""

from typing import Any, List, Optional
from app.schemas.decision import RecommendationItem

_NAME_PATHS = (
    "display_name",
    "canonical_name",
    "model_name",
    "name",
    "technology",
    "id",
    "title",
)

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


class RecommendationEngine:
    """Engine responsible for selecting top candidate technologies and assembling RecommendationItems."""

    @staticmethod
    def _get_nested_value(entry: dict[str, Any], path: str) -> Any:
        """Retrieve a value from dictionary using a dot-separated key path."""
        if not isinstance(entry, dict):
            return None
        keys = path.split(".")
        curr: Any = entry
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return None
        return curr

    @classmethod
    def _extract_name(cls, entry: dict[str, Any]) -> str:
        """Extract candidate display name using priority metadata paths and formatting fallbacks."""
        for path in _NAME_PATHS:
            val = cls._get_nested_value(entry, path)
            if val and isinstance(val, str) and val.strip():
                s = val.strip()
                lowered = s.lower()
                if lowered in _SPECIAL_DISPLAY_NAMES:
                    return _SPECIAL_DISPLAY_NAMES[lowered]
                if "_" in s or "-" in s:
                    words = s.replace("_", " ").replace("-", " ").split()
                    cap = [
                        w.upper()
                        if w.lower() in ("ai", "db", "rag", "cot", "got", "tot", "llm", "gpt", "tgi", "api", "cpu", "gpu", "aws", "gcp")
                        else w.capitalize()
                        for w in words
                    ]
                    return " ".join(cap)
                return s
        return "Unknown"

    @classmethod
    def _calculate_dynamic_confidence(
        cls, top_candidate: dict[str, Any], runner_up: Optional[dict[str, Any]] = None
    ) -> float:
        """Calculate calibrated confidence score directly reflecting recommendation strength and score margin."""
        top_score = float(top_candidate.get("score", 0.7))
        runner_up_score = float(runner_up.get("score", 0.0)) if runner_up else 0.0
        margin = max(0.0, top_score - runner_up_score)

        # Base confidence scales directly with composite top_score and margin dominance
        confidence = round(top_score * 0.85 + margin * 0.15 + 0.10, 4)
        return min(0.98, max(0.20, confidence))

    @classmethod
    def _extract_alternatives(
        cls, items: list[dict[str, Any]], top_name: str, top_id: str
    ) -> list[str]:
        """Extract up to 3 distinct alternative technology names."""
        alternatives: list[str] = []
        seen_names: set[str] = {top_name.lower()}
        seen_ids: set[str] = {top_id.lower()}

        for item in items[1:]:
            if len(alternatives) >= 3:
                break

            alt_name = cls._extract_name(item)
            alt_id = str(item.get("id") or item.get("technology") or alt_name).strip().lower()

            if alt_name == "Unknown":
                continue

            lowered_name = alt_name.lower()
            if lowered_name in seen_names or alt_id in seen_ids:
                continue

            seen_names.add(lowered_name)
            seen_ids.add(alt_id)
            alternatives.append(alt_name)

        return alternatives

    @classmethod
    def _create_recommendation_item(
        cls, category: str, items: list[dict[str, Any]]
    ) -> RecommendationItem | None:
        """Construct a RecommendationItem from a category's scored candidates."""
        if not items:
            return None

        top_candidate = items[0]
        runner_up = items[1] if len(items) > 1 else None

        recommended_name = cls._extract_name(top_candidate)
        top_id = str(top_candidate.get("id") or top_candidate.get("technology") or recommended_name).strip().lower()

        # Calculate calibrated confidence score
        confidence = cls._calculate_dynamic_confidence(top_candidate, runner_up)

        reason = f"Recommended for {category} based on multi-factor suitability scoring."
        alternatives = cls._extract_alternatives(items, recommended_name, top_id)

        rec = RecommendationItem(
            category=category,
            recommended=recommended_name,
            confidence=confidence,
            reason=reason,
            alternatives=alternatives,
        )
        rec._top_candidate = top_candidate
        rec._runner_up = runner_up
        return rec

    def recommend(
        self, scored_candidates: dict[str, list[dict[str, Any]]]
    ) -> list[RecommendationItem]:
        """Select top candidate technologies for each category and build RecommendationItems."""
        recommendations: list[RecommendationItem] = []

        for category, items in scored_candidates.items():
            rec_item = self._create_recommendation_item(category, items)
            if rec_item is not None:
                recommendations.append(rec_item)

        recommendations.sort(key=lambda rec: rec.category)
        return recommendations
