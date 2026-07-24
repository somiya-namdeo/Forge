import httpx
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from collections import deque

from app.connectors.base import BaseConnector
from app.connectors.website.discovery import WebsiteDiscovery
from app.connectors.website.downloader import WebsiteDownloader
from app.connectors.website.parser import WebsiteParser
from app.connectors.website.models import PageMetadata
from app.connectors.website.utils import get_domain, hash_string, normalize_url
from app.storage.base import BaseStorage
from app.config.settings import settings

logger = logging.getLogger("forge.connectors.website")

class WebsiteConnector(BaseConnector):
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.discovery = WebsiteDiscovery()
        self.parser = WebsiteParser()

    async def ingest(self, url: str, max_depth: int = None, max_pages: int = None) -> Dict[str, Any]:
        max_depth = max_depth if max_depth is not None else settings.CRAWL_MAX_DEPTH
        max_pages = max_pages if max_pages is not None else settings.CRAWL_MAX_PAGES
        
        logger.info(f"Starting ingestion for: {url}")
        
        start_time = datetime.utcnow()
        base_domain = get_domain(url)
        normalized_start = normalize_url(url)
        
        visited = set()
        queued = {normalized_start}
        queue = deque([(normalized_start, 0)])
        
        pages_discovered = 0
        pages_downloaded = 0
        pages_failed = 0
        
        from crawl4ai import AsyncWebCrawler
        async with AsyncWebCrawler() as crawler:
            downloader = WebsiteDownloader(crawler)
            
            while queue and pages_discovered < max_pages:
                current_url, depth = queue.popleft()
                
                if current_url in visited:
                    continue
                    
                visited.add(current_url)
                pages_discovered += 1
                logger.info(f"Discovered: {current_url} at depth {depth}")
                
                try:
                    # Download
                    status, content_type, html = await downloader.download(current_url)
                    
                    if "text/html" not in content_type:
                        logger.warning(f"Skipping non-HTML content at {current_url}")
                        continue
                        
                    pages_downloaded += 1
                    logger.info(f"Downloaded: {current_url} ({status})")
                    
                    # Parse Metadata
                    title = self.parser.extract_title(html)
                    metadata = PageMetadata(
                        url=current_url,
                        title=title,
                        source="website",
                        crawl_timestamp=datetime.utcnow().isoformat(),
                        http_status=status,
                        content_type=content_type
                    )
                    
                    # Save via Storage Abstraction
                    domain_hash = hash_string(base_domain)
                    url_hash = hash_string(current_url)
                    
                    file_loc = await self.storage.save_raw_document(
                        domain_hash=domain_hash,
                        url_hash=url_hash,
                        content=html,
                        metadata=metadata.model_dump()
                    )
                    logger.debug(f"Saved {current_url} to {file_loc}")
                    
                    # Discover more links if under max_depth
                    if depth < max_depth:
                        all_links = self.parser.extract_links(current_url, html)
                        valid_links = self.discovery.filter_links(all_links, base_domain, visited)
                        
                        for link in valid_links:
                            if link not in queued:  
                                queued.add(link)
                                queue.append((link, depth + 1))
                                
                    # Rate Limiter
                    await asyncio.sleep(settings.CRAWL_DELAY_SECONDS)
                    
                except Exception as e:
                    pages_failed += 1
                    logger.error(f"Failed to process {current_url}: {e}")
                    
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"Crawl completed. Downloaded: {pages_downloaded}, Failed: {pages_failed}")
        
        return {
            "source": base_domain,
            "pages_discovered": pages_discovered,
            "pages_downloaded": pages_downloaded,
            "pages_failed": pages_failed,
            "duration_seconds": duration
        }
