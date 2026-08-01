"""Benchmark service orchestrating complete benchmark workflows."""

from datetime import datetime, timezone
from pathlib import Path

from app.benchmark.benchmark_models import (
    BenchmarkReport,
    BenchmarkRunConfig,
)
from app.benchmark.benchmark_report import BenchmarkReportBuilder
from app.benchmark.benchmark_runner import BenchmarkRunner
from app.datasets.benchmark_loader import BenchmarkLoader
from app.services.evaluation_service import EvaluationService


class BenchmarkService:
    """Service orchestrating benchmark dataset loading, execution, and report generation."""

    def __init__(
        self,
        evaluation_service: EvaluationService,
        loader: BenchmarkLoader,
        runner: BenchmarkRunner,
        report_builder: BenchmarkReportBuilder,
    ) -> None:
        """Initialize benchmark service with injected dependencies."""
        self.evaluation_service = evaluation_service
        self.loader = loader
        self.runner = runner
        self.report_builder = report_builder

    def run_benchmark(
        self,
        benchmark_name: str,
        config: BenchmarkRunConfig,
        dataset_path: str | Path | None = None,
        metadata: dict[str, str] | None = None,
    ) -> BenchmarkReport:
        """Execute a complete benchmark run and produce a structured report."""
        started_at = datetime.now(timezone.utc)

        results = self.runner.run(
            benchmark_name=benchmark_name,
            config=config,
            dataset_path=dataset_path,
        )

        completed_at = datetime.now(timezone.utc)
        provider = config.provider

        return self.report_builder.build(
            benchmark_name=benchmark_name,
            provider=provider,
            results=results,
            started_at=started_at,
            completed_at=completed_at,
            metadata=metadata,
        )
