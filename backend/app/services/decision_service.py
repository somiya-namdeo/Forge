"""Decision service module orchestrating the AI architecture recommendation pipeline."""

from datetime import datetime, timezone
import statistics
import time

from app.decision.constraint_matcher import ConstraintMatcher
from app.decision.explanation_engine import ExplanationEngine
from app.decision.recommendation_engine import RecommendationEngine
from app.decision.requirement_analyzer import RequirementAnalyzer
from app.decision.retriever import KnowledgeRetriever
from app.decision.scoring_engine import ScoringEngine
from app.schemas.decision import DecisionRequest, DecisionResponse


class DecisionService:
    """Service orchestrating AI architecture candidate retrieval, matching, scoring, and recommendation."""

    def __init__(
        self,
        retriever: KnowledgeRetriever,
        constraint_matcher: ConstraintMatcher,
        scoring_engine: ScoringEngine,
        recommendation_engine: RecommendationEngine,
        explanation_engine: ExplanationEngine,
    ) -> None:
        """Initialize DecisionService with injected pipeline dependencies."""
        self.retriever = retriever
        self.constraint_matcher = constraint_matcher
        self.scoring_engine = scoring_engine
        self.recommendation_engine = recommendation_engine
        self.explanation_engine = explanation_engine

    def recommend(self, request: DecisionRequest) -> DecisionResponse:
        """Execute complete recommendation pipeline using RequirementAnalyzer ProjectProfile."""
        # 1. Convert raw DecisionRequest into structured ProjectProfile
        profile = RequirementAnalyzer.analyze(request)

        # 2. Retrieve knowledge base candidates (measure retrieval time)
        t_ret_start = time.perf_counter()
        raw_candidates = self.retriever.retrieve(request)
        t_ret_end = time.perf_counter()
        retrieval_time_ms = round((t_ret_end - t_ret_start) * 1000, 2)

        # 3. Apply explicit user constraints & calculate ranking metrics (measure ranking time)
        t_rank_start = time.perf_counter()
        filtered_candidates = self.constraint_matcher.apply_constraints(
            request, raw_candidates
        )

        # Count total technologies considered and categories processed
        technologies_considered = sum(len(items) for items in filtered_candidates.values())
        categories_processed = len(filtered_candidates)

        # 4. Compute deterministic scores using ProjectProfile
        scored_candidates = self.scoring_engine.score_candidates(
            profile, filtered_candidates
        )

        # 5. Generate candidate recommendations with calibrated confidence
        base_recommendations = self.recommendation_engine.recommend(scored_candidates)

        # 6. Synthesize deterministic rationale explanations using ProjectProfile
        final_recommendations = self.explanation_engine.generate(
            base_recommendations, profile
        )
        t_rank_end = time.perf_counter()
        ranking_time_ms = round((t_rank_end - t_rank_start) * 1000, 2)

        # 7. Calculate overall confidence arithmetic mean
        if final_recommendations:
            confidences = [item.confidence for item in final_recommendations]
            overall_confidence = round(float(statistics.fmean(confidences)), 4)
        else:
            overall_confidence = 0.0

        # 8. Construct output DecisionResponse & pipeline_statistics
        generated_at = datetime.now(timezone.utc)
        count = len(final_recommendations)
        summary = f"Generated architecture recommendations for {count} component categories."

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
        }

        pipeline_statistics: dict[str, Any] = {
            "technologies_considered": technologies_considered,
            "categories_processed": categories_processed,
            "average_confidence": overall_confidence,
            "knowledge_base_version": "1.0.0",
            "retrieval_time_ms": max(1, int(retrieval_time_ms)),
            "ranking_time_ms": max(1, int(ranking_time_ms)),
        }

        return DecisionResponse(
            recommendations=final_recommendations,
            summary=summary,
            overall_confidence=overall_confidence,
            generated_at=generated_at,
            metadata=metadata,
            pipeline_statistics=pipeline_statistics,
        )
