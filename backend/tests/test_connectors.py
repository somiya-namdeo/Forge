import pytest
from httpx import AsyncClient
from app.main import app
from app.connectors.website.utils import get_domain, hash_string, normalize_url
from app.connectors.website.parser import WebsiteParser
from app.connectors.website.discovery import WebsiteDiscovery

def test_get_domain():
    assert get_domain("https://fastapi.tiangolo.com/tutorial/") == "fastapi.tiangolo.com"
    assert get_domain("http://github.com") == "github.com"

def test_normalize_url():
    assert normalize_url("https://example.com/page/#section") == "https://example.com/page"
    assert normalize_url("https://example.com/page/") == "https://example.com/page"

def test_extract_title():
    html = "<html><head><title>Test Title</title></head><body></body></html>"
    parser = WebsiteParser()
    assert parser.extract_title(html) == "Test Title"

def test_extract_links():
    html = '<html><body><a href="/about">About</a><a href="https://other.com/contact">Contact</a></body></html>'
    parser = WebsiteParser()
    links = parser.extract_links("https://example.com", html)
    assert "https://example.com/about" in links
    assert "https://other.com/contact" in links

def test_discovery_filtering():
    discovery = WebsiteDiscovery()
    links = [
        "https://example.com/about",
        "https://example.com/about",  # duplicate
        "https://other.com/contact",  # external
    ]
    visited = set()
    valid = discovery.filter_links(links, "example.com", visited)
    
    assert len(valid) == 1
    assert valid[0] == "https://example.com/about"

from httpx import AsyncClient, ASGITransport

@pytest.mark.asyncio
async def test_api_ingest_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/ingest", json={"url": "not-a-url"})
        assert response.status_code == 422
