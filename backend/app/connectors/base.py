from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseConnector(ABC):
    """
    Abstract interface for all connectors (Website, GitHub, PDF, etc).
    """
    @abstractmethod
    async def ingest(self, url: str, max_depth: int = 2, max_pages: int = 100) -> Dict[str, Any]:
        """
        Orchestrates the discovery and downloading of content.
        Returns a summary of the ingestion process.
        """
        pass
