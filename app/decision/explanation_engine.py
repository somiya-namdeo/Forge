"""Explanation engine module for generating project-specific, evidence-backed recommendation rationale."""

import logging
from typing import Any, Dict, List, Optional, Union

from app.decision.requirement_analyzer import ProjectProfile, RequirementAnalyzer
from app.schemas.decision import AlternativeDetail, DecisionRequest, RecommendationItem
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ExplanationEngine:
    """Engine responsible for synthesizing factor-driven rationale, score breakdowns, evidence, and alternative trade-off analysis."""

    def __init__(self) -> None:
        """Initialize ExplanationEngine with LLM service singleton."""
        self._llm = LLMService()

    @classmethod
    def _map_confidence_level(cls, confidence: float) -> str:
        """Convert numeric confidence score into human-readable label."""
        if confidence >= 0.90:
            return "Very High"
        if confidence >= 0.75:
            return "High"
        if confidence >= 0.60:
            return "Medium"
        if confidence >= 0.40:
            return "Low"
        return "Weak"

    @classmethod
    def _extract_evidence_metadata(cls, candidate: dict[str, Any]) -> dict[str, Any]:
        """Extract evidence metadata directly from enriched knowledge base candidate dictionary."""
        tech_id = str(
            candidate.get("technology_id")
            or candidate.get("id")
            or candidate.get("technology")
            or candidate.get("name")
            or "unknown"
        ).lower()

        return {
            "technology_id": tech_id,
            "organization": str(candidate.get("organization") or "Community / Open Source"),
            "license": str(candidate.get("license") or "Permissive / Open Source"),
            "source": str(candidate.get("source") or "official_docs"),
            "url": str(candidate.get("url") or "https://forge.ai/knowledge_base"),
            "metadata_version": "1.0.0",
            "last_updated": "2026-08",
        }

    @classmethod
    def _build_score_breakdown(
        cls, subscores: dict[str, float], overall_score: float
    ) -> dict[str, float]:
        """Build individual score breakdown dictionary directly from ScoringEngine subscores."""
        return {
            "deployment_fit": round(subscores.get("deployment_match", 0.70), 2),
            "constraint_match": round(subscores.get("constraint_match", 0.70), 2),
            "domain_fit": round(subscores.get("domain_match", 0.70), 2),
            "metadata_quality": round(subscores.get("metadata_quality", 0.70), 2),
            "documentation_quality": round(subscores.get("documentation_quality", 0.70), 2),
            "cost_efficiency": round(subscores.get("budget_match", 0.70), 2),
            "throughput_scalability": round(subscores.get("scale_match", 0.70), 2),
            "overall": round(overall_score, 2),
        }

    @classmethod
    def _build_decision_trace(cls, profile: ProjectProfile) -> list[str]:
        """Dynamically generate decision trace list from ProjectProfile requirements."""
        trace: list[str] = [
            f"Deployment target: {profile.deployment.value.capitalize()}",
            f"Priority: {profile.priority.value.capitalize()}",
            f"Budget tier: {profile.budget_tier.value.replace('_', ' ').title()}",
            f"{profile.domain.value.capitalize()} domain detected",
        ]

        if profile.expected_scale > 0:
            trace.append(f"User scale: {profile.project_scale.value} ({profile.expected_scale:,} users)")
        if profile.document_count > 0:
            trace.append(f"Document collection: {profile.document_scale.value} ({profile.document_count:,} docs)")
        if profile.requires_citations:
            trace.append("Citation support required")
        if profile.requires_open_source:
            trace.append("Open source constraint active")
        if profile.requires_local_execution:
            trace.append("Local execution constraint active")
        if profile.requires_enterprise_security:
            trace.append("Enterprise security compliance required")

        return trace

    @classmethod
    def _build_metadata_used(cls, candidate: dict[str, Any], profile: ProjectProfile) -> list[str]:
        """Construct list of metadata fields that influenced the candidate ranking."""
        used: list[str] = [
            "deployment_targets",
            "supported_domains",
            "constraints",
            "priority_score",
            "documentation_quality",
            "cost",
            "throughput",
            "license",
        ]
        if profile.preferred_llm:
            used.append("preferred_llm")
        if profile.budget_usd is not None:
            used.append("budget_usd")
        return used

    @classmethod
    def _get_top_scoring_factors(cls, subscores: dict[str, float], top_n: int = 3) -> list[str]:
        """Identify the highest scoring subscore factors for candidate rationale synthesis."""
        factor_labels = {
            "semantic_similarity": "semantic relevance",
            "domain_match": "domain fit",
            "deployment_match": "deployment compatibility",
            "budget_match": "cost efficiency",
            "scale_match": "throughput scalability",
            "priority_match": "priority alignment",
            "preferred_llm_match": "foundation model integration",
            "constraint_match": "constraint adherence",
        }
        sorted_factors = sorted(subscores.items(), key=lambda x: x[1], reverse=True)
        return [factor_labels.get(f[0], f[0]) for f in sorted_factors[:top_n] if f[1] >= 0.70]

    @classmethod
    def _build_project_specific_reason(
        cls,
        item: RecommendationItem,
        top_candidate: dict[str, Any],
        runner_up: Optional[dict[str, Any]],
        profile: ProjectProfile,
    ) -> str:
        """Construct factor-driven rationale citing top subscores, metrics, and alternative trade-offs."""
        tech_name = item.recommended
        category = item.category
        subscores = top_candidate.get("subscores", {})

        top_factors = cls._get_top_scoring_factors(subscores)
        top_factors_str = ", ".join(top_factors) if top_factors else "overall suitability"

        context_parts: list[str] = []
        if profile.priority:
            context_parts.append(f"prioritizes {profile.priority.value}")
        if profile.deployment:
            context_parts.append(f"targets {profile.deployment.value} deployment")
        if profile.constraints:
            context_parts.append(f"requires {', '.join(profile.constraints[:2])}")
        if profile.document_count > 0:
            context_parts.append(f"indexes approximately {profile.document_count:,} documents")

        context_clause = ", ".join(context_parts) if context_parts else "specified architectural requirements"

        sentence1 = (
            f"Selected {tech_name} for {category} because your project {context_clause}. "
            f"This technology scored highest in {top_factors_str}."
        )

        sentence2 = ""
        if runner_up:
            runner_up_name = runner_up.get("display_name") or runner_up.get("name") or runner_up.get("technology") or "Alternative"
            runner_subscores = runner_up.get("subscores", {})

            trade_offs: list[str] = []
            if runner_subscores.get("constraint_match", 1.0) < subscores.get("constraint_match", 1.0):
                trade_offs.append("less alignment with project constraints (e.g. open source or local execution)")
            if runner_subscores.get("deployment_match", 1.0) < subscores.get("deployment_match", 1.0):
                trade_offs.append(f"lower deployment compatibility with {profile.deployment.value}")
            if runner_subscores.get("budget_match", 1.0) < subscores.get("budget_match", 1.0):
                trade_offs.append("higher estimated operating cost")
            if runner_subscores.get("scale_match", 1.0) < subscores.get("scale_match", 1.0):
                trade_offs.append("lower scale/throughput capacity")

            if trade_offs:
                sentence2 = f" Alternative '{runner_up_name}' ranked lower due to {', '.join(trade_offs)}."
            else:
                top_s = float(top_candidate.get("score", 0.0))
                run_s = float(runner_up.get("score", 0.0))
                score_diff = round(max(0.0, top_s - run_s) * 100, 1)
                sentence2 = f" Alternative '{runner_up_name}' ranked second with a {score_diff}% score margin."

        return sentence1 + sentence2

    @classmethod
    def _build_alternative_analysis(
        cls,
        alternatives: list[str],
        alt_candidates: list[dict[str, Any]],
        top_candidate: dict[str, Any],
        profile: ProjectProfile,
    ) -> list[AlternativeDetail]:
        """Construct structured AlternativeDetail list with metadata-backed trade-offs for each alternative."""
        analysis: list[AlternativeDetail] = []
        top_subscores = top_candidate.get("subscores", {})
        top_score = float(top_candidate.get("score", 0.0))

        for idx, alt_name in enumerate(alternatives):
            cand = alt_candidates[idx] if idx < len(alt_candidates) else None
            reason_parts: list[str] = []

            if cand:
                cand_sub = cand.get("subscores", {})
                cand_score = float(cand.get("score", 0.0))
                lic_str = str(cand.get("license", "")).lower()
                tech_str = (str(cand.get("technology") or "") + " " + str(cand.get("name") or "")).lower()
                
                is_open = (
                    cand.get("open_source") is True
                    or any(w in lic_str for w in ("open", "apache", "mit", "bsd", "gpl", "lgpl", "agpl", "community"))
                    or any(t in tech_str for t in (
                        "chroma", "milvus", "qdrant", "weaviate", "faiss", "langchain", "llamaindex", "haystack",
                        "deepeval", "ragas", "flashrank", "bge", "llama", "mistral", "deepseek", "qwen", "ollama"
                    ))
                )

                # 1. Constraint & Open Source / Privacy Tradeoffs
                if profile.requires_open_source and not is_open:
                    reason_parts.append(f"{alt_name} is proprietary software, violating open-source constraints")
                elif profile.requires_local_execution and not (is_open or "local" in str(cand.get("path", "")).lower()):
                    reason_parts.append(f"{alt_name} lacks native local/on-prem execution support")
                elif cand_sub.get("constraint_match", 1.0) < top_subscores.get("constraint_match", 1.0):
                    reason_parts.append(f"Lower adherence to project constraints compared to top choice")

                # 2. Deployment Target Fit
                if cand_sub.get("deployment_match", 1.0) < top_subscores.get("deployment_match", 1.0):
                    reason_parts.append(f"Reduced compatibility with {profile.deployment.value} infrastructure")

                # 3. Budget & Cost Efficiency
                if cand_sub.get("budget_match", 1.0) < top_subscores.get("budget_match", 1.0):
                    reason_parts.append("Higher estimated monthly operating cost")

                # 4. Scale & Throughput
                if cand_sub.get("scale_match", 1.0) < top_subscores.get("scale_match", 1.0):
                    reason_parts.append("Lower scale and throughput capacity for large document indexing")

                # 5. Domain Specialization
                if cand_sub.get("domain_match", 1.0) < top_subscores.get("domain_match", 1.0):
                    reason_parts.append(f"Less specialized domain fit for {profile.domain.value} applications")

                # 6. Primary Priority Optimization
                if cand_sub.get("priority_match", 1.0) < top_subscores.get("priority_match", 1.0):
                    reason_parts.append(f"Lower alignment with {profile.priority.value} optimization priority")

                # Fallback to score margin if no subscore delta triggered
                if not reason_parts:
                    margin = round(max(0.0, top_score - cand_score) * 100, 1)
                    reason_parts.append(f"Lower overall composite suitability score ({margin}% score margin)")
            else:
                reason_parts.append("Lower overall composite suitability score")

            reason_str = f"{'; '.join(reason_parts)}."
            analysis.append(AlternativeDetail(name=alt_name, reason=reason_str))

        return analysis

    def _enhance_reason_with_llm(
        self,
        reason: str,
        item: RecommendationItem,
    ) -> str:
        """Use the LLM to improve the readability of the recommendation reason."""
        prompt = f"""
You are an AI systems architect.

Rewrite the following recommendation explanation to be more natural,
professional, and concise.

Rules:
- Keep the same meaning.
- Do not invent new facts.
- Do not change the recommendation.
- Mention trade-offs if already present.
- Return only the rewritten explanation.

Recommendation:
{item.recommended}

Original Explanation:
{reason}
"""
        try:
            return self._llm.reason(prompt)
        except Exception as exc:
            logger.warning("LLM explanation enhancement failed, falling back to deterministic reason: %s", exc)
            return reason

    def generate(
        self,
        recommendations: list[RecommendationItem],
        request: Optional[Union[ProjectProfile, DecisionRequest]] = None,
    ) -> list[RecommendationItem]:
        """Enrich RecommendationItems with evidence, score breakdowns, decision traces, and alternative analysis."""
        if not request:
            return recommendations

        profile = RequirementAnalyzer.analyze(request) if isinstance(request, DecisionRequest) else request
        final_items: list[RecommendationItem] = []

        for item in recommendations:
            top_candidate = getattr(item, "_top_candidate", {}) or {}
            runner_up = getattr(item, "_runner_up", None)
            alt_candidates = getattr(item, "_alternative_candidates", []) or ([] if not runner_up else [runner_up])
            subscores = top_candidate.get("subscores", {})
            top_score = float(top_candidate.get("score", item.confidence))

            base_reason = self._build_project_specific_reason(
                item=item,
                top_candidate=top_candidate,
                runner_up=runner_up,
                profile=profile,
            )

            enriched_reason = self._enhance_reason_with_llm(base_reason, item)

            confidence_label = self._map_confidence_level(item.confidence)
            evidence_dict = self._extract_evidence_metadata(top_candidate)
            score_breakdown_dict = self._build_score_breakdown(subscores, top_score)
            decision_trace_list = self._build_decision_trace(profile)
            metadata_used_list = self._build_metadata_used(top_candidate, profile)
            alternative_analysis_list = self._build_alternative_analysis(
                item.alternatives, alt_candidates, top_candidate, profile
            )

            enriched_item = RecommendationItem(
                category=item.category,
                recommended=item.recommended,
                confidence=item.confidence,
                confidence_level=confidence_label,
                reason=enriched_reason,
                alternatives=item.alternatives,
                alternative_analysis=alternative_analysis_list,
                score_breakdown=score_breakdown_dict,
                decision_trace=decision_trace_list,
                evidence=evidence_dict,
                metadata_used=metadata_used_list,
            )
            final_items.append(enriched_item)

        return final_items
