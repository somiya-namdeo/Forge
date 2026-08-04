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


import logging
from typing import Any

logger = logging.getLogger(__name__)


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
        t_pipeline_start = time.perf_counter()

        # Stage 1: Requirement Analysis & Domain Detection
        t_req_start = time.perf_counter()
        profile = RequirementAnalyzer.analyze(request)
        t_req_end = time.perf_counter()
        req_analysis_ms = round((t_req_end - t_req_start) * 1000, 2)

        # Stage 2: Retrieve knowledge base candidates from Qdrant
        t_ret_start = time.perf_counter()
        raw_candidates = self.retriever.retrieve(request)
        t_ret_end = time.perf_counter()
        retrieval_time_ms = round((t_ret_end - t_ret_start) * 1000, 2)

        # Stage 3: Candidate Filtering
        t_filt_start = time.perf_counter()
        filtered_candidates = self.constraint_matcher.apply_constraints(
            request, raw_candidates
        )
        t_filt_end = time.perf_counter()
        filtering_time_ms = round((t_filt_end - t_filt_start) * 1000, 2)

        technologies_considered = sum(len(items) for items in filtered_candidates.values())
        categories_processed = len(filtered_candidates)

        # Stage 4: Compute deterministic candidate subscores
        t_score_start = time.perf_counter()
        scored_candidates = self.scoring_engine.score_candidates(
            profile, filtered_candidates
        )
        t_score_end = time.perf_counter()
        scoring_time_ms = round((t_score_end - t_score_start) * 1000, 2)

        # Stage 5: Select winner candidates per category & dynamic confidence
        t_rec_start = time.perf_counter()
        base_recommendations = self.recommendation_engine.recommend(scored_candidates)
        t_rec_end = time.perf_counter()
        rec_gen_ms = round((t_rec_end - t_rec_start) * 1000, 2)

        # Stage 6: Consolidated LLM Rationale Synthesis & Alternative Analysis
        t_exp_start = time.perf_counter()
        final_recommendations = self.explanation_engine.generate(
            base_recommendations, profile
        )
        t_exp_end = time.perf_counter()
        explanation_time_ms = round((t_exp_end - t_exp_start) * 1000, 2)

        # Stage 7: Response Construction & Arithmetic Mean Confidence
        t_resp_start = time.perf_counter()
        if final_recommendations:
            confidences = [item.confidence for item in final_recommendations]
            overall_confidence = round(float(statistics.fmean(confidences)), 4)
        else:
            overall_confidence = 0.0

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

        ranking_time_ms = round(filtering_time_ms + scoring_time_ms, 2)

        pipeline_statistics: dict[str, Any] = {
            "technologies_considered": technologies_considered,
            "categories_processed": categories_processed,
            "average_confidence": overall_confidence,
            "knowledge_base_version": "1.0.0",
            "retrieval_time_ms": max(1, int(retrieval_time_ms)),
            "ranking_time_ms": max(1, int(ranking_time_ms)),
        }

        t_resp_end = time.perf_counter()
        serialization_ms = round((t_resp_end - t_resp_start) * 1000, 2)
        total_pipeline_ms = round((time.perf_counter() - t_pipeline_start) * 1000, 2)

        logger.info("\nDecision Pipeline Latency Profile:")
        logger.info(f"Requirement Analysis ............ {req_analysis_ms:>7.2f} ms")
        logger.info(f"Qdrant Retrieval ............... {retrieval_time_ms:>7.2f} ms")
        logger.info(f"Candidate Filtering .............. {filtering_time_ms:>7.2f} ms")
        logger.info(f"Candidate Ranking .............. {scoring_time_ms:>7.2f} ms")
        logger.info(f"Recommendation Generation ...... {rec_gen_ms:>7.2f} ms")
        logger.info(f"Explanation Generation ......... {explanation_time_ms:>7.2f} ms")
        logger.info(f"Response Serialization .......... {serialization_ms:>7.2f} ms")
        logger.info(f"Total Pipeline Latency ......... {total_pipeline_ms:>7.2f} ms\n")

        return DecisionResponse(
            recommendations=final_recommendations,
            summary=summary,
            overall_confidence=overall_confidence,
            generated_at=generated_at,
            metadata=metadata,
            pipeline_statistics=pipeline_statistics,
        )
