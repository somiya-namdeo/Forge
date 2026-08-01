"""Recommendation engine module for selecting optimal AI architecture components."""

from typing import Any

from app.schemas.decision import RecommendationItem

_DEFAULT_CONFIDENCE = 0.70

_NAME_PATHS = (
    "display_name",
    "canonical_name",
    "model_name",
    "name",
    "technology",
    "id",
    "title",
)

_CONFIDENCE_PATHS = (
    "recommendation.confidence",
    "recommendation.score",
    "confidence",
    "score",
)

_OPEN_SOURCE_PATHS = (
    "open_source",
    "is_open_source",
    "pricing.open_source",
    "pricing.is_open_source",
    "cost.open_source",
)

_FREE_TIER_PATHS = (
    "free_tier",
    "has_free_tier",
    "pricing.free_tier",
    "pricing.has_free_tier",
    "cost.free_tier",
)

_LATENCY_PATHS = (
    "latency_ms",
    "latency",
    "performance.latency_ms",
    "performance.inference_latency_ms",
)

_STARS_PATHS = (
    "stars",
    "github_stars",
    "adoption.stars",
    "adoption.github_stars",
)

_COMMUNITY_PATHS = (
    "community_score",
    "popularity",
    "adoption.community_score",
    "adoption.popularity",
)

_QUALITY_PATHS = (
    "quality_score",
    "performance_score",
    "quality",
    "accuracy",
    "performance.quality_score",
    "performance.score",
    "performance.accuracy",
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
    def _extract_first_value(cls, entry: dict[str, Any], paths: tuple[str, ...]) -> Any:
        """Retrieve the first non-None value matching any flat or dot-separated path."""
        for path in paths:
            val = cls._get_nested_value(entry, path)
            if val is not None:
                return val
        return None

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
    def _extract_confidence(cls, entry: dict[str, Any]) -> float:
        """Extract recommendation confidence score, clamped to [0.0, 1.0]."""
        for path in _CONFIDENCE_PATHS:
            val = cls._get_nested_value(entry, path)
            if isinstance(val, (int, float)):
                score_float = float(val)
                if 1.0 < score_float <= 100.0:
                    score_float /= 100.0
                return max(0.0, min(1.0, score_float))
        return _DEFAULT_CONFIDENCE

    @classmethod
    def _build_reason(cls, entry: dict[str, Any], category: str) -> str:
        """Construct a deterministic, metadata-aware rationale sentence."""
        phrases: list[str] = [
            f"Selected as the top candidate for '{category}' based on suitability scoring."
        ]

        # 1. Open Source check
        is_open_source = cls._extract_first_value(entry, _OPEN_SOURCE_PATHS)
        if is_open_source is True:
            phrases.append("Open-source solution.")

        # 2. Free Tier check
        has_free_tier = cls._extract_first_value(entry, _FREE_TIER_PATHS)
        if has_free_tier is True:
            phrases.append("Offers free tier.")

        # 3. Community Adoption check
        stars = cls._extract_first_value(entry, _STARS_PATHS)
        community = cls._extract_first_value(entry, _COMMUNITY_PATHS)
        if (isinstance(stars, (int, float)) and stars > 1000) or (
            isinstance(community, (int, float)) and community > 0.70
        ):
            phrases.append("High community adoption.")

        # 4. Latency check
        latency = cls._extract_first_value(entry, _LATENCY_PATHS)
        if isinstance(latency, (int, float)) and 0 < latency < 100:
            phrases.append("Optimized for low latency.")

        # 5. Production deployment check
        deployments = (
            entry.get("supported_deployments")
            or entry.get("deployments")
            or entry.get("supported_platforms")
        )
        if deployments:
            phrases.append("Suitable for production deployments.")

        # 6. Quality check
        quality = cls._extract_first_value(entry, _QUALITY_PATHS)
        if isinstance(quality, (int, float)) and (quality > 0.80 or quality > 80):
            phrases.append("High quality and accuracy ratings.")

        return " ".join(phrases)

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
        recommended_name = cls._extract_name(top_candidate)
        top_id = str(top_candidate.get("id") or top_candidate.get("technology") or recommended_name).strip().lower()
        confidence = cls._extract_confidence(top_candidate)
        reason = cls._build_reason(top_candidate, category)
        alternatives = cls._extract_alternatives(items, recommended_name, top_id)

        return RecommendationItem(
            category=category,
            recommended=recommended_name,
            confidence=confidence,
            reason=reason,
            alternatives=alternatives,
        )

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
