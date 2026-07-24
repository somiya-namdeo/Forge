from bs4 import BeautifulSoup
from typing import Optional, List
from urllib.parse import urljoin

class WebsiteParser:
    @staticmethod
    def extract_title(html: str) -> Optional[str]:
        """Extracts the page title from raw HTML."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            return title_tag.string.strip() if title_tag and title_tag.string else None
        except Exception:
            return None
            
    @staticmethod
    def extract_links(base_url: str, html: str) -> List[str]:
        """Extracts all hyperlinks from raw HTML and resolves them to absolute URLs."""
        try:
            soup = BeautifulSoup(html, "html.parser")
            links = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"]
                full_url = urljoin(base_url, href)
                links.append(full_url)
            return links
        except Exception:
            return []
