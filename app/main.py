"""Forge AI Engineering Decision Platform - Main FastAPI Application."""

from datetime import datetime, timezone
import logging
from typing import Union

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.decision import router as decision_router
from app.api.routes.reports import router as reports_router
from app.api.routes.knowledge import router as knowledge_router
from app.routes.evaluation import router as evaluation_router
import os

# Configure logger for global exception tracking
logger = logging.getLogger("forge.api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Forge AI Engineering Decision Platform",
    description=(
        "REST API for AI-powered engineering decision support, architecture"
        " recommendation, and Retrieval-Augmented Generation (RAG)."
    ),
    version="1.0.0",
)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
        "https://forge-beta-gilt-16.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def create_error_response(
    status_code: int,
    code: str,
    message: str,
    details: Union[str, list, dict],
) -> JSONResponse:
    """Construct a uniform JSON error response payload adhering to Forge standards."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "timestamp": timestamp,
        },
    }
    return JSONResponse(status_code=status_code, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request payload validation failures (HTTP 422)."""
    logger.warning(
        "Request validation error | Path=%s | Method=%s | Type=%s | Errors=%s",
        request.url.path,
        request.method,
        exc.__class__.__name__,
        str(exc.errors()),
    )
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="VALIDATION_ERROR",
        message="Invalid request payload.",
        details=exc.errors(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle explicit HTTP exceptions, preserving the requested HTTP status code."""
    logger.warning(
        "HTTP exception | Path=%s | Method=%s | Status=%d | Message=%s",
        request.url.path,
        request.method,
        exc.status_code,
        str(exc.detail),
    )
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        422: "UNPROCESSABLE_ENTITY",
        503: "SERVICE_UNAVAILABLE",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return create_error_response(
        status_code=exc.status_code,
        code=code,
        message=str(exc.detail),
        details=str(exc.detail),
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle domain validation errors (HTTP 400)."""
    logger.warning(
        "Value error | Path=%s | Method=%s | Type=%s | Message=%s",
        request.url.path,
        request.method,
        exc.__class__.__name__,
        str(exc),
    )
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="BAD_REQUEST",
        message=str(exc),
        details=str(exc),
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    """Handle infrastructure and runtime execution failures (HTTP 503)."""
    logger.error(
        "Runtime error | Path=%s | Method=%s | Type=%s | Message=%s",
        request.url.path,
        request.method,
        exc.__class__.__name__,
        str(exc),
        exc_info=True,
    )
    return create_error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="SERVICE_UNAVAILABLE",
        message=str(exc),
        details=str(exc),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled server exceptions (HTTP 500)."""
    logger.error(
        "Unhandled server exception | Path=%s | Method=%s | Type=%s | Message=%s",
        request.url.path,
        request.method,
        exc.__class__.__name__,
        str(exc),
        exc_info=True,
    )
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="INTERNAL_SERVER_ERROR",
        message="An internal server error occurred.",
        details=str(exc),
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
    reports_router,
    prefix="/api/v1",
)
app.include_router(
    knowledge_router,
    prefix="/api/v1",
)


@app.get("/")
def read_root():
    """Retrieve system metadata."""
    return {
        "name": "Forge",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "forge-api",
    }
