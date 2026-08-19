"""FastAPI router for Forge Knowledge Base module."""
from typing import Optional
from fastapi import APIRouter, Query, status
from app.schemas.knowledge import KnowledgeRegistryResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])
knowledge_service = KnowledgeService()

@router.get(
    "",
    response_model=KnowledgeRegistryResponse,
    status_code=status.HTTP_200_OK,
    summary="List Knowledge Base Registry",
    description="Retrieve deduplicated components from the vector store with optional filtering.",
)
def get_knowledge_registry(
    category: Optional[str] = Query(None, description="Filter by component category"),
    search: Optional[str] = Query(None, description="Search term for names or descriptions"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(24, ge=1, le=100, description="Items per page"),
) -> KnowledgeRegistryResponse:
    """Execute knowledge base search request."""
    return knowledge_service.get_knowledge_registry(
        category=category,
        search=search,
        page=page,
        page_size=page_size,
    )
