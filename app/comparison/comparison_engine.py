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
    ("precision_at_k", "Precision@K (top-K retrieval precision)"),
    ("recall_at_k", "Recall@K (top-K retrieval recall)"),
    ("hit_rate", "Hit Rate (retrieval hit rate)"),
    ("mrr", "MRR (Mean Reciprocal Rank of first relevant document)"),
    ("ndcg", "NDCG (Normalized Discounted Cumulative Gain)"),
    ("latency_ms", "Average Execution Latency (ms)"),
    ("estimated_cost_usd", "Estimated Cost per Query (USD)"),
    ("throughput_tokens_per_second", "Generation Throughput (tokens/sec)"),
]

_RADAR_METRIC_KEYS = [
    "faithfulness",
    "answer_relevancy",
    "precision_at_k",
    "recall_at_k",
    "hit_rate",
    "mrr",
    "ndcg",
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
        if metric_key == "faithfulness":
            return arch.faithfulness
        if metric_key == "answer_relevancy":
            return arch.answer_relevancy
        if metric_key == "precision_at_k":
            return arch.precision_at_k
        if metric_key == "recall_at_k":
            return arch.recall_at_k

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

            metric_title = metric_key.replace("_", " ").title()

            if runner_up_val is not None:
                diff = round(abs(winner_val - runner_up_val), 4)
                if diff < 1e-4:
                    winner_name = "Tie"
                    reason_str = f"Both architectures achieved identical {metric_title} scores ({winner_val})."
                else:
                    winner_name = winner_arch.architecture_name
                    reason_str = (
                        f"'{winner_arch.architecture_name}' outperformed '{runner_up_arch.architecture_name}' "
                        f"on {metric_key} by {diff:.4f} ({winner_val} vs {runner_up_val})."
                    )
            else:
                diff = 0.0
                winner_name = winner_arch.architecture_name
                reason_str = f"'{winner_arch.architecture_name}' achieved top score of {winner_val}."

            metric_winners.append(
                MetricWinner(
                    metric=metric_key,
                    winner=winner_name,
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
            tradeoffs.append(
                TradeOff(
                    dimension="General Performance",
                    winner=rankings[0].architecture_name if rankings else "None",
                    loser="None",
                    analysis="Single architecture evaluation — no comparative trade-offs identified.",
                    recommendation="Evaluate additional candidate architectures for comparative trade-off analysis.",
                )
            )
            return tradeoffs

        winner = rankings[0]
        runner_up = rankings[1]

        # 1. Quality vs Latency Tradeoff
        quality_diff = winner.overall_score - runner_up.overall_score
        latency_diff = runner_up.average_latency_ms - winner.average_latency_ms

        if quality_diff > 1e-4 and latency_diff < -1.0:
            # Winner has higher quality but ALSO higher latency (slower)
            tradeoffs.append(
                TradeOff(
                    dimension="Quality vs. Latency",
                    winner=winner.architecture_name,
                    loser=runner_up.architecture_name,
                    analysis=(
                        f"'{winner.architecture_name}' offers higher overall quality (+{quality_diff:.3f} composite score) "
                        f"but incurs a latency penalty of {abs(latency_diff):.0f} ms compared to '{runner_up.architecture_name}'."
                    ),
                    recommendation=(
                        f"If response latency is critical (< {winner.average_latency_ms:.0f} ms required), consider '{runner_up.architecture_name}' "
                        f"or introduce caching to optimize '{winner.architecture_name}'."
                    ),
                )
            )
        elif quality_diff > 1e-4 and latency_diff >= 0:
            # Winner dominates both quality and latency
            tradeoffs.append(
                TradeOff(
                    dimension="Quality vs. Latency",
                    winner=winner.architecture_name,
                    loser=runner_up.architecture_name,
                    analysis=(
                        f"'{winner.architecture_name}' dominates both overall quality (+{quality_diff:.3f}) and execution latency "
                        f"({winner.average_latency_ms:.0f} ms vs {runner_up.average_latency_ms:.0f} ms)."
                    ),
                    recommendation=f"Clear operational advantage for '{winner.architecture_name}' — no latency penalty incurred.",
                )
            )
        elif abs(quality_diff) <= 1e-4 and abs(latency_diff) > 1.0:
            # Same quality, but different latency
            faster = winner if winner.average_latency_ms < runner_up.average_latency_ms else runner_up
            slower = runner_up if faster == winner else winner
            tradeoffs.append(
                TradeOff(
                    dimension="Quality vs. Latency",
                    winner=faster.architecture_name,
                    loser=slower.architecture_name,
                    analysis=(
                        f"Both architectures achieved equivalent quality scores, but '{faster.architecture_name}' "
                        f"is {abs(latency_diff):.0f} ms faster than '{slower.architecture_name}'."
                    ),
                    recommendation=f"Prefer '{faster.architecture_name}' for lower latency and better user experience.",
                )
            )

        # 2. Retrieval Precision vs Recall Tradeoff
        if winner.precision_at_k > runner_up.precision_at_k + 1e-4 and winner.recall_at_k < runner_up.recall_at_k - 1e-4:
            tradeoffs.append(
                TradeOff(
                    dimension="Precision vs. Recall",
                    winner=winner.architecture_name,
                    loser=runner_up.architecture_name,
                    analysis=(
                        f"'{winner.architecture_name}' provides higher precision@k ({winner.precision_at_k:.2f}), "
                        f"whereas '{runner_up.architecture_name}' retrieves broader context with higher recall@k ({runner_up.recall_at_k:.2f})."
                    ),
                    recommendation="Choose based on whether noiseless prompt context (precision) or maximum information retrieval (recall) is prioritized.",
                )
            )
        elif runner_up.precision_at_k > winner.precision_at_k + 1e-4 and runner_up.recall_at_k < winner.recall_at_k - 1e-4:
            tradeoffs.append(
                TradeOff(
                    dimension="Precision vs. Recall",
                    winner=runner_up.architecture_name,
                    loser=winner.architecture_name,
                    analysis=(
                        f"'{runner_up.architecture_name}' provides higher precision@k ({runner_up.precision_at_k:.2f}), "
                        f"whereas '{winner.architecture_name}' retrieves broader context with higher recall@k ({winner.recall_at_k:.2f})."
                    ),
                    recommendation="Choose based on whether noiseless prompt context (precision) or maximum information retrieval (recall) is prioritized.",
                )
            )

        # Never return an empty list
        if not tradeoffs:
            tradeoffs.append(
                TradeOff(
                    dimension="General Performance",
                    winner="Both Architectures",
                    loser="None",
                    analysis="No significant trade-offs identified between compared architectures across quality, latency, and cost dimensions.",
                    recommendation="Selection can be guided by external infrastructure or deployment constraints.",
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
                elif key == "precision_at_k":
                    val = arch.precision_at_k
                elif key == "recall_at_k":
                    val = arch.recall_at_k
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
        """Construct structured executive summary with evidence-based tie handling."""
        is_tie = runner_up is not None and abs(winner.overall_score - runner_up.overall_score) <= 1e-4

        if is_tie and runner_up:
            verdict = (
                f"'{winner.architecture_name}' and '{runner_up.architecture_name}' achieved equivalent overall "
                f"composite scores ({winner.overall_score:.4f}). Rank assignment reflects primary optimization goal "
                f"('{goal.value}') and secondary metric tie-breaking."
            )
            reason = f"Tie — both candidates achieved equivalent composite scores under '{goal.value}' optimization."
            dep_rec = (
                f"Both '{winner.architecture_name}' and '{runner_up.architecture_name}' are suitable for deployment. "
                f"Select based on operational constraints such as infrastructure or latency."
            )
            risk = "Low operational risk — architectures demonstrate equivalent benchmark quality."
            mig_rec = (
                "Both architectures demonstrate equivalent benchmark performance. "
                "Selection should be based on deployment constraints such as latency, infrastructure, or cost."
            )
        elif runner_up:
            score_diff = winner.overall_score - runner_up.overall_score
            verdict = (
                f"'{winner.architecture_name}' is selected as the top RAG architecture candidate with a composite score of "
                f"{winner.overall_score:.4f} (Quality Grade: {winner.quality_grade or 'N/A'}, Readiness: {winner.deployment_readiness or 'N/A'}). "
                f"It outperforms runner-up '{runner_up.architecture_name}' by +{score_diff:.4f} points."
            )
            reason = winner.explanation or f"Highest composite score under '{goal.value}' optimization goal."
            dep_rec = f"Deploy '{winner.architecture_name}' to target environment ({winner.deployment_readiness or 'Production Ready'})."
            risk = f"Low migration risk if upgrading from '{runner_up.architecture_name}' to '{winner.architecture_name}'."
            
            faith_diff = winner.faithfulness - runner_up.faithfulness
            if faith_diff > 0.01:
                mig_rec = (
                    f"Recommended to transition workloads from '{runner_up.architecture_name}' to '{winner.architecture_name}' "
                    f"to achieve +{faith_diff:.2f} higher faithfulness."
                )
            else:
                mig_rec = f"Recommended to deploy '{winner.architecture_name}' as primary architecture."
        else:
            verdict = (
                f"'{winner.architecture_name}' evaluated with composite score of {winner.overall_score:.4f} "
                f"(Quality Grade: {winner.quality_grade or 'N/A'})."
            )
            reason = f"Evaluated under '{goal.value}' optimization goal."
            dep_rec = f"Deploy '{winner.architecture_name}' to target environment."
            risk = "Standard operational risks apply."
            mig_rec = "Proceed with standard deployment."

        primary_tradeoff = (
            tradeoffs[0].analysis if tradeoffs else "No significant trade-offs identified among top candidates."
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
        is_tie = runner_up is not None and abs(winner.overall_score - runner_up.overall_score) <= 1e-4

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
            score_diff = 0.0 if is_tie else round(winner.overall_score - runner_up.overall_score, 4)
            latency_diff_ms = round(runner_up.average_latency_ms - winner.average_latency_ms, 2)
            metric_diffs = {
                "faithfulness": round(winner.faithfulness - runner_up.faithfulness, 4),
                "answer_relevancy": round(winner.answer_relevancy - runner_up.answer_relevancy, 4),
                "precision_at_k": round(winner.precision_at_k - runner_up.precision_at_k, 4),
                "recall_at_k": round(winner.recall_at_k - runner_up.recall_at_k, 4),
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

        if is_tie and runner_up:
            summary_text = (
                f"Compared {len(rankings)} RAG architectures under '{request.optimization_goal.value}' optimization. "
                f"Result: Tie between '{winner.architecture_name}' and '{runner_up.architecture_name}' (Score: {winner.overall_score:.4f})."
            )
            recommendations = [
                f"Both architectures demonstrate equivalent benchmark performance ({winner.overall_score:.4f}).",
                "Selection should be based on deployment constraints such as latency, infrastructure, or cost.",
                f"Faithfulness: {winner.faithfulness:.2f} vs {runner_up.faithfulness:.2f} | Answer Relevancy: {winner.answer_relevancy:.2f} vs {runner_up.answer_relevancy:.2f}.",
                f"Average latency: {winner.architecture_name} ({winner.average_latency_ms:.0f} ms) vs {runner_up.architecture_name} ({runner_up.average_latency_ms:.0f} ms).",
            ]
        else:
            summary_text = (
                f"Compared {len(rankings)} RAG architectures under '{request.optimization_goal.value}' optimization. "
                f"Winner: '{winner.architecture_name}' (Score: {winner.overall_score:.4f}, Grade: {winner.quality_grade or 'N/A'})."
            )
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

        rec_paragraph = exec_summary.overall_verdict

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