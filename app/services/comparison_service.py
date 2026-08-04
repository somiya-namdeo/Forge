"""
Comparison service for Forge architecture comparison (v2.0).
"""

from typing import Any, Dict
from app.benchmark.benchmark_models import BenchmarkRunConfig
from app.comparison.comparison_engine import ComparisonEngine
from app.comparison.comparison_models import ComparisonRequest, ComparisonResponse
from app.comparison.comparison_report import ComparisonReportBuilder
from app.services.benchmark_service import BenchmarkService


class ComparisonService:
    """Service layer for architecture comparison."""

    def __init__(
        self,
        comparison_engine: ComparisonEngine | None = None,
        report_builder: ComparisonReportBuilder | None = None,
        benchmark_service: BenchmarkService | None = None,
    ) -> None:
        """Initialize comparison service."""
        self.comparison_engine = comparison_engine or ComparisonEngine()
        self.report_builder = report_builder or ComparisonReportBuilder()
        self.benchmark_service = benchmark_service

    def _ensure_benchmarked(self, request: ComparisonRequest) -> ComparisonRequest:
        """Ensure every candidate architecture has an attached BenchmarkReport, executing internal benchmark if omitted."""
        benchmarked_candidates = []
        for candidate in request.architectures:
            if candidate.benchmark_report is not None:
                benchmarked_candidates.append(candidate)
            else:
                bm_service = self.benchmark_service
                if bm_service is None:
                    from app.api.deps import get_benchmark_service
                    bm_service = get_benchmark_service()

                run_cfg = BenchmarkRunConfig(
                    benchmark_name=f"Automated Benchmark - {candidate.architecture_name}",
                    rag_architecture_id=candidate.architecture_id,
                    max_samples=1,
                )
                report = bm_service.run_benchmark(
                    benchmark_name=run_cfg.benchmark_name,
                    config=run_cfg,
                    metadata=candidate.metadata,
                )
                candidate_with_report = candidate.model_copy(update={"benchmark_report": report})
                benchmarked_candidates.append(candidate_with_report)

        return request.model_copy(update={"architectures": benchmarked_candidates})

    def compare(
        self,
        request: ComparisonRequest,
    ) -> ComparisonResponse:
        """Compare architectures (automatically running internal benchmarks if omitted) and return ComparisonResponse."""
        processed_request = self._ensure_benchmarked(request)
        return self.comparison_engine.compare(processed_request)

    def generate_report(
        self,
        request: ComparisonRequest,
    ) -> Dict[str, Any]:
        """Compare architectures and generate structured report payload."""
        comparison = self.compare(request)
        report = self.report_builder.build_report(comparison)
        if hasattr(report, "model_dump"):
            return report.model_dump()
        return dict(report)