from fastapi import FastAPI

from app.api.routes.decision import router as decision_router

app = FastAPI(
    title="Forge AI Engineering Decision Platform",
    description=(
        "REST API for AI-powered engineering decision support, architecture"
        " recommendation, and Retrieval-Augmented Generation (RAG)."
    ),
    version="1.0.0",
)

app.include_router(
    decision_router,
    prefix="/api/v1",
    tags=["Decision"],
)


@app.get("/")
def read_root():
    return {
        "name": "Forge",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "forge-api",
    }
