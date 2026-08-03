"""Candidate scoring engine for AI Architecture Recommendation Engine."""

from typing import Any, Dict, List, Optional, Union
from app.decision.domain_detector import Domain
from app.decision.requirement_analyzer import BudgetTier, DocScaleTier, ProjectProfile, RequirementAnalyzer, ScaleTier
from app.schemas.decision import DecisionRequest, DeploymentTarget, Priority

_DEFAULT_NEUTRAL_SCORE = 0.70


class ScoringEngine:
    """Engine responsible for computing multi-factor suitability scores for technology candidates."""

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

    # --- 1. Semantic Similarity ---
    @classmethod
    def _calc_semantic_similarity(cls, entry: dict[str, Any], profile: ProjectProfile) -> float:
        """Compute keyword and semantic overlap score between candidate metadata and project description."""
        query_words = set(profile.project_description.lower().split())
        if not query_words:
            return 0.5

        text_content = str(
            entry.get("text")
            or entry.get("description")
            or entry.get("name")
            or entry.get("technology")
            or ""
        ).lower()

        matches = sum(1 for w in query_words if len(w) > 3 and w in text_content)
        overlap_ratio = matches / max(1, len(query_words))
        return min(1.0, max(0.2, round(0.4 + overlap_ratio * 1.5, 4)))

    # --- 2. Domain Match ---
    @classmethod
    def _calc_domain_match(cls, entry: dict[str, Any], profile: ProjectProfile) -> float:
        """Calculate domain suitability based on project domain classification."""
        domain = profile.domain
        tech_name = str(entry.get("technology") or entry.get("name") or "").lower()
        entry_text = str(entry.get("text") or "").lower()

        domain_affinities = {
            Domain.RESEARCH: {"qdrant", "ragas", "llamaindex", "gpt", "bge", "sentence_transformers"},
            Domain.ENTERPRISE: {"pinecone", "claude", "kubernetes", "aws", "azure", "milvus"},
            Domain.STARTUP: {"chroma", "deepseek", "ollama", "docker", "faiss", "fastapi"},
            Domain.HEALTHCARE: {"on_prem", "privacy", "hipaa", "claude", "qdrant"},
            Domain.LEGAL: {"claude", "gpt", "ragas", "qdrant", "reranker"},
            Domain.FINANCE: {"pinecone", "milvus", "claude", "aws", "soc2"},
            Domain.DEVELOPER_TOOLS: {"ollama", "vllm", "tgi", "qwen", "fastapi", "docker"},
            Domain.EDUCATION: {"chroma", "faiss", "ollama", "gpt"},
            Domain.CUSTOMER_SUPPORT: {"milvus", "qdrant", "fastapi", "claude", "gpt"},
        }

        affinities = domain_affinities.get(domain, set())
        if any(a in tech_name or a in entry_text for a in affinities):
            return 1.0
        return 0.65

    # --- 3. Deployment Match ---
    @classmethod
    def _calc_deployment_match(cls, entry: dict[str, Any], profile: ProjectProfile) -> float:
        """Score candidate compatibility with target deployment environment."""
        target = profile.deployment.value.lower()
        tech_name = str(entry.get("technology") or entry.get("name") or "").lower()
        entry_text = (str(entry.get("text") or "") + " " + str(entry.get("path") or "")).lower()

        full_text = tech_name + " " + entry_text

        # 1. AWS Target
        if target == "aws":
            if any(k in full_text for k in ("aws", "sagemaker", "eks", "bedrock")):
                return 1.0
            if any(k in full_text for k in ("azure", "azure_ai_foundry", "azure_ml", "gcp", "vertex_ai")):
                return 0.05  # Severe penalty for competing cloud platforms
            if any(k in full_text for k in ("kubernetes", "docker", "triton", "tgi", "vllm", "fastapi")):
                return 0.80
            return 0.50

        # 2. Azure Target
        if target == "azure":
            if any(k in full_text for k in ("azure", "azure_ai_foundry", "azure_ml", "aks")):
                return 1.0
            if any(k in full_text for k in ("aws", "sagemaker", "eks", "bedrock", "gcp", "vertex_ai")):
                return 0.05  # Severe penalty for competing cloud platforms
            if any(k in full_text for k in ("kubernetes", "docker", "triton", "tgi", "vllm", "fastapi")):
                return 0.80
            return 0.50

        # 3. GCP Target
        if target == "gcp":
            if any(k in full_text for k in ("gcp", "vertex_ai", "gke", "cloud_run", "google_cloud")):
                return 1.0
            if any(k in full_text for k in ("aws", "sagemaker", "azure", "azure_ai_foundry")):
                return 0.05  # Severe penalty for competing cloud platforms
            if any(k in full_text for k in ("kubernetes", "docker", "triton", "tgi", "vllm", "fastapi")):
                return 0.80
            return 0.50

        # 4. Local / On-Prem Target
        if target in ("local", "on_prem"):
            if any(k in full_text for k in ("docker", "bentoml", "ollama", "compose", "llama_cpp", "local", "on_prem")):
                return 1.0
            if any(k in full_text for k in ("sagemaker", "azure_ai_foundry", "vertex_ai", "fly_io")):
                return 0.05  # Severe penalty for managed cloud platforms
            if any(k in full_text for k in ("kubernetes", "triton", "fastapi", "chroma", "faiss")):
                return 0.85
            return 0.40

        return 0.70

    # --- 4. Budget Match ---
    @classmethod
    def _calc_budget_match(cls, entry: dict[str, Any], profile: ProjectProfile) -> float:
        """Evaluate candidate pricing efficiency against project budget tier."""
        is_open_source = entry.get("open_source") is True or "open_source" in str(entry.get("path") or "").lower()
        has_free_tier = entry.get("free_tier") or entry.get("has_free_tier")
        cost_val = entry.get("min_monthly_cost_usd") or entry.get("monthly_cost")

        if profile.budget_tier == BudgetTier.FREE_LOW:
            if is_open_source:
                return 1.0
            if has_free_tier:
                return 0.80
            return 0.2

        if profile.budget_tier == BudgetTier.HIGH_UNLIMITED:
            return 0.95

        if isinstance(cost_val, (int, float)) and profile.budget_usd:
            if cost_val <= profile.budget_usd:
                return 0.90
            overrun = cost_val / profile.budget_usd
            return max(0.1, round(1.0 / (1.0 + overrun), 4))

        return 0.75

    # --- 5. Scale Match ---
    @classmethod
    def _calc_scale_match(cls, entry: dict[str, Any], profile: ProjectProfile) -> float:
        """Assess candidate scalability for expected user volume and document counts."""
        tech_name = str(entry.get("technology") or entry.get("name") or "").lower()
        entry_text = str(entry.get("text") or "").lower()

        high_scale_techs = {"milvus", "qdrant", "pinecone", "vllm", "tgi", "sglang", "triton", "kubernetes"}

        if profile.project_scale in (ScaleTier.LARGE, ScaleTier.ENTERPRISE) or profile.document_scale == DocScaleTier.MASSIVE:
            if any(t in tech_name for t in high_scale_techs) or "scale" in entry_text or "distributed" in entry_text:
                return 1.0
            return 0.35

        if profile.project_scale == ScaleTier.MEDIUM:
            return 0.85

        if any(t in tech_name for t in ("chroma", "faiss", "ollama", "llama_cpp")):
            return 1.0
        return 0.80

    # --- 6. Priority Match ---
    @classmethod
    def _calc_priority_match(cls, entry: dict[str, Any], profile: ProjectProfile) -> float:
        """Align candidate features with primary optimization goal (cost, latency, quality, balanced)."""
        p = profile.priority
        text = str(entry.get("text") or "").lower()
        is_open_source = entry.get("open_source") is True or "open_source" in text

        if p == Priority.COST:
            return 1.0 if is_open_source else 0.4

        if p == Priority.LATENCY:
            latency = entry.get("latency_ms") or entry.get("latency")
            if isinstance(latency, (int, float)) and latency < 100:
                return 1.0
            if any(k in text for k in ("fast", "latency", "c++", "rust", "deepseek", "bge")):
                return 0.9
            return 0.5

        if p == Priority.QUALITY:
            quality = entry.get("quality_score") or entry.get("benchmark_score")
            if isinstance(quality, (int, float)) and quality > 0.8:
                return 1.0
            if any(k in text for k in ("claude", "gpt", "pinecone", "qdrant", "sota", "quality")):
                return 0.95
            return 0.6

        return 0.8

    # --- 7. Preferred LLM Match ---
    @classmethod
    def _calc_preferred_llm_match(cls, entry: dict[str, Any], profile: ProjectProfile) -> float:
        """Evaluate integration compatibility with user's preferred foundation model."""
        if not profile.preferred_llm:
            return 0.7

        pref = profile.preferred_llm.strip().lower()
        tech_name = str(entry.get("technology") or entry.get("name") or "").lower()
        text = str(entry.get("text") or "").lower()

        if pref in tech_name or pref in text:
            return 1.0
        return 0.4

    # --- 8. First-Class Constraint Match ---
    @classmethod
    def _calc_constraint_match(cls, entry: dict[str, Any], profile: ProjectProfile) -> float:
        """Treat constraints as first-class ranking signals with hard penalties and rewards."""
        tech_name = str(entry.get("technology") or entry.get("name") or "").lower()
        is_open_source = entry.get("open_source") is True or "open_source" in str(entry.get("path") or "").lower()

        score = 1.0

        if profile.requires_open_source:
            if is_open_source or any(t in tech_name for t in ("chroma", "faiss", "qdrant", "deepseek", "ollama", "bge", "ragas", "docker")):
                score += 0.15
            else:
                score -= 0.55

        if profile.requires_local_execution:
            if is_open_source or any(t in tech_name for t in ("chroma", "faiss", "ollama", "docker", "llama_cpp")):
                score += 0.20
            else:
                score -= 0.45

        if profile.requires_citations:
            if any(t in tech_name for t in ("ragas", "qdrant", "llamaindex", "retriever", "bge")):
                score += 0.25
            else:
                score -= 0.20

        if profile.requires_enterprise_security:
            if any(t in tech_name for t in ("pinecone", "claude", "aws", "azure", "kubernetes", "milvus")):
                score += 0.25
            else:
                score -= 0.25

        return min(1.0, max(0.0, round(score, 4)))

    # --- 9. Metadata Quality ---
    @classmethod
    def _calc_metadata_quality(cls, entry: dict[str, Any]) -> float:
        """Calculate metadata completeness score based on presence of enriched metadata fields."""
        fields = [
            "technology_id", "category", "organization", "license",
            "priority", "update_frequency", "url", "source"
        ]
        present = sum(1 for f in fields if entry.get(f) is not None)
        return round(present / len(fields), 4)

    # --- 10. Documentation Quality ---
    @classmethod
    def _calc_documentation_quality(cls, entry: dict[str, Any]) -> float:
        """Assess documentation depth and source authority."""
        score = 0.5
        if entry.get("url") and str(entry["url"]).startswith("http"):
            score += 0.25
        source = str(entry.get("source") or "").lower()
        if source in ("documentation", "research_papers", "official_docs"):
            score += 0.25
        elif source == "github_repository":
            score += 0.15
        return min(1.0, round(score, 4))

    @classmethod
    def calculate_score(
        cls, entry: dict[str, Any], target: Union[ProjectProfile, DecisionRequest]
    ) -> float:
        """Compute 10 sub-scores and weighted composite score for candidate using ProjectProfile."""
        if isinstance(target, DecisionRequest):
            profile = RequirementAnalyzer.analyze(target)
        else:
            profile = target

        subscores: dict[str, float] = {
            "semantic_similarity": cls._calc_semantic_similarity(entry, profile),
            "domain_match": cls._calc_domain_match(entry, profile),
            "deployment_match": cls._calc_deployment_match(entry, profile),
            "budget_match": cls._calc_budget_match(entry, profile),
            "scale_match": cls._calc_scale_match(entry, profile),
            "priority_match": cls._calc_priority_match(entry, profile),
            "preferred_llm_match": cls._calc_preferred_llm_match(entry, profile),
            "constraint_match": cls._calc_constraint_match(entry, profile),
            "metadata_quality": cls._calc_metadata_quality(entry),
            "documentation_quality": cls._calc_documentation_quality(entry),
        }

        category = str(entry.get("category") or "").lower()

        # Increase deployment_match weight to 35% specifically for 'deployment' category candidates
        if category == "deployment":
            weights = {
                "semantic_similarity": 0.10,
                "domain_match": 0.10,
                "deployment_match": 0.35,  # 35% weight for deployment category!
                "budget_match": 0.10 if profile.budget_tier == BudgetTier.FREE_LOW else 0.05,
                "scale_match": 0.10 if profile.project_scale in (ScaleTier.LARGE, ScaleTier.ENTERPRISE) else 0.05,
                "priority_match": 0.10,
                "preferred_llm_match": 0.0,
                "constraint_match": 0.15 if profile.constraints else 0.05,
                "metadata_quality": 0.025,
                "documentation_quality": 0.025,
            }
        else:
            weights = {
                "semantic_similarity": 0.10,
                "domain_match": 0.15,
                "deployment_match": 0.15,
                "budget_match": 0.15 if profile.budget_tier == BudgetTier.FREE_LOW else 0.05,
                "scale_match": 0.15 if profile.project_scale in (ScaleTier.LARGE, ScaleTier.ENTERPRISE) else 0.05,
                "priority_match": 0.10,
                "preferred_llm_match": 0.10 if profile.preferred_llm else 0.0,
                "constraint_match": 0.20 if profile.constraints else 0.05,
                "metadata_quality": 0.05,
                "documentation_quality": 0.05,
            }

        weighted_sum = sum(subscores[k] * weights[k] for k in subscores)
        weight_sum = sum(weights.values())

        final_score = round(weighted_sum / weight_sum, 4) if weight_sum > 0 else _DEFAULT_NEUTRAL_SCORE
        final_score = min(1.0, max(0.0, final_score))

        entry["subscores"] = subscores
        entry["score"] = final_score
        return final_score

    def score_candidates(
        self,
        request: Union[ProjectProfile, DecisionRequest],
        candidates: dict[str, list[dict[str, Any]]],
    ) -> dict[str, list[dict[str, Any]]]:
        """Score candidate technology entities and return candidates sorted by composite score descending."""
        profile = RequirementAnalyzer.analyze(request) if isinstance(request, DecisionRequest) else request
        scored_candidates: dict[str, list[dict[str, Any]]] = {}

        for category, items in candidates.items():
            scored_items: list[dict[str, Any]] = []

            for item in items:
                item_copy = item.copy()
                self.calculate_score(item_copy, profile)
                scored_items.append(item_copy)

            scored_items.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            scored_candidates[category] = scored_items

        return scored_candidates
