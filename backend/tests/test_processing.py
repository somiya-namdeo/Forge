import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.processing.pipeline import DocumentPipeline
from app.storage.filesystem import FileSystemStorage

@pytest.mark.asyncio
async def test_api_process_not_implemented():
    """Verifies that the API endpoint returns 501 Not Implemented."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/process", json={
            "url": "https://example.com", 
            "html_content": "<html><body>test</body></html>"
        })
        assert response.status_code == 501

def test_pipeline_not_implemented():
    """Verifies that the DocumentPipeline orchestration raises NotImplementedError."""
    pipeline = DocumentPipeline(FileSystemStorage())
    with pytest.raises(NotImplementedError):
        asyncio.run(pipeline.process_document("<html></html>", "https://example.com"))

def test_extractor_not_implemented():
    """Placeholder test for ContentExtractor."""
    from app.processing.extractor import ContentExtractor
    extractor = ContentExtractor()
    with pytest.raises(NotImplementedError):
        extractor.extract("<html></html>")

def test_cleaner_not_implemented():
    """Placeholder test for ContentCleaner."""
    from app.processing.cleaner import ContentCleaner
    cleaner = ContentCleaner()
    with pytest.raises(NotImplementedError):
        cleaner.clean("<html></html>")
