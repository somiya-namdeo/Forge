"""FastAPI router for Forge benchmark execution module."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_benchmark_service
from app.benchmark.benchmark_models import (
    BenchmarkReport,
    BenchmarkRunConfig,
)
from app.services.benchmark_service import BenchmarkService

router = APIRouter(
    prefix="/benchmark",
    tags=["Benchmark"],
)


@router.post(
    "/run",
    response_model=BenchmarkReport,
    status_code=status.HTTP_200_OK,
    summary="Execute RAG Benchmark Suite",
    description="Run evaluation benchmark samples across datasets or inline samples.",
)
def run_benchmark(
    config: BenchmarkRunConfig,
    benchmark_name: Optional[str] = None,
    service: BenchmarkService = Depends(get_benchmark_service),
) -> BenchmarkReport:
    """Execute benchmark run request and return aggregate summary report."""
    name = benchmark_name or config.benchmark_name or "Forge Benchmark Suite"
    try:
        return service.run_benchmark(
            benchmark_name=name,
            config=config,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Benchmark execution error: {str(exc)}",
        )
