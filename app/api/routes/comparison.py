"""FastAPI router for Forge architecture comparison module."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_comparison_service
from app.comparison.comparison_models import (
    ComparisonRequest,
    ComparisonResponse,
)
from app.services.comparison_service import ComparisonService

router = APIRouter(
    prefix="/comparison",
    tags=["Comparison"],
)


@router.post(
    "/run",
    response_model=ComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare RAG Architectures",
    description="Compare multiple benchmarked RAG architectures and return a ranked recommendation.",
)
def run_comparison(
    request: ComparisonRequest,
    service: ComparisonService = Depends(get_comparison_service),
) -> ComparisonResponse:
    """Execute architecture comparison."""
    try:
        return service.compare(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison processing error: {str(exc)}",
        )


@router.post(
    "/report",
    status_code=status.HTTP_200_OK,
    summary="Generate Comparison Report",
    description="Generate a structured report for a completed architecture comparison.",
)
def generate_comparison_report(
    request: ComparisonRequest,
    service: ComparisonService = Depends(get_comparison_service),
) -> dict[str, object]:
    """Generate architecture comparison report."""
    try:
        return service.generate_report(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Comparison report generation failed: {str(exc)}",
        )