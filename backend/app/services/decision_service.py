"""Decision service module orchestrating the AI architecture recommendation pipeline."""

from datetime import datetime, timezone
import statistics

from app.decision.constraint_matcher import ConstraintMatcher
from app.decision.explanation_engine import ExplanationEngine
from app.decision.recommendation_engine import RecommendationEngine
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
        """Execute complete recommendation pipeline and return structured DecisionResponse."""
        # 1. Retrieve knowledge base candidates
        raw_candidates = self.retriever.retrieve(request)

        # 2. Apply explicit user constraints
        filtered_candidates = self.constraint_matcher.apply_constraints(
            request, raw_candidates
        )

        # 3. Compute deterministic scores
        scored_candidates = self.scoring_engine.score_candidates(
            request, filtered_candidates
        )

        # 4. Generate candidate recommendations
        base_recommendations = self.recommendation_engine.recommend(scored_candidates)

        # 5. Synthesize deterministic rationale explanations
        final_recommendations = self.explanation_engine.generate(base_recommendations)

        # 6. Calculate overall confidence arithmetic mean
        if final_recommendations:
            confidences = [item.confidence for item in final_recommendations]
            overall_confidence = round(float(statistics.fmean(confidences)), 4)
        else:
            overall_confidence = 0.0

        # 7. Construct output DecisionResponse
        generated_at = datetime.now(timezone.utc)
        count = len(final_recommendations)
        summary = f"Generated architecture recommendations for {count} component categories."

        metadata: dict[str, str] = {
            "pipeline_version": "1.0.0",
            "recommendation_count": str(count),
            "project_name": request.project_name,
            "deployment_target": request.deployment_target.value,
            "priority": request.priority.value,
        }

        return DecisionResponse(
            recommendations=final_recommendations,
            summary=summary,
            overall_confidence=overall_confidence,
            generated_at=generated_at,
            metadata=metadata,
        )
