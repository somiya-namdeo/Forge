from fastapi import FastAPI
from app.api.router import router as api_router
from app.config.settings import settings
from app.observability.logging import setup_logging

def create_app() -> FastAPI:
    """
    Application factory pattern.
    Configures logging, CORS, and registers API routers.
    """
    # Initialize telemetry/logging before handling requests
    setup_logging()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Forge AI Engineering Research Assistant",
    )
    
    app.include_router(api_router, prefix="/api")
    
    return app

app = create_app()
