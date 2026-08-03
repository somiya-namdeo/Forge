"""
Comparison report builder for Forge architecture comparison.
"""

from typing import Any, Dict
from app.comparison.comparison_models import ComparisonResponse


class ComparisonReportBuilder:
    """Builds human-readable structured comparison reports."""

    def build_report(
        self,
        response: ComparisonResponse,
    ) -> Dict[str, Any]:
        """Generate structured comparison report dictionary payload."""
        winner = response.winner
        runner_up = response.runner_up

        return {
            "comparison_id": response.comparison_id,
            "comparison_name": response.comparison_name,
            "best_architecture": winner.architecture_name,
            "runner_up": runner_up.architecture_name if runner_up else None,
            "winner_details": {
                "architecture_id": winner.architecture_id,
                "overall_score": winner.overall_score,
                "benchmark_score": winner.benchmark_score,
                "average_latency_ms": winner.average_latency_ms,
                "faithfulness": winner.faithfulness,
                "answer_relevancy": winner.answer_relevancy,
                "context_precision": winner.context_precision,
                "context_recall": winner.context_recall,
                "explanation": winner.explanation,
            },
            "summary": response.summary,
            "recommendation_paragraph": response.recommendation_paragraph or response.summary,
            "recommendations": response.recommendations,
            "strengths": winner.strengths,
            "weaknesses": winner.weaknesses,
            "comparison_summary": (
                response.comparison_summary.model_dump() if response.comparison_summary else {}
            ),
            "metadata": response.metadata.model_dump() if response.metadata else {},
            "rankings": [
                {
                    "rank": arch.rank,
                    "architecture_id": arch.architecture_id,
                    "architecture_name": arch.architecture_name,
                    "overall_score": arch.overall_score,
                    "benchmark_score": arch.benchmark_score,
                    "average_latency_ms": arch.average_latency_ms,
                    "faithfulness": arch.faithfulness,
                    "answer_relevancy": arch.answer_relevancy,
                    "context_precision": arch.context_precision,
                    "context_recall": arch.context_recall,
                    "strengths": arch.strengths,
                    "weaknesses": arch.weaknesses,
                    "explanation": arch.explanation,
                    "reason": arch.reason,
                }
                for arch in response.rankings
            ],
        }