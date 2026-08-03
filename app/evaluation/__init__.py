"""
Forge Evaluation Module.

A clean, scalable, and modular evaluation subsystem for Retrieval-Augmented Generation
(RAG) architectures and AI engineering decisions.

Key Subpackages:
    - metrics: Plug-in metric evaluation providers (RAGAS, DeepEval, TruLens, Custom).
    - datasets: Benchmark loaders and golden dataset primitives.
    - thresholds: Quality gates, threshold managers, and pass/fail rules.
    - reports: Evaluation report generators and PDF/JSON export engines.
    - history: Evaluation run persistence and trend analysis.
    - schemas: Pydantic v2 data models for evaluation requests/responses.
    - services: Orchestration services for evaluation execution.
    - routes: FastAPI API endpoints for evaluation management.
    - utils: Weighted scoring engines and mathematical score aggregators.
"""

__all__ = [
    "metrics",
    "datasets",
    "thresholds",
    "reports",
    "history",
    "schemas",
    "services",
    "routes",
    "utils",
]
