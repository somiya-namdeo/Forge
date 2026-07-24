from pydantic import BaseModel
from typing import Optional

class PageMetadata(BaseModel):
    url: str
    title: Optional[str]
    source: str
    crawl_timestamp: str
    http_status: int
    content_type: str
    file_location: Optional[str] = None
