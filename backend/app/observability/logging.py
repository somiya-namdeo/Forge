import logging
from app.config.settings import settings

def setup_logging() -> None:
    """
    Configures standard application logging.
    Future telemetry (Langfuse, OTel) will be initialized here.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    logger = logging.getLogger("forge")
    logger.info("Forge Observability Initialized")
