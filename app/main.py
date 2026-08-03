from fastapi import FastAPI

from app.api.routes.benchmark import router as benchmark_router
from app.api.routes.decision import router as decision_router
from app.routes.evaluation import router as evaluation_router
from app.api.routes.comparison import router as comparison_router
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
)
app.include_router(
    evaluation_router,
    prefix="/api/v1",
)
app.include_router(
    benchmark_router,
    prefix="/api/v1",
)
app.include_router(
    comparison_router,
    prefix="/api/v1",
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
