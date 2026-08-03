"""
FastAPI Routes Package.

Contains API endpoint routers for evaluation triggers, threshold configuration,
history search, and report generation/exports.
"""

from app.routes.evaluation import router as evaluation_router

__all__ = ["evaluation_router"]
