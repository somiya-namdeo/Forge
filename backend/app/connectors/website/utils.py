import hashlib
from urllib.parse import urlparse

def get_domain(url: str) -> str:
    """Extracts the network location (domain) from a URL."""
    parsed = urlparse(url)
    return parsed.netloc

def hash_string(text: str) -> str:
    """Returns a SHA-256 hash of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def normalize_url(url: str) -> str:
    """Removes fragments and standardizes the URL format."""
    parsed = urlparse(url)
    # Reconstruct without fragment
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if parsed.query:
         normalized += f"?{parsed.query}"
    return normalized.rstrip("/")
