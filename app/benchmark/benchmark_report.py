"""Benchmark report builder module assembling evaluation reports."""

from datetime import datetime, timezone

from app.benchmark.benchmark_models import (
    BenchmarkReport,
    BenchmarkSampleResult,
)
from app.benchmark.benchmark_statistics import BenchmarkStatisticsEngine
from app.schemas.evaluation import EvaluationProvider


class BenchmarkReportBuilder:
    """Builder responsible for assembling complete BenchmarkReport instances."""

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
        results: list[BenchmarkSampleResult],
        started_at: datetime,
        completed_at: datetime,
        metadata: dict[str, str] | None = None,
    ) -> BenchmarkReport:
        """Assemble a complete BenchmarkReport from evaluation sample results."""
        statistics = self.statistics_engine.compute(results)

        utc_started_at = self._ensure_utc(started_at)
        utc_completed_at = self._ensure_utc(completed_at)

        return BenchmarkReport(
            benchmark_name=benchmark_name,
            benchmark_version="1.0.0",
            provider=provider,
            started_at=utc_started_at,
            completed_at=utc_completed_at,
            statistics=statistics,
            results=results,
            metadata=metadata or {},
        )
