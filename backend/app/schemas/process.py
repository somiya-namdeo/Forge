from pydantic import BaseModel, HttpUrl

class ProcessRequest(BaseModel):
    """Schema for the processing API request."""
    url: HttpUrl
    html_content: str

class ProcessResponse(BaseModel):
    """Schema for the processing API response."""
    status: str
    message: str
