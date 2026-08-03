"""
Comparison report builder for Forge architecture comparison (v2.0).
"""

from typing import Any, Dict
from app.comparison.comparison_models import ComparisonReport, ComparisonResponse


class ComparisonReportBuilder:
    """Builds human-readable structured comparison reports (v2.0)."""

    def build_report(
        self,
        response: ComparisonResponse,
    ) -> ComparisonReport:
        """Generate typed ComparisonReport Pydantic model payload."""
        winner = response.winner
        runner_up = response.runner_up

        winner_details = {
            "architecture_id": winner.architecture_id,
            "overall_score": winner.overall_score,
            "benchmark_score": winner.benchmark_score,
            "average_latency_ms": winner.average_latency_ms,
            "quality_grade": winner.quality_grade,
            "deployment_readiness": winner.deployment_readiness,
            "faithfulness": winner.faithfulness,
            "answer_relevancy": winner.answer_relevancy,
            "context_precision": winner.context_precision,
            "context_recall": winner.context_recall,
            "explanation": winner.explanation,
        }

        exec_summary_dict = (
            response.executive_summary.model_dump()
            if response.executive_summary
            else {}
        )

        return ComparisonReport(
            comparison_id=response.comparison_id,
            comparison_name=response.comparison_name,
            comparison_version=response.comparison_version or "2.0",
            best_architecture=winner.architecture_name,
            runner_up=runner_up.architecture_name if runner_up else None,
            winner_details=winner_details,
            summary=response.summary,
            recommendation_paragraph=response.recommendation_paragraph or response.summary,
            recommendations=response.recommendations,
            strengths=winner.strengths,
            weaknesses=winner.weaknesses,
            comparison_summary=(
                response.comparison_summary.model_dump() if response.comparison_summary else {}
            ),
            rankings=[
                {
                    "rank": arch.rank,
                    "architecture_id": arch.architecture_id,
                    "architecture_name": arch.architecture_name,
                    "overall_score": arch.overall_score,
                    "benchmark_score": arch.benchmark_score,
                    "average_latency_ms": arch.average_latency_ms,
                    "quality_grade": arch.quality_grade,
                    "deployment_readiness": arch.deployment_readiness,
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
            metric_winners=[mw.model_dump() for mw in response.metric_winners],
            trade_off_analysis=[to.model_dump() for to in response.trade_off_analysis],
            strength_comparison=response.strength_comparison,
            weakness_comparison=response.weakness_comparison,
            production_readiness_comparison=response.production_readiness_comparison,
            radar_metrics=response.radar_metrics,
            executive_summary=exec_summary_dict,
            metadata=response.metadata.model_dump() if response.metadata else {},
            compared_at=response.compared_at,
        )

    def build_report_dict(
        self,
        response: ComparisonResponse,
    ) -> Dict[str, Any]:
        """Generate structured comparison report dictionary payload (backward compatible alias)."""
        report = self.build_report(response)
        return report.model_dump()