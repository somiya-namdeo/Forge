"""Recommendation engine module for selecting optimal AI architecture components."""

from typing import Any, Optional
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
    def _extract_tech_key(cls, entry: dict[str, Any]) -> str:
        """Extract a normalized unique key representing a technology entity."""
        raw = (
            entry.get("technology_id")
            or entry.get("technology")
            or entry.get("canonical_name")
            or entry.get("id")
            or entry.get("display_name")
            or entry.get("name")
            or ""
        )
        s = str(raw).strip().lower().replace("_", " ").replace("-", " ")
        return " ".join(s.split())

    @classmethod
    def _calculate_dynamic_confidence(
        cls, top_candidate: dict[str, Any], runner_up: Optional[dict[str, Any]] = None
    ) -> float:
        """Calculate calibrated confidence score directly reflecting recommendation strength and score margin."""
        top_score = float(top_candidate.get("score", 0.7))
        runner_up_score = float(runner_up.get("score", 0.0)) if runner_up else 0.0
        margin = max(0.0, top_score - runner_up_score)

        if top_score >= 0.88 and margin >= 0.10:
            base_conf = 0.90 + min(0.08, (top_score - 0.88) * 0.40 + margin * 0.15)
        elif top_score >= 0.72:
            base_conf = 0.70 + min(0.15, (top_score - 0.72) * 0.80 + margin * 0.10)
        elif top_score >= 0.55:
            base_conf = 0.55 + min(0.14, (top_score - 0.55) * 0.70 + margin * 0.05)
        else:
            base_conf = max(0.20, round(top_score * 0.90, 4))

        subscores = top_candidate.get("subscores", {})
        if subscores.get("preferred_llm_match", 0.0) >= 0.90:
            base_conf += 0.03

        return min(0.98, max(0.20, round(base_conf, 4)))

    @classmethod
    def _create_recommendation_item(
        cls, category: str, items: list[dict[str, Any]]
    ) -> RecommendationItem | None:
        """Construct a RecommendationItem from a category's scored candidates, filtering out duplicate technologies."""
        if not items:
            return None

        # Deduplicate candidate entries by technology key and display name, preserving score ranking order
        unique_candidates: list[dict[str, Any]] = []
        seen_keys: set[str] = set()

        for item in items:
            tech_key = cls._extract_tech_key(item)
            display_name = cls._extract_name(item)

            if display_name == "Unknown":
                continue

            lowered_name = display_name.lower()
            if tech_key in seen_keys or lowered_name in seen_keys:
                continue

            seen_keys.add(tech_key)
            seen_keys.add(lowered_name)
            unique_candidates.append(item)

        if not unique_candidates:
            return None

        top_candidate = unique_candidates[0]
        recommended_name = cls._extract_name(top_candidate)

        # Extract distinct alternative candidates (up to 3)
        alt_candidates = unique_candidates[1:4]
        alt_names = [cls._extract_name(cand) for cand in alt_candidates]
        runner_up = alt_candidates[0] if alt_candidates else None

        # Calculate calibrated confidence score
        confidence = cls._calculate_dynamic_confidence(top_candidate, runner_up)

        reason = f"Recommended for {category} based on multi-factor suitability scoring."

        rec = RecommendationItem(
            category=category,
            recommended=recommended_name,
            confidence=confidence,
            reason=reason,
            alternatives=alt_names,
        )
        rec._top_candidate = top_candidate
        rec._runner_up = runner_up
        rec._alternative_candidates = alt_candidates
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
