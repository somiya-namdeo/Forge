import json
from pathlib import Path
import aiofiles
from app.storage.base import BaseStorage

class FileSystemStorage(BaseStorage):
    """
    Local filesystem storage backend for raw documents.
    Files are stored in data/raw/{domain_hash}/{url_hash}.html
    """
    def __init__(self, base_dir: str = "../../data/raw"):
        # Resolve path relative to backend directory or use absolute path
        # In a real environment, this might come from settings.
        # But data/ is at the root of the repo (forge/data/raw)
        # Assuming app is running from forge/backend
        self.base_dir = Path(__file__).parent.parent.parent.parent / "data" / "raw"
        
    async def save_raw_document(self, domain_hash: str, url_hash: str, content: str, metadata: dict) -> str:
        target_dir = self.base_dir / domain_hash
        target_dir.mkdir(parents=True, exist_ok=True)
        
        html_path = target_dir / f"{url_hash}.html"
        json_path = target_dir / f"{url_hash}.json"
        
        async with aiofiles.open(html_path, "w", encoding="utf-8") as f:
            await f.write(content)
            
        async with aiofiles.open(json_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(metadata, indent=2))
            
        return str(html_path.resolve())
