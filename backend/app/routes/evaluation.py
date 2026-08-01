"""FastAPI router for Forge evaluation module."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_evaluation_service
from app.schemas.evaluation import EvaluationRequest, EvaluationResponse
from app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.post(
    "/run",
    response_model=EvaluationResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute RAG Evaluation",
    description="Run synchronous RAG evaluation against the requested provider.",
)
def run_evaluation(
    request: EvaluationRequest,
    service: EvaluationService = Depends(get_evaluation_service),
) -> EvaluationResponse:
    """Execute synchronous evaluation request."""
    try:
        return service.evaluate(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation processing error: {str(exc)}",
        )
