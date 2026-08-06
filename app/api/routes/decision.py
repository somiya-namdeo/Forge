"""FastAPI router for Forge AI Architecture Recommendation Engine."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_decision_service
from app.schemas.decision import DecisionRequest, DecisionResponse
from app.schemas.decision_run import DecisionRunRequest
from app.services.decision_service import DecisionService

router = APIRouter(
    prefix="/decision",
    tags=["Decision"],
)


@router.post(
    "/recommend",
    response_model=DecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate AI Architecture Recommendations",
    description="Analyze project requirements, budget, constraints, and priorities to generate tailored AI architecture recommendations.",
)
def generate_recommendations(
    request: DecisionRequest,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionResponse:
    """Process architecture decision request and return component recommendations."""
    try:
        return service.recommend(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision recommendation error: {str(exc)}",
        )

@router.post(
    "/run",
    response_model=DecisionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Architecture Decision Explanations",
    description="Generate detailed reasoning and alternative analysis from recommendation results.",
)
def run_decision_engine(
    request: DecisionRunRequest,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionResponse:
    """Generate reasoning from existing recommendation outputs."""
    try:
        return service.run_decision(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision engine error: {str(exc)}",
        )
