from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration via environment variables.
    Pydantic automatically reads from the .env file.
    """
    PROJECT_NAME: str = "Forge API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Crawler configurations
    CRAWL_MAX_DEPTH: int = 2
    CRAWL_MAX_PAGES: int = 100
    CRAWL_TIMEOUT_SECONDS: int = 10
    CRAWL_DELAY_SECONDS: float = 1.0
    CRAWL_USER_AGENT: str = "ForgeBot/2.0 (+https://github.com/forge)"
    
    # Ensures it loads from .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instantiate settings to be imported across the app
settings = Settings()
