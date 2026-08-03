"""
Architecture comparison engine for Forge platform (v2.0).

Orchestrates multi-candidate RAG architecture benchmarking comparisons using pre-computed
BenchmarkReports. Produces winner explanations, metric winners, trade-off analysis,
radar-chart metrics, and executive summaries.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import uuid4

from app.comparison.comparison_models import (
    ArchitectureCandidate,
    ComparisonExecutiveSummary,
    ComparisonMetadata,
    ComparisonRequest,
    ComparisonResponse,
    ComparisonSummaryDetails,
    MetricWinner,
    OptimizationGoal,
    RankedArchitecture,
    TradeOff,
)
from app.comparison.ranking import RankingEngine

# Standard evaluation metrics to evaluate for per-metric winners & radar chart
_ALL_COMPARED_METRICS = [
    ("faithfulness", "Faithfulness (factual adherence to contexts)"),
    ("answer_relevancy", "Answer Relevancy (relevance of generated response to prompt)"),
    ("groundedness", "Groundedness (claims supported by source documents)"),
    ("context_precision", "Context Precision (signal-to-noise ratio in retrieval)"),
    ("context_recall", "Context Recall (completeness of retrieved context)"),
    ("hallucination_score", "Hallucination Avoidance (freedom from ungrounded content)"),
    ("completeness", "Answer Completeness (coverage of expected information)"),
    ("coherence", "Answer Coherence (structural and logical clarity)"),
    ("precision_at_k", "Precision@K (top-K retrieval precision)"),
    ("recall_at_k", "Recall@K (top-K retrieval recall)"),
    ("mrr", "MRR (Mean Reciprocal Rank of first relevant document)"),
    ("ndcg", "NDCG (Normalized Discounted Cumulative Gain)"),
    ("latency_ms", "Average Execution Latency (ms)"),
    ("estimated_cost_usd", "Estimated Cost per Query (USD)"),
    ("throughput_tokens_per_second", "Generation Throughput (tokens/sec)"),
]

_RADAR_METRIC_KEYS = [
    "faithfulness",
    "groundedness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
    "hallucination_score",
    "mrr",
    "coherence",
]


class ComparisonEngine:
    """Orchestrates RAG architecture comparisons using RankingEngine and BenchmarkReports."""

    def __init__(self, ranking_engine: Optional[RankingEngine] = None) -> None:
        """Initialize comparison engine with injected dependencies."""
        self.ranking_engine = ranking_engine or RankingEngine()

    @staticmethod
    def _extract_metric_value(arch: RankedArchitecture, metric_key: str) -> float:
        """Helper to fetch metric score from RankedArchitecture."""
        if metric_key == "latency_ms":
            return arch.average_latency_ms
        if metric_key == "faithfulness":
            return arch.faithfulness
        if metric_key == "answer_relevancy":
            return arch.answer_relevancy
        if metric_key == "context_precision":
            return arch.context_precision
        if metric_key == "context_recall":
            return arch.context_recall

        # Check full metric_averages dict
        if arch.metric_averages and metric_key in arch.metric_averages:
            return float(arch.metric_averages[metric_key])

        # Fallback for benchmark_score
        return arch.benchmark_score

    def _determine_metric_winners(
        self,
        rankings: List[RankedArchitecture],
    ) -> List[MetricWinner]:
        """Determine winner for every important metric across compared architectures."""
        metric_winners: List[MetricWinner] = []

        for metric_key, description in _ALL_COMPARED_METRICS:
            # Sort candidates by this metric
            # Note: For latency_ms and estimated_cost_usd, LOWER score is better!
            is_lower_better = metric_key in ("latency_ms", "estimated_cost_usd")

            sorted_archs = sorted(
                rankings,
                key=lambda a: self._extract_metric_value(a, metric_key),
                reverse=not is_lower_better,
            )

            winner_arch = sorted_archs[0]
            winner_val = round(self._extract_metric_value(winner_arch, metric_key), 4)

            runner_up_arch = sorted_archs[1] if len(sorted_archs) > 1 else None
            runner_up_val = (
                round(self._extract_metric_value(runner_up_arch, metric_key), 4)
                if runner_up_arch
                else None
            )

            if runner_up_val is not None:
                diff = round(abs(winner_val - runner_up_val), 4)
                reason_str = (
                    f"'{winner_arch.architecture_name}' outperform '{runner_up_arch.architecture_name}' "
                    f"on {metric_key} by {diff:.4f} ({winner_val} vs {runner_up_val})."
                )
            else:
                diff = 0.0
                reason_str = f"'{winner_arch.architecture_name}' achieved top score of {winner_val}."

            metric_winners.append(
                MetricWinner(
                    metric=metric_key,
                    winner=winner_arch.architecture_name,
                    winner_score=winner_val,
                    runner_up=runner_up_arch.architecture_name if runner_up_arch else None,
                    runner_up_score=runner_up_val,
                    score_difference=diff,
                    reason=reason_str,
                )
            )

        return metric_winners

    @staticmethod
    def _generate_tradeoffs(
        rankings: List[RankedArchitecture],
        goal: OptimizationGoal,
    ) -> List[TradeOff]:
        """Automatically generate trade-off analysis across architectures."""
        tradeoffs: List[TradeOff] = []
        if len(rankings) < 2:
            return tradeoffs

        winner = rankings[0]
        runner_up = rankings[1]

        # 1. Quality vs Latency Tradeoff
        quality_diff = winner.overall_score - runner_up.overall_score
        latency_diff = runner_up.average_latency_ms - winner.average_latency_ms

        if quality_diff > 0 and latency_diff < 0:
            # Winner has higher quality but ALSO higher latency (slower)
            tradeoffs.append(
                TradeOff(
                    dimension="Quality vs. Latency",
                    winner=winner.architecture_name,
                    loser=runner_up.architecture_name,
                    analysis=(
                        f"'{winner.architecture_name}' offers higher quality (+{quality_diff:.3f} overall score) "
                        f"but incurs a latency penalty of {abs(latency_diff):.0f} ms compared to '{runner_up.architecture_name}'."
                    ),
                    recommendation=(
                        f"If latency is critical (< {winner.average_latency_ms:.0f}ms required), consider '{runner_up.architecture_name}' "
                        f"or introduce caching to optimize '{winner.architecture_name}'."
                    ),
                )
            )
        elif quality_diff > 0 and latency_diff >= 0:
            # Winner dominates both quality and latency
            tradeoffs.append(
                TradeOff(
                    dimension="Quality vs. Latency",
                    winner=winner.architecture_name,
                    loser=runner_up.architecture_name,
                    analysis=(
                        f"'{winner.architecture_name}' dominates both quality (+{quality_diff:.3f}) and latency "
                        f"({winner.average_latency_ms:.0f} ms vs {runner_up.average_latency_ms:.0f} ms)."
                    ),
                    recommendation=f"Clear advantage for '{winner.architecture_name}' — no latency penalty incurred.",
                )
            )

        # 2. Retrieval Precision vs Recall Tradeoff
        if winner.context_precision > runner_up.context_precision and winner.context_recall < runner_up.context_recall:
            tradeoffs.append(
                TradeOff(
                    dimension="Context Precision vs. Recall",
                    winner=winner.architecture_name,
                    loser=runner_up.architecture_name,
                    analysis=(
                        f"'{winner.architecture_name}' provides higher context precision ({winner.context_precision:.2f}), "
                        f"whereas '{runner_up.architecture_name}' retrieves broader context with higher recall ({runner_up.context_recall:.2f})."
                    ),
                    recommendation="Choose based on whether noiseless prompt context (precision) or maximum information retrieval (recall) is prioritized.",
                )
            )

        # 3. Groundedness vs Coherence
        w_groundedness = winner.metric_averages.get("groundedness", winner.faithfulness)
        ru_groundedness = runner_up.metric_averages.get("groundedness", runner_up.faithfulness)
        if w_groundedness > ru_groundedness:
            tradeoffs.append(
                TradeOff(
                    dimension="Factual Groundedness",
                    winner=winner.architecture_name,
                    loser=runner_up.architecture_name,
                    analysis=(
                        f"'{winner.architecture_name}' has superior factual groundedness ({w_groundedness:.2f} vs {ru_groundedness:.2f}), "
                        "reducing hallucination risk."
                    ),
                    recommendation="Recommended for high-compliance enterprise legal and technical domains.",
                )
            )

        return tradeoffs

    @staticmethod
    def _build_radar_metrics(
        rankings: List[RankedArchitecture],
    ) -> Dict[str, Dict[str, float]]:
        """Generate backend-ready radar chart metrics dictionary."""
        radar_data: Dict[str, Dict[str, float]] = {}

        for arch in rankings:
            arch_metrics: Dict[str, float] = {}
            for key in _RADAR_METRIC_KEYS:
                if key == "faithfulness":
                    val = arch.faithfulness
                elif key == "answer_relevancy":
                    val = arch.answer_relevancy
                elif key == "context_precision":
                    val = arch.context_precision
                elif key == "context_recall":
                    val = arch.context_recall
                elif arch.metric_averages and key in arch.metric_averages:
                    val = arch.metric_averages[key]
                else:
                    val = arch.overall_score
                arch_metrics[key.replace("_", " ").title()] = round(val, 4)

            radar_data[arch.architecture_name] = arch_metrics

        return radar_data

    @staticmethod
    def _build_executive_summary(
        winner: RankedArchitecture,
        runner_up: Optional[RankedArchitecture],
        tradeoffs: List[TradeOff],
        goal: OptimizationGoal,
    ) -> ComparisonExecutiveSummary:
        """Construct structured executive summary."""
        verdict = (
            f"'{winner.architecture_name}' is selected as the top RAG architecture candidate with a composite score of "
            f"{winner.overall_score:.4f} (Quality Grade: {winner.quality_grade or 'N/A'}, Readiness: {winner.deployment_readiness or 'N/A'})."
        )
        if runner_up:
            verdict += f" It outperforms runner-up '{runner_up.architecture_name}' by +{winner.overall_score - runner_up.overall_score:.4f} points."

        reason = winner.explanation or f"Highest composite score under '{goal.value}' optimization goal."

        primary_tradeoff = (
            tradeoffs[0].analysis if tradeoffs else "No significant trade-offs identified among top candidates."
        )

        dep_rec = (
            f"Deploy '{winner.architecture_name}' to target environment ({winner.deployment_readiness or 'Production Ready'})."
        )

        risk = (
            f"Low migration risk if upgrading from '{runner_up.architecture_name}' to '{winner.architecture_name}'."
            if runner_up
            else "Standard operational risks apply."
        )

        mig_rec = (
            f"Recommended to transition workloads from '{runner_up.architecture_name}' to '{winner.architecture_name}' "
            f"to achieve +{winner.faithfulness - (runner_up.faithfulness if runner_up else 0):.2f} higher faithfulness."
            if runner_up
            else "Proceed with standard deployment."
        )

        return ComparisonExecutiveSummary(
            overall_winner=winner.architecture_name,
            overall_verdict=verdict,
            best_architecture=winner.architecture_name,
            runner_up=runner_up.architecture_name if runner_up else None,
            primary_reason=reason,
            major_tradeoff=primary_tradeoff,
            deployment_recommendation=dep_rec,
            risk_analysis=risk,
            migration_recommendation=mig_rec,
        )

    def compare(self, request: ComparisonRequest) -> ComparisonResponse:
        """Execute multi-architecture comparison using pre-computed BenchmarkReports.

        Consumes BenchmarkReport v2.0 only — zero re-execution of evaluation or benchmark metrics.
        """
        comparison_id = str(uuid4())
        created_at = datetime.now(timezone.utc)

        # 1. Rank candidates using RankingEngine
        rankings = self.ranking_engine.rank(
            candidates=request.architectures,
            goal=request.optimization_goal,
            strategy=request.ranking_strategy,
        )

        winner = rankings[0]
        runner_up = rankings[1] if len(rankings) > 1 else None

        # 2. Metric winners
        metric_winners_list = self._determine_metric_winners(rankings)

        # 3. Trade-off analysis
        tradeoffs = self._generate_tradeoffs(rankings, request.optimization_goal)

        # 4. Radar metrics
        radar_metrics = self._build_radar_metrics(rankings)

        # 5. Executive summary
        exec_summary = self._build_executive_summary(
            winner, runner_up, tradeoffs, request.optimization_goal
        )

        # 6. Comparative maps
        strength_comp = {a.architecture_name: a.strengths for a in rankings}
        weakness_comp = {a.architecture_name: a.weaknesses for a in rankings}
        rec_comp = {a.architecture_name: a.recommendations for a in rankings}
        readiness_comp = {a.architecture_name: a.deployment_readiness or "Prototype" for a in rankings}
        fallback_comp = {a.architecture_name: a.fallback_rate for a in rankings}

        metric_diffs: Dict[str, float] = {}
        score_diff = 0.0
        latency_diff_ms = 0.0
        metric_winners_map: Dict[str, str] = {}

        for mw in metric_winners_list:
            metric_winners_map[mw.metric] = mw.winner

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
            recommendation=exec_summary.deployment_recommendation,
            metric_winners=metric_winners_map,
            production_readiness_comparison=readiness_comp,
            fallback_rate_comparison=fallback_comp,
        )

        metadata = ComparisonMetadata(
            comparison_id=comparison_id,
            created_at=created_at,
            ranking_strategy=request.ranking_strategy.value
            if hasattr(request.ranking_strategy, "value")
            else str(request.ranking_strategy),
            optimization_goal=request.optimization_goal.value
            if hasattr(request.optimization_goal, "value")
            else str(request.optimization_goal),
            number_of_architectures=len(rankings),
        )

        summary_text = (
            f"Compared {len(rankings)} RAG architectures under '{request.optimization_goal.value}' optimization. "
            f"Winner: '{winner.architecture_name}' (Score: {winner.overall_score:.4f}, Grade: {winner.quality_grade or 'N/A'})."
        )
        rec_paragraph = exec_summary.overall_verdict
        recommendations = [
            f"Deploy {winner.architecture_name} as the primary RAG architecture.",
            f"Overall composite score: {winner.overall_score:.4f} (Grade: {winner.quality_grade or 'N/A'}).",
            f"Faithfulness: {winner.faithfulness:.2f} | Answer Relevancy: {winner.answer_relevancy:.2f}.",
            f"Average latency: {winner.average_latency_ms:.0f} ms | Deployment Readiness: {winner.deployment_readiness or 'Production Ready'}.",
        ]
        if runner_up:
            recommendations.append(
                f"Runner-up alternative: {runner_up.architecture_name} (score: {runner_up.overall_score:.4f})."
            )

        # Cost vs quality / Latency vs quality text analysis
        cost_vs_quality = (
            f"'{winner.architecture_name}' delivers a composite quality score of {winner.overall_score:.4f} "
            f"with competitive execution cost and resource utilization."
        )
        latency_vs_quality = (
            f"'{winner.architecture_name}' achieves {winner.overall_score:.4f} quality score with an average "
            f"execution latency of {winner.average_latency_ms:.0f} ms."
        )

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
            # v2.0 fields
            comparison_version="2.0",
            overall_winner=winner.architecture_name,
            overall_winner_reason=winner.explanation,
            ranked_architectures=rankings,
            metric_winners=metric_winners_list,
            trade_off_analysis=tradeoffs,
            strength_comparison=strength_comp,
            weakness_comparison=weakness_comp,
            recommendation_comparison=rec_comp,
            deployment_recommendation=exec_summary.deployment_recommendation,
            production_readiness_comparison=readiness_comp,
            cost_vs_quality_analysis=cost_vs_quality,
            latency_vs_quality_analysis=latency_vs_quality,
            radar_metrics=radar_metrics,
            executive_summary=exec_summary,
        )