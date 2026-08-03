"""Benchmark report builder module assembling complete BenchmarkReport v2.0 instances."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.benchmark.benchmark_models import (
    BenchmarkExecutiveSummary,
    BenchmarkReport,
    BenchmarkSampleResult,
)
from app.benchmark.benchmark_statistics import BenchmarkStatisticsEngine
from app.schemas.evaluation import EvaluationProvider

# ─── Grading thresholds (mirrors EvaluationEngine to stay in sync) ──────────
_GRADE_THRESHOLDS = [
    (0.97, "A+"),
    (0.90, "A"),
    (0.80, "B"),
    (0.70, "C"),
    (0.55, "D"),
]

_READINESS_THRESHOLDS = [
    (0.90, "Production Ready"),
    (0.80, "Pilot Ready"),
    (0.65, "Prototype"),
    (0.50, "Experimental"),
]


def _assign_grade(score: float) -> str:
    """Assign a letter grade from the average benchmark score."""
    for threshold, grade in _GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def _assign_readiness(score: float) -> str:
    """Assign a deployment readiness tier from the average benchmark score."""
    for threshold, tier in _READINESS_THRESHOLDS:
        if score >= threshold:
            return tier
    return "Research Only"


def _rank_samples(
    results: List[BenchmarkSampleResult],
    top_n: int = 3,
) -> tuple[List[str], List[str]]:
    """Return top-N and bottom-N sample IDs sorted by overall_score."""
    if not results:
        return [], []
    ranked = sorted(results, key=lambda r: r.evaluation_response.overall_score, reverse=True)
    best = [r.sample_id for r in ranked[:top_n]]
    worst = [r.sample_id for r in ranked[-top_n:] if r not in ranked[:top_n]]
    # Guard: if fewer than 2*top_n samples, avoid overlapping lists
    if len(results) <= top_n:
        return best, []
    worst = [r.sample_id for r in ranked[-top_n:]]
    return best, worst


def _build_metric_rankings(metric_averages: Dict[str, float]) -> Dict[str, float]:
    """Produce a leaderboard dict sorted by average score descending."""
    return dict(sorted(metric_averages.items(), key=lambda kv: kv[1], reverse=True))


def _build_executive_summary(
    average_score: float,
    quality_grade: str,
    deployment_readiness: str,
    metric_rankings: Dict[str, float],
    top_weaknesses: List[str],
    top_recommendations: List[str],
) -> BenchmarkExecutiveSummary:
    """Construct a concise executive summary from aggregated benchmark results."""
    # Overall verdict
    verdict = (
        f"The benchmarked RAG system achieved an average quality score of "
        f"{average_score:.2f} ({quality_grade}), qualifying for '{deployment_readiness}'."
    )

    # Best / weakest metric from rankings
    best_metric = next(iter(metric_rankings), "") if metric_rankings else ""
    weakest_metric = next(reversed(metric_rankings), "") if metric_rankings else ""

    # Primary bottleneck: first top weakness, or the weakest metric name
    if top_weaknesses:
        bottleneck = top_weaknesses[0]
    elif weakest_metric:
        bottleneck = f"Low score on '{weakest_metric}' metric."
    else:
        bottleneck = "Insufficient data to identify bottleneck."

    # Recommended next action: first top recommendation, or a generic prompt
    if top_recommendations:
        next_action = top_recommendations[0]
    elif weakest_metric:
        next_action = f"Focus on improving '{weakest_metric}' to raise overall score."
    else:
        next_action = "Collect more evaluation samples for a reliable benchmark."

    return BenchmarkExecutiveSummary(
        overall_verdict=verdict,
        best_metric=best_metric,
        weakest_metric=weakest_metric,
        primary_bottleneck=bottleneck,
        recommended_next_action=next_action,
    )


class BenchmarkReportBuilder:
    """Builder responsible for assembling complete BenchmarkReport v2.0 instances.

    Consumes enriched BenchmarkStatistics produced by BenchmarkStatisticsEngine.
    Does NOT execute evaluation metrics or duplicate any evaluation logic.
    """

    def __init__(self, statistics_engine: BenchmarkStatisticsEngine) -> None:
        """Initialize report builder with injected statistics engine dependency."""
        self.statistics_engine = statistics_engine

    @staticmethod
    def _ensure_utc(dt: datetime) -> datetime:
        """Ensure a datetime instance is UTC-aware."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def build(
        self,
        benchmark_name: str,
        provider: EvaluationProvider,
        results: List[BenchmarkSampleResult],
        started_at: datetime,
        completed_at: datetime,
        metadata: Optional[Dict] = None,
    ) -> BenchmarkReport:
        """Assemble a complete BenchmarkReport v2.0 from evaluation sample results.

        All v2.0 fields are populated from pre-computed evaluation data —
        no metric recalculation occurs here.
        """
        # ── Core statistics (enriched) ─────────────────────────────────────
        statistics = self.statistics_engine.compute(results)

        # ── Timestamps ────────────────────────────────────────────────────
        utc_started_at = self._ensure_utc(started_at)
        utc_completed_at = self._ensure_utc(completed_at)

        # ── Quality grading from average score ────────────────────────────
        quality_grade = _assign_grade(statistics.average_score)
        deployment_readiness = _assign_readiness(statistics.average_score)

        # ── Metric leaderboard ────────────────────────────────────────────
        metric_rankings = _build_metric_rankings(statistics.metric_averages)

        # ── Sample rankings (Part 5) ──────────────────────────────────────
        best_performing_samples, worst_performing_samples = _rank_samples(results)

        # ── Executive summary ─────────────────────────────────────────────
        executive_summary = _build_executive_summary(
            average_score=statistics.average_score,
            quality_grade=quality_grade,
            deployment_readiness=deployment_readiness,
            metric_rankings=metric_rankings,
            top_weaknesses=statistics.top_weaknesses,
            top_recommendations=statistics.top_recommendations,
        )

        return BenchmarkReport(
            # ── Existing fields ──────────────────────────────────────────
            benchmark_name=benchmark_name,
            benchmark_version="2.0.0",
            provider=provider,
            started_at=utc_started_at,
            completed_at=utc_completed_at,
            statistics=statistics,
            results=results,
            metadata=metadata or {},
            # ── v2.0 fields ──────────────────────────────────────────────
            quality_grade=quality_grade,
            deployment_readiness=deployment_readiness,
            metric_rankings=metric_rankings,
            best_performing_samples=best_performing_samples,
            worst_performing_samples=worst_performing_samples,
            overall_strengths=statistics.top_strengths,
            overall_weaknesses=statistics.top_weaknesses,
            overall_recommendations=statistics.top_recommendations,
            provider_summary=statistics.provider_summary,
            fallback_rate=statistics.fallback_rate,
            executive_summary=executive_summary,
        )
