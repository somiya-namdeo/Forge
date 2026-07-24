from fastapi import APIRouter, HTTPException
from app.schemas.process import ProcessRequest, ProcessResponse

router = APIRouter()

@router.post("/process", response_model=ProcessResponse, tags=["Processing"])
async def process_document(request: ProcessRequest):
    """
    Endpoint for processing raw HTML into normalized Markdown with metadata.
    Currently returns 501 Not Implemented.
    """
    # TODO: Initialize FileSystemStorage and DocumentPipeline
    # TODO: Await pipeline.process_document(raw_html, url)
    # TODO: Handle ProcessingError exceptions gracefully
    
    raise HTTPException(status_code=501, detail="Processing pipeline is not yet implemented.")
