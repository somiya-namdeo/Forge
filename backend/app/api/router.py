from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.config.settings import settings
from app.api.routes import ingest, process

router = APIRouter()

@router.get("/health", response_model=HealthResponse, tags=["Diagnostics"])
async def health_check():
    """
    Diagnostic endpoint to verify application status.
    """
    return HealthResponse(
        status="healthy",
        version=settings.VERSION
    )
    
router.include_router(ingest.router)
router.include_router(process.router)
