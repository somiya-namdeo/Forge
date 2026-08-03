"""Benchmark statistics engine module for aggregating evaluation results (v2.0)."""

import math
import statistics
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

from app.benchmark.benchmark_models import (
    BenchmarkSampleResult,
    BenchmarkStatistics,
    MetricStatistics,
)
from app.schemas.evaluation import EvaluationStatus

# ─── Known metric categories (mirrors MetricCategory enum values) ─────────────
_GENERATION_METRICS = frozenset({
    "faithfulness", "answer_relevancy", "context_precision", "context_recall",
    "groundedness", "hallucination_score", "completeness", "coherence",
})
_RETRIEVAL_METRICS = frozenset({
    "precision_at_k", "recall_at_k", "hit_rate", "mrr", "ndcg",
})
_OPERATIONAL_METRICS = frozenset({
    "latency_ms", "token_usage", "estimated_cost_usd", "throughput_tokens_per_second",
})

# Maximum top-N items to surface in aggregated diagnostic lists
_TOP_N_DIAGNOSTICS = 5


class BenchmarkStatisticsEngine:
    """Engine responsible for computing aggregate statistics from benchmark sample results (v2.0).

    Consumes ComprehensiveEvaluationReport fields from each BenchmarkSampleResult.
    Does NOT recompute or duplicate any evaluation metric logic.
    """

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp a score to [0.0, 1.0]."""
        return min(1.0, max(0.0, value))

    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        """Compute percentile using linear interpolation."""
        if not values:
            return 0.0
        values = sorted(values)
        if len(values) == 1:
            return values[0]
        k = (len(values) - 1) * percentile
        lower = math.floor(k)
        upper = math.ceil(k)
        if lower == upper:
            return values[int(k)]
        return values[lower] * (upper - k) + values[upper] * (k - lower)

    @classmethod
    def _compute_metric_statistics(
        cls,
        metric_scores_map: Dict[str, List[float]],
    ) -> Dict[str, MetricStatistics]:
        """Compute per-metric detailed statistics."""
        metric_stats: Dict[str, MetricStatistics] = {}
        for metric_name, scores in metric_scores_map.items():
            if not scores:
                continue
            metric_stats[metric_name] = MetricStatistics(
                average=cls._clamp(statistics.fmean(scores)),
                median=cls._clamp(statistics.median(scores)),
                minimum=cls._clamp(min(scores)),
                maximum=cls._clamp(max(scores)),
                standard_deviation=(
                    statistics.stdev(scores) if len(scores) > 1 else 0.0
                ),
            )
        return metric_stats

    @staticmethod
    def _top_by_frequency(items: List[str], n: int = _TOP_N_DIAGNOSTICS) -> List[str]:
        """Return the top-N most frequent strings from a list."""
        if not items:
            return []
        return [item for item, _ in Counter(items).most_common(n)]

    @staticmethod
    def _aggregate_provider_summary(
        per_sample_summaries: List[Dict[str, List[str]]],
    ) -> Dict[str, List[str]]:
        """Merge per-sample provider→metric mappings, collecting the unique metric names per provider."""
        merged: Dict[str, set] = defaultdict(set)
        for sample_summary in per_sample_summaries:
            for provider, metrics in sample_summary.items():
                merged[provider].update(metrics)
        return {provider: sorted(metrics) for provider, metrics in merged.items()}

    @classmethod
    def _compute_fallback_rate(
        cls,
        per_sample_fallback_lists: List[List[str]],
        per_sample_total_metrics: List[int],
    ) -> float:
        """Calculate the fraction of metric executions that used deterministic fallback."""
        total_fallbacks = sum(len(fb) for fb in per_sample_fallback_lists)
        total_executions = sum(per_sample_total_metrics)
        if total_executions == 0:
            return 0.0
        return round(cls._clamp(total_fallbacks / total_executions), 4)

    @classmethod
    def _create_empty_statistics(cls) -> BenchmarkStatistics:
        """Construct an empty BenchmarkStatistics object (all defaults)."""
        return BenchmarkStatistics(
            total_samples=0,
            passed_samples=0,
            warning_samples=0,
            failed_samples=0,
            average_score=0.0,
            median_score=0.0,
            minimum_score=0.0,
            maximum_score=0.0,
            score_standard_deviation=0.0,
            average_execution_time_ms=0.0,
            median_execution_time_ms=0.0,
            minimum_execution_time_ms=0.0,
            maximum_execution_time_ms=0.0,
            p95_execution_time_ms=0.0,
            success_rate=0.0,
            failure_rate=0.0,
            metric_averages={},
            metric_statistics={},
            status_distribution={
                EvaluationStatus.PASS.value: 0,
                EvaluationStatus.WARNING.value: 0,
                EvaluationStatus.FAIL.value: 0,
            },
        )

    # ─── Main Computation ──────────────────────────────────────────────────────

    @classmethod
    def compute(cls, results: List[BenchmarkSampleResult]) -> BenchmarkStatistics:
        """Compute enriched benchmark summary statistics from evaluation results.

        Consumes ComprehensiveEvaluationReport fields from each result.
        Does NOT recompute evaluation metrics.
        """
        if not results:
            return cls._create_empty_statistics()

        total_samples = len(results)

        # ── Core accumulators ─────────────────────────────────────────────────
        overall_scores: List[float] = []
        execution_times: List[float] = []
        metric_scores_map: Dict[str, List[float]] = defaultdict(list)
        status_counts: Dict[str, int] = {
            EvaluationStatus.PASS.value: 0,
            EvaluationStatus.WARNING.value: 0,
            EvaluationStatus.FAIL.value: 0,
        }

        # ── v2.0 accumulators ─────────────────────────────────────────────────
        grade_counter: Counter = Counter()
        readiness_counter: Counter = Counter()
        generation_scores_map: Dict[str, List[float]] = defaultdict(list)
        retrieval_scores_map: Dict[str, List[float]] = defaultdict(list)
        operational_scores_map: Dict[str, List[float]] = defaultdict(list)
        all_strengths: List[str] = []
        all_weaknesses: List[str] = []
        all_recommendations: List[str] = []
        per_sample_provider_summaries: List[Dict[str, List[str]]] = []
        per_sample_fallback_lists: List[List[str]] = []
        per_sample_total_metrics: List[int] = []

        # ── Iterate over sample results ───────────────────────────────────────
        for result in results:
            response = result.evaluation_response

            overall_scores.append(response.overall_score)
            execution_times.append(result.execution_time_ms)

            # Status distribution (existing logic)
            status_val = response.status.value if hasattr(response.status, "value") else str(response.status)
            if status_val in status_counts:
                status_counts[status_val] += 1

            # Flat metrics (existing logic)
            if isinstance(response.metrics, dict):
                for metric_name, metric_score in response.metrics.items():
                    metric_scores_map[metric_name].append(metric_score)

                    # Categorise into generation / retrieval / operational
                    if metric_name in _GENERATION_METRICS:
                        generation_scores_map[metric_name].append(metric_score)
                    elif metric_name in _RETRIEVAL_METRICS:
                        retrieval_scores_map[metric_name].append(metric_score)
                    elif metric_name in _OPERATIONAL_METRICS:
                        operational_scores_map[metric_name].append(metric_score)
            else:
                # Legacy path: list of metric objects
                for metric in response.metrics:
                    metric_scores_map[metric.name].append(metric.score)

            # ── v2.0: consume ComprehensiveEvaluationReport fields ────────────
            # Quality grade
            grade = getattr(response, "quality_grade", None)
            if grade:
                grade_counter[grade] += 1

            # Deployment readiness
            readiness = getattr(response, "deployment_readiness", None)
            if readiness:
                readiness_counter[readiness] += 1

            # Diagnostic strings from summary
            summary = getattr(response, "summary", None)
            if summary:
                all_strengths.extend(getattr(summary, "strengths", []) or [])
                all_weaknesses.extend(getattr(summary, "weaknesses", []) or [])
                all_recommendations.extend(getattr(summary, "recommendations", []) or [])

            # Provider metadata
            provider_summary = getattr(response, "provider_summary", None) or {}
            per_sample_provider_summaries.append(dict(provider_summary))

            fallback_metrics = getattr(response, "fallback_metrics", None) or []
            per_sample_fallback_lists.append(list(fallback_metrics))

            total_metrics = getattr(response, "total_metrics", 0) or 0
            per_sample_total_metrics.append(total_metrics)

        # ── Compute existing aggregates ───────────────────────────────────────
        metric_averages = {
            metric_name: cls._clamp(statistics.fmean(scores))
            for metric_name, scores in metric_scores_map.items()
            if scores
        }
        metric_stats = cls._compute_metric_statistics(metric_scores_map)
        passed = status_counts[EvaluationStatus.PASS.value]
        failed = status_counts[EvaluationStatus.FAIL.value]

        # ── Compute v2.0 aggregates ───────────────────────────────────────────
        grade_distribution = dict(grade_counter)
        deployment_readiness_distribution = dict(readiness_counter)

        generation_metric_averages = {
            k: cls._clamp(statistics.fmean(v)) for k, v in generation_scores_map.items() if v
        }
        retrieval_metric_averages = {
            k: cls._clamp(statistics.fmean(v)) for k, v in retrieval_scores_map.items() if v
        }
        operational_metric_averages = {
            k: cls._clamp(statistics.fmean(v)) for k, v in operational_scores_map.items() if v
        }

        aggregated_provider_summary = cls._aggregate_provider_summary(per_sample_provider_summaries)
        fallback_rate = cls._compute_fallback_rate(per_sample_fallback_lists, per_sample_total_metrics)

        top_strengths = cls._top_by_frequency(all_strengths)
        top_weaknesses = cls._top_by_frequency(all_weaknesses)
        top_recommendations = cls._top_by_frequency(all_recommendations)

        return BenchmarkStatistics(
            # ── Existing fields ──────────────────────────────────────────────
            total_samples=total_samples,
            passed_samples=passed,
            warning_samples=status_counts[EvaluationStatus.WARNING.value],
            failed_samples=failed,
            average_score=cls._clamp(statistics.fmean(overall_scores)),
            median_score=cls._clamp(statistics.median(overall_scores)),
            minimum_score=cls._clamp(min(overall_scores)),
            maximum_score=cls._clamp(max(overall_scores)),
            score_standard_deviation=(
                statistics.stdev(overall_scores) if len(overall_scores) > 1 else 0.0
            ),
            average_execution_time_ms=statistics.fmean(execution_times),
            median_execution_time_ms=statistics.median(execution_times),
            minimum_execution_time_ms=min(execution_times),
            maximum_execution_time_ms=max(execution_times),
            p95_execution_time_ms=cls._percentile(execution_times, 0.95),
            success_rate=passed / total_samples,
            failure_rate=failed / total_samples,
            metric_averages=metric_averages,
            metric_statistics=metric_stats,
            status_distribution=status_counts,
            # ── v2.0 fields ──────────────────────────────────────────────────
            grade_distribution=grade_distribution,
            deployment_readiness_distribution=deployment_readiness_distribution,
            generation_metric_averages=generation_metric_averages,
            retrieval_metric_averages=retrieval_metric_averages,
            operational_metric_averages=operational_metric_averages,
            provider_summary=aggregated_provider_summary,
            fallback_rate=fallback_rate,
            top_strengths=top_strengths,
            top_weaknesses=top_weaknesses,
            top_recommendations=top_recommendations,
        )