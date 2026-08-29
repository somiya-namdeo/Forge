"""Explanation engine module for generating project-specific, evidence-backed recommendation rationale."""

import logging
from typing import Any, Optional, Union

from app.decision.requirement_analyzer import ProjectProfile, RequirementAnalyzer
from app.schemas.decision import AlternativeDetail, DecisionRequest, RecommendationItem

logger = logging.getLogger(__name__)


class ExplanationEngine:
    """Engine responsible for synthesizing factor-driven rationale, score breakdowns, evidence, and alternative trade-off analysis."""

    def __init__(self) -> None:
        """Initialize ExplanationEngine with LLM service singleton."""
        from app.services.llm_service import LLMService
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

        why_selected = f"{tech_name} aligns well with {profile.priority.value} priorities, scoring highest among eligible candidates in {top_factors_str}."
        
        if profile.requires_privacy:
            tech_lower = tech_name.lower()
            is_cloud_api = any(c in tech_lower for c in ("claude", "gpt", "openai", "anthropic", "gemini", "cohere"))
            if is_cloud_api:
                why_selected += " Note: Requires dedicated private VPC endpoints or zero-data-retention agreements to satisfy strict privacy constraints."

        trade_off = "No major trade-offs."
        if runner_up:
            runner_subscores = runner_up.get("subscores", {})
            trade_offs: list[str] = []
            if runner_subscores.get("constraint_match", 1.0) < subscores.get("constraint_match", 1.0):
                trade_offs.append("less constraint alignment")
            if runner_subscores.get("deployment_match", 1.0) < subscores.get("deployment_match", 1.0):
                trade_offs.append(f"lower compatibility with {profile.deployment.value}")
            if runner_subscores.get("budget_match", 1.0) < subscores.get("budget_match", 1.0):
                trade_offs.append("higher cost")
            if runner_subscores.get("scale_match", 1.0) < subscores.get("scale_match", 1.0):
                trade_offs.append("lower scale capacity")
            if trade_offs:
                trade_off = f"Slightly {trade_offs[0]}."

        alternative = "None available."
        if runner_up:
            runner_up_name = runner_up.get("display_name") or runner_up.get("name") or runner_up.get("technology") or "Alternative"
            top_s = float(top_candidate.get("score", 0.0))
            run_s = float(runner_up.get("score", 0.0))
            score_diff = round(max(0.0, top_s - run_s) * 100, 1)
            alternative = f"{runner_up_name} — rejected due to {score_diff}% lower score."
            
        return f"Why selected: {why_selected} Trade-off: {trade_off} Alternative: {alternative}"

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
                        "ragas", "flashrank", "bge", "llama", "mistral", "deepseek", "qwen", "ollama"
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

    def _batch_enhance_reasons_with_llm(
        self,
        base_reasons: dict[str, str],
        recommendations: list[RecommendationItem],
        profile: ProjectProfile,
    ) -> dict[str, str]:
        """Perform ONE single Groq API completion request to enhance explanations for all recommendations in batch.

        Expects a JSON response mapping category names to enhanced explanation strings.
        If parsing fails or hallucination validation triggers, automatically returns base_reasons without retrying.
        """
        import json

        if not base_reasons:
            return base_reasons

        # 1. Compact Project Context for the LLM
        # Included to prevent the LLM from guessing missing architectural constraints
        project_context = {
            "deployment_target": profile.deployment.value if profile.deployment else None,
            "local_execution_required": profile.requires_local_execution,
            "open_source_required": profile.requires_open_source,
            "budget_tier": profile.budget_tier.value if profile.budget_tier else None,
            "project_scale": profile.project_scale.value if profile.project_scale else None,
            "document_scale": profile.document_scale.value if profile.document_scale else None,
            "latency_priority": profile.requires_low_latency,
            "compliance_requirements": {
                "enterprise_security": profile.requires_enterprise_security,
                "privacy": profile.requires_privacy,
                "high_availability": profile.requires_high_availability,
                "citations": profile.requires_citations,
            }
        }

        items_payload = []
        for item in recommendations:
            cat = item.category
            items_payload.append({
                "category": cat,
                "recommended": item.recommended,
                "base_explanation": base_reasons.get(cat, "")
            })

        prompt = f"""You are an AI systems architect.

Rewrite the following architectural recommendation explanations to be more natural, professional, and concise.

- Rewrite only.
- Preserve all technical meaning.
- KEEP TEXT EXTREMELY BRIEF (maximum 2-3 sentences total, under 40 words per category) to prevent token limits.
- Do not repeat project requirements.
- Format the explanation exactly as:
  Why selected: <short explanation> Trade-off: <one sentence> Alternative: <Technology> — rejected because ...
- Never invent new facts or technologies.
- Return ONLY a valid JSON object mapping each category name to its enhanced explanation string.

Project Context:
{json.dumps(project_context)}

Input Recommendations:
{json.dumps(items_payload)}

JSON Output Format:
{{
  "category_name": "Enhanced explanation text..."
}}
"""
        try:
            raw_response = self._llm.reason(prompt, json_mode=True).strip()
            if raw_response.startswith("```"):
                lines = raw_response.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                raw_response = "\n".join(lines).strip()

            parsed = json.loads(raw_response)
            if isinstance(parsed, dict) and parsed:
                enhanced: dict[str, str] = {}
                
                # 4. Validate output for hallucinations
                # Reject enhanced explanations introducing new cloud/enterprise terms
                restricted_terms = ["aws", "azure", "gcp", "enterprise", "hipaa", "soc2", "gdpr", "kubernetes"]
                context_str = json.dumps(project_context).lower()
                
                for cat, base_txt in base_reasons.items():
                    val = parsed.get(cat) or parsed.get(cat.lower())
                    if val and isinstance(val, str) and val.strip():
                        val_str = val.strip()
                        val_lower = val_str.lower()
                        base_lower = base_txt.lower()
                        
                        # Check for hallucinations
                        is_hallucinated = False
                        for term in restricted_terms:
                            if term in val_lower and term not in base_lower and term not in context_str:
                                is_hallucinated = True
                                break
                                
                        if is_hallucinated:
                            logger.warning("Hallucination detected in category '%s'. Falling back to base reason.", cat)
                            enhanced[cat] = base_txt
                        else:
                            enhanced[cat] = val_str
                    else:
                        enhanced[cat] = base_txt
                return enhanced
        except Exception as exc:
            logger.warning("Batch LLM explanation enhancement failed or JSON parse error. Using deterministic base reasons: %s", exc)

        return base_reasons

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

        base_reasons: dict[str, str] = {}
        item_data_map: dict[str, dict[str, Any]] = {}

        for item in recommendations:
            top_candidate = getattr(item, "_top_candidate", {}) or {}
            runner_up = getattr(item, "_runner_up", None)
            alt_candidates = getattr(item, "_alternative_candidates", []) or ([] if not runner_up else [runner_up])

            base_reason = self._build_project_specific_reason(
                item=item,
                top_candidate=top_candidate,
                runner_up=runner_up,
                profile=profile,
            )
            base_reasons[item.category] = base_reason
            item_data_map[item.category] = {
                "top_candidate": top_candidate,
                "runner_up": runner_up,
                "alt_candidates": alt_candidates,
            }

        enhanced_reasons = self._batch_enhance_reasons_with_llm(base_reasons, recommendations, profile)

        for item in recommendations:
            category_data = item_data_map.get(item.category, {})
            top_candidate = category_data.get("top_candidate", {})
            runner_up = category_data.get("runner_up")
            alt_candidates = category_data.get("alt_candidates", [])
            subscores = top_candidate.get("subscores", {})
            top_score = float(top_candidate.get("score", item.confidence))

            base_reason = base_reasons.get(item.category, item.reason)
            enriched_reason = enhanced_reasons.get(item.category, base_reason)

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
