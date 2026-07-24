from urllib.robotparser import RobotFileParser
from typing import List, Set
from app.connectors.website.utils import get_domain, normalize_url
from app.config.settings import settings

class WebsiteDiscovery:
    def __init__(self):
        self.robot_parsers = {}
        
    def _get_robot_parser(self, domain: str) -> RobotFileParser:
        if domain not in self.robot_parsers:
            rp = RobotFileParser()
            rp.set_url(f"https://{domain}/robots.txt")
            try:
                # Synchronous read. In a high scale system, we'd use async httpx here,
                # but for Phase 3 urllib is an approved MVP implementation.
                rp.read()
            except Exception:
                pass # Default to allow if robots.txt is missing or unreachable
            self.robot_parsers[domain] = rp
        return self.robot_parsers[domain]
        
    def filter_links(self, links: List[str], base_domain: str, visited: Set[str]) -> List[str]:
        """
        Filters discovered links based on domain match, duplicate checking, and robots.txt.
        """
        valid_links = []
        rp = self._get_robot_parser(base_domain)
        seen_in_this_batch = set()
        
        for link in links:
            normalized = normalize_url(link)
            
            # Prevent duplicates
            if normalized in visited or normalized in seen_in_this_batch:
                continue
            seen_in_this_batch.add(normalized)
                
            # Ignore external domains
            if get_domain(normalized) != base_domain:
                continue
                
            # Respect robots.txt
            if not rp.can_fetch(settings.CRAWL_USER_AGENT, normalized):
                continue
                
            valid_links.append(normalized)
            
        return valid_links
