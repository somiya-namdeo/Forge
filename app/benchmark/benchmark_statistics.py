"""Benchmark statistics engine module for aggregating evaluation results."""

from collections import defaultdict
import statistics

from app.benchmark.benchmark_models import (
    BenchmarkSampleResult,
    BenchmarkStatistics,
)
from app.schemas.evaluation import EvaluationStatus


class BenchmarkStatisticsEngine:
    """Engine responsible for computing aggregate statistics from benchmark sample results."""

    @staticmethod
    def _compute_metric_averages(
        metric_scores_map: dict[str, list[float]],
    ) -> dict[str, float]:
        """Calculate arithmetic mean for each metric from collected raw scores."""
        return {
            metric_name: min(1.0, max(0.0, statistics.fmean(scores)))
            for metric_name, scores in metric_scores_map.items()
            if scores
        }

    @staticmethod
    def _create_empty_statistics() -> BenchmarkStatistics:
        """Construct a zero-valued BenchmarkStatistics container for empty datasets."""
        return BenchmarkStatistics(
            total_samples=0,
            passed_samples=0,
            warning_samples=0,
            failed_samples=0,
            average_score=0.0,
            average_execution_time_ms=0.0,
            metric_averages={},
            status_distribution={
                EvaluationStatus.PASS.value: 0,
                EvaluationStatus.WARNING.value: 0,
                EvaluationStatus.FAIL.value: 0,
            },
        )

    @classmethod
    def compute(cls, results: list[BenchmarkSampleResult]) -> BenchmarkStatistics:
        """Compute summary statistics across a list of benchmark sample results."""
        if not results:
            return cls._create_empty_statistics()

        total_samples = len(results)
        overall_scores: list[float] = []
        execution_times: list[float] = []
        metric_scores_map: dict[str, list[float]] = defaultdict(list)
        status_counts: dict[str, int] = defaultdict(int)

        status_counts[EvaluationStatus.PASS.value] = 0
        status_counts[EvaluationStatus.WARNING.value] = 0
        status_counts[EvaluationStatus.FAIL.value] = 0

        for result in results:
            eval_resp = result.evaluation_response
            overall_scores.append(eval_resp.overall_score)
            execution_times.append(result.execution_time_ms)

            status_counts[eval_resp.status.value] += 1

            if isinstance(eval_resp.metrics, dict):
                for m_name, m_score in eval_resp.metrics.items():
                    metric_scores_map[m_name].append(m_score)
            else:
                for metric in eval_resp.metrics:
                    m_name = getattr(metric, "name", str(metric))
                    m_score = getattr(metric, "score", 0.0)
                    metric_scores_map[m_name].append(m_score)

        avg_score = min(1.0, max(0.0, statistics.fmean(overall_scores)))
        avg_exec_time = max(0.0, statistics.fmean(execution_times))
        metric_averages = cls._compute_metric_averages(metric_scores_map)

        return BenchmarkStatistics(
            total_samples=total_samples,
            passed_samples=status_counts[EvaluationStatus.PASS.value],
            warning_samples=status_counts[EvaluationStatus.WARNING.value],
            failed_samples=status_counts[EvaluationStatus.FAIL.value],
            average_score=avg_score,
            average_execution_time_ms=avg_exec_time,
            metric_averages=metric_averages,
            status_distribution=dict(status_counts),
        )
