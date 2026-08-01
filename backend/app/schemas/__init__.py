"""
API Schemas Package.

Defines Pydantic v2 data transfer objects (DTOs) for evaluation API requests,
responses, metric settings, threshold configs, and query filters.
"""

from backend.app.schemas.evaluation import (
    EvaluationBatchRequest,
    EvaluationHistoryFilter,
    EvaluationRequest,
    EvaluationResponse,
    MetricConfigSchema,
    MetricResultSchema,
    ReportRequestSchema,
    ReportResponseSchema,
    SampleEvaluationResultSchema,
    ThresholdConfigSchema,
    ThresholdResultSchema,
)

__all__ = [
    "MetricConfigSchema",
    "ThresholdConfigSchema",
    "EvaluationRequest",
    "EvaluationBatchRequest",
    "MetricResultSchema",
    "SampleEvaluationResultSchema",
    "ThresholdResultSchema",
    "EvaluationResponse",
    "EvaluationHistoryFilter",
    "ReportRequestSchema",
    "ReportResponseSchema",
]
