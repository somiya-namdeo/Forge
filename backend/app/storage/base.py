from abc import ABC, abstractmethod

class BaseStorage(ABC):
    @abstractmethod
    async def save_raw_document(self, domain_hash: str, url_hash: str, content: str, metadata: dict) -> str:
        """
        Saves raw document and its metadata.
        Returns the absolute or relative file location.
        """
        pass
