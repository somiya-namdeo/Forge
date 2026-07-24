from fastapi import APIRouter, HTTPException
from app.schemas.ingest import IngestRequest, IngestResponse
from app.connectors.website.connector import WebsiteConnector
from app.storage.filesystem import FileSystemStorage
import logging

router = APIRouter()
logger = logging.getLogger("forge.api.ingest")

@router.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_url(request: IngestRequest):
    """
    Triggers the website ingestion process for a given URL.
    """
    try:
        storage = FileSystemStorage()
        connector = WebsiteConnector(storage=storage)
        
        result = await connector.ingest(
            url=str(request.url),
            max_depth=request.max_depth,
            max_pages=request.max_pages
        )
        return IngestResponse(**result)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
