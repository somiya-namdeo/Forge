from fastapi import APIRouter, Depends, HTTPException

from app.schemas.request import DecisionRequest
from app.schemas.response import DecisionResponse
from app.services.decision_service import DecisionService

router = APIRouter(prefix="/decision", tags=["Decision"])

_decision_service: DecisionService | None = None


def get_decision_service() -> DecisionService:
    global _decision_service
    if _decision_service is None:
        _decision_service = DecisionService()
    return _decision_service


@router.post("", response_model=DecisionResponse)
def generate_decision(
    request: DecisionRequest,
    service: DecisionService = Depends(get_decision_service),
) -> DecisionResponse:
    try:
        return service.generate_decision(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )