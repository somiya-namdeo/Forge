"""Benchmark statistics engine module for aggregating evaluation results."""

from collections import defaultdict
import math
import statistics

from app.benchmark.benchmark_models import (
    BenchmarkSampleResult,
    BenchmarkStatistics,
    MetricStatistics,
)
from app.schemas.evaluation import EvaluationStatus


class BenchmarkStatisticsEngine:
    """Engine responsible for computing aggregate statistics from benchmark sample results."""

    @staticmethod
    def _clamp(value: float) -> float:
        """Clamp score to [0, 1]."""
        return min(1.0, max(0.0, value))

    @classmethod
    def _compute_metric_statistics(
        cls,
        metric_scores_map: dict[str, list[float]],
    ) -> dict[str, MetricStatistics]:
        """Compute detailed statistics for every evaluation metric."""
        metric_stats: dict[str, MetricStatistics] = {}

        for metric_name, scores in metric_scores_map.items():
            if not scores:
                continue

            metric_stats[metric_name] = MetricStatistics(
                average=cls._clamp(statistics.fmean(scores)),
                median=cls._clamp(statistics.median(scores)),
                minimum=cls._clamp(min(scores)),
                maximum=cls._clamp(max(scores)),
                standard_deviation=(
                    statistics.stdev(scores)
                    if len(scores) > 1
                    else 0.0
                ),
            )

        return metric_stats

    @staticmethod
    def _percentile(values: list[float], percentile: float) -> float:
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
    def _create_empty_statistics(cls) -> BenchmarkStatistics:
        """Construct an empty BenchmarkStatistics object."""
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

    @classmethod
    def compute(cls, results: list[BenchmarkSampleResult]) -> BenchmarkStatistics:
        """Compute benchmark summary statistics."""
        if not results:
            return cls._create_empty_statistics()

        total_samples = len(results)

        overall_scores: list[float] = []
        execution_times: list[float] = []

        metric_scores_map: dict[str, list[float]] = defaultdict(list)

        status_counts: dict[str, int] = {
            EvaluationStatus.PASS.value: 0,
            EvaluationStatus.WARNING.value: 0,
            EvaluationStatus.FAIL.value: 0,
        }

        for result in results:
            response = result.evaluation_response

            overall_scores.append(response.overall_score)
            execution_times.append(result.execution_time_ms)

            status_counts[response.status.value] += 1

            if isinstance(response.metrics, dict):
                for metric_name, metric_score in response.metrics.items():
                    metric_scores_map[metric_name].append(metric_score)
            else:
                for metric in response.metrics:
                    metric_scores_map[metric.name].append(metric.score)

        metric_averages = {
            metric_name: cls._clamp(statistics.fmean(scores))
            for metric_name, scores in metric_scores_map.items()
            if scores
        }

        metric_statistics = cls._compute_metric_statistics(metric_scores_map)

        passed = status_counts[EvaluationStatus.PASS.value]
        failed = status_counts[EvaluationStatus.FAIL.value]

        return BenchmarkStatistics(
            total_samples=total_samples,
            passed_samples=passed,
            warning_samples=status_counts[EvaluationStatus.WARNING.value],
            failed_samples=failed,
            average_score=cls._clamp(statistics.fmean(overall_scores)),
            median_score=cls._clamp(statistics.median(overall_scores)),
            minimum_score=cls._clamp(min(overall_scores)),
            maximum_score=cls._clamp(max(overall_scores)),
            score_standard_deviation=(
                statistics.stdev(overall_scores)
                if len(overall_scores) > 1
                else 0.0
            ),
            average_execution_time_ms=statistics.fmean(execution_times),
            median_execution_time_ms=statistics.median(execution_times),
            minimum_execution_time_ms=min(execution_times),
            maximum_execution_time_ms=max(execution_times),
            p95_execution_time_ms=cls._percentile(execution_times, 0.95),
            success_rate=passed / total_samples,
            failure_rate=failed / total_samples,
            metric_averages=metric_averages,
            metric_statistics=metric_statistics,
            status_distribution=status_counts,
        )