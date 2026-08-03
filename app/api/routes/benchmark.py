"""FastAPI router for Forge benchmark execution module."""

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
    summary="Execute Benchmark Suite",
    description="Run evaluation benchmark samples across dataset configurations.",
)
def run_benchmark(
    config: BenchmarkRunConfig,
    benchmark_name: str = "Forge Benchmark",
    service: BenchmarkService = Depends(get_benchmark_service),
) -> BenchmarkReport:
    """Execute benchmark run request and return summary report."""
    try:
        return service.run_benchmark(
            benchmark_name=benchmark_name,
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
