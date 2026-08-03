"""
Architecture comparison engine for Forge platform.

Orchestrates multi-candidate RAG architecture benchmarking comparisons, producing winner
explanations, detailed metric differences, and executive recommendations.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from app.comparison.comparison_models import (
    ComparisonMetadata,
    ComparisonRequest,
    ComparisonResponse,
    ComparisonSummaryDetails,
    RankedArchitecture,
)
from app.comparison.ranking import RankingEngine


class ComparisonEngine:
    """Orchestrates RAG architecture comparisons using RankingEngine."""

    def __init__(self, ranking_engine: Optional[RankingEngine] = None) -> None:
        """Initialize comparison engine with injected dependencies."""
        self.ranking_engine = ranking_engine or RankingEngine()

    @staticmethod
    def _build_summary_text(
        winner: RankedArchitecture,
        runner_up: Optional[RankedArchitecture],
        total_architectures: int,
    ) -> str:
        """Generate high-level text summary of comparison results."""
        if runner_up:
            gap = winner.overall_score - runner_up.overall_score
            return (
                f"Compared {total_architectures} RAG architectures. "
                f"'{winner.architecture_name}' ranked #1 with an overall composite score of {winner.overall_score:.4f}, "
                f"outperforming runner-up '{runner_up.architecture_name}' by +{gap:.4f} points."
            )
        return (
            f"Evaluated 1 architecture: '{winner.architecture_name}' with an overall score of {winner.overall_score:.4f}."
        )

    @staticmethod
    def _build_recommendation_paragraph(
        winner: RankedArchitecture,
        runner_up: Optional[RankedArchitecture],
    ) -> str:
        """Generate short recommendation paragraph detailing winner superiority."""
        if runner_up:
            gap = winner.overall_score - runner_up.overall_score
            return (
                f"{winner.architecture_name} is the recommended architecture for production deployment. "
                f"It achieved an overall composite score of {winner.overall_score:.4f} (+{gap:.4f} higher than {runner_up.architecture_name}), "
                f"demonstrating high factual faithfulness ({winner.faithfulness:.2f}) and an average latency of {winner.average_latency_ms:.0f} ms."
            )
        return (
            f"{winner.architecture_name} is recommended with an overall score of {winner.overall_score:.4f} "
            f"and average latency of {winner.average_latency_ms:.0f} ms."
        )

    @staticmethod
    def _build_recommendation_list(
        winner: RankedArchitecture,
        runner_up: Optional[RankedArchitecture],
    ) -> List[str]:
        """Generate actionable recommendations bullet list."""
        recs = [
            f"Deploy {winner.architecture_name} as the primary RAG architecture.",
            f"Overall comparison score: {winner.overall_score:.4f}.",
            f"Faithfulness: {winner.faithfulness:.2f} | Answer Relevancy: {winner.answer_relevancy:.2f}.",
            f"Average latency: {winner.average_latency_ms:.0f} ms | Quality Gate Pass Rate: {winner.success_rate * 100:.0f}%.",
        ]
        if runner_up:
            recs.append(f"Runner-up alternative: {runner_up.architecture_name} (score: {runner_up.overall_score:.4f}).")
        return recs

    def compare(self, request: ComparisonRequest) -> ComparisonResponse:
        """Execute multi-architecture comparison and generate comprehensive evaluation response."""
        comparison_id = str(uuid4())
        created_at = datetime.utcnow()

        rankings = self.ranking_engine.rank(
            candidates=request.architectures,
            goal=request.optimization_goal,
            strategy=request.ranking_strategy,
        )

        winner = rankings[0]
        runner_up = rankings[1] if len(rankings) > 1 else None

        # Compute metric differences between winner and runner-up
        metric_diffs: Dict[str, float] = {}
        score_diff = 0.0
        latency_diff_ms = 0.0

        if runner_up:
            score_diff = round(winner.overall_score - runner_up.overall_score, 4)
            latency_diff_ms = round(runner_up.average_latency_ms - winner.average_latency_ms, 2)
            metric_diffs = {
                "faithfulness": round(winner.faithfulness - runner_up.faithfulness, 4),
                "answer_relevancy": round(winner.answer_relevancy - runner_up.answer_relevancy, 4),
                "context_precision": round(winner.context_precision - runner_up.context_precision, 4),
                "context_recall": round(winner.context_recall - runner_up.context_recall, 4),
            }

        comparison_summary = ComparisonSummaryDetails(
            best_architecture=winner.architecture_name,
            runner_up=runner_up.architecture_name if runner_up else None,
            score_difference=score_diff,
            metric_differences=metric_diffs,
            latency_difference_ms=latency_diff_ms,
            recommendation=self._build_recommendation_paragraph(winner, runner_up),
        )

        metadata = ComparisonMetadata(
            comparison_id=comparison_id,
            created_at=created_at,
            ranking_strategy=request.ranking_strategy.value if hasattr(request.ranking_strategy, "value") else str(request.ranking_strategy),
            optimization_goal=request.optimization_goal.value if hasattr(request.optimization_goal, "value") else str(request.optimization_goal),
            number_of_architectures=len(rankings),
        )

        summary_text = self._build_summary_text(winner, runner_up, len(rankings))
        rec_paragraph = self._build_recommendation_paragraph(winner, runner_up)
        recommendations = self._build_recommendation_list(winner, runner_up)

        return ComparisonResponse(
            comparison_id=comparison_id,
            comparison_name=request.comparison_name,
            winner=winner,
            runner_up=runner_up,
            rankings=rankings,
            summary=summary_text,
            comparison_summary=comparison_summary,
            recommendation_paragraph=rec_paragraph,
            recommendations=recommendations,
            metadata=metadata,
            compared_at=created_at,
        )