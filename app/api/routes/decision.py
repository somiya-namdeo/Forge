from fastapi import APIRouter, HTTPException

from app.schemas.request import DecisionRequest
from app.schemas.response import DecisionResponse
from app.services.decision_service import DecisionService

router = APIRouter(prefix="/decision", tags=["Decision"])

service = DecisionService()


@router.post("", response_model=DecisionResponse)
def generate_decision(request: DecisionRequest) -> DecisionResponse:
    try:
        return service.generate_decision(request)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )