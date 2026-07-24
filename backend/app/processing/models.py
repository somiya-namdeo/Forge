from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class ProcessedDocument(BaseModel):
    """
    Represents a fully processed document that is ready for chunking and embedding.
    """
    original_url: str
    markdown_content: str
    title: Optional[str] = None
    processing_timestamp: datetime
    metadata: Dict[str, Any]
