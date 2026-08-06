"""Decision engine module for generating project-specific reasoning."""

import statistics
import time
from datetime import datetime, timezone
from typing import Any

from app.decision.explanation_engine import ExplanationEngine
from app.decision.requirement_analyzer import RequirementAnalyzer
from app.schemas.decision import DecisionRequest, DecisionResponse, RecommendationItem


class DecisionEngine:
    """The Decision Engine receives Recommendation Engine outputs and explains WHY recommendations won."""

    def __init__(self) -> None:
        """Initialize DecisionEngine."""
        self.explanation_engine = ExplanationEngine()

    def run(
        self,
        request: DecisionRequest,
        base_recommendations: list[RecommendationItem],
        pipeline_statistics: dict[str, Any] = None,
    ) -> DecisionResponse:
        """Generate full DecisionResponse from base recommendations."""
        t_start = time.perf_counter()

        profile = RequirementAnalyzer.analyze(request)
        final_recommendations = self.explanation_engine.generate(base_recommendations, profile)

        if final_recommendations:
            confidences = [item.confidence for item in final_recommendations]
            overall_confidence = round(float(statistics.fmean(confidences)), 4)
        else:
            overall_confidence = 0.0

        generated_at = datetime.now(timezone.utc)
        count = len(final_recommendations)
        summary = f"Generated architecture recommendations for {count} component categories."

        total_estimated_cost = 0.0
        total_estimated_latency = 0.0
        cost_available = False
        latency_available = False

        for rec in final_recommendations:
            entry = getattr(rec, "_top_candidate", {})
            cost_val = entry.get("min_monthly_cost_usd") or entry.get("monthly_cost") or entry.get("cost")
            if cost_val is not None and isinstance(cost_val, (int, float)):
                total_estimated_cost += float(cost_val)
                cost_available = True
                
            latency_val = entry.get("latency_ms") or entry.get("latency")
            if latency_val is not None and isinstance(latency_val, (int, float)):
                total_estimated_latency += float(latency_val)
                latency_available = True

        metadata: dict[str, str] = {
            "pipeline_version": "1.0.0",
            "recommendation_count": str(count),
            "project_name": request.project_name,
            "domain": profile.domain.value,
            "project_scale": profile.project_scale.value,
            "document_scale": profile.document_scale.value,
            "budget_tier": profile.budget_tier.value,
            "deployment_target": request.deployment_target.value,
            "priority": request.priority.value,
            "estimated_cost": f"${int(total_estimated_cost)}/mo" if cost_available else "Unknown",
            "estimated_latency": f"{int(total_estimated_latency)}ms p95" if latency_available else "Unknown",
        }

        stats = pipeline_statistics or {}
        if "categories_processed" not in stats:
            stats["categories_processed"] = count
        stats["average_confidence"] = overall_confidence

        return DecisionResponse(
            recommendations=final_recommendations,
            summary=summary,
            overall_confidence=overall_confidence,
            generated_at=generated_at,
            metadata=metadata,
            pipeline_statistics=stats,
        )
