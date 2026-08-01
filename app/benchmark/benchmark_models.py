"""Benchmark data models alias."""

from backend.app.benchmark.benchmark_models import (
    BenchmarkReport,
    BenchmarkRunConfig,
    BenchmarkSample,
    BenchmarkSampleResult,
    BenchmarkStatistics,
)

__all__ = [
    "BenchmarkSample",
    "BenchmarkRunConfig",
    "BenchmarkSampleResult",
    "BenchmarkStatistics",
    "BenchmarkReport",
]
