from pydantic import BaseModel, HttpUrl
from typing import Optional

class IngestRequest(BaseModel):
    url: HttpUrl
    max_depth: Optional[int] = None
    max_pages: Optional[int] = None
    
class IngestResponse(BaseModel):
    source: str
    pages_discovered: int
    pages_downloaded: int
    pages_failed: int
    duration_seconds: float
