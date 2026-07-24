from typing import Tuple
from crawl4ai import AsyncWebCrawler

class WebsiteDownloader:
    """
    Downloads raw documents using Crawl4AI.
    """
    def __init__(self, crawler: AsyncWebCrawler):
        self.crawler = crawler
        
    async def download(self, url: str) -> Tuple[int, str, str]:
        """
        Downloads the raw document.
        Returns: (http_status, content_type, text_content)
        """
        result = await self.crawler.arun(url=url)
        if not result.success:
            raise Exception(f"Crawl4AI failed to fetch {url}: {result.error_message}")
            
        status = result.status_code if result.status_code else 200
        return status, "text/html", result.html
