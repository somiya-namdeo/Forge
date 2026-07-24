from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration via environment variables.
    Pydantic automatically reads from the .env file.
    """
    PROJECT_NAME: str = "Forge API"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Ensures it loads from .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

# Instantiate settings to be imported across the app
settings = Settings()
