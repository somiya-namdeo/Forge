"""
Evaluation Pydantic v2 Schemas.

Contains data validation models for evaluation requests, results, metric configurations,
quality gate thresholds, report generation, and historical filters.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from backend.app.metrics import EvaluationProvider, MetricType, PassFailStatus
from backend.app.thresholds import ThresholdOperator
from backend.app.utils.weighting import WeightPreset


class MetricConfigSchema(BaseModel):
    """Pydantic v2 schema for individual metric evaluation settings."""

    metric_type: MetricType = Field(..., description="Type of evaluation metric.")
    provider: EvaluationProvider = Field(
        default=EvaluationProvider.RAGAS,
        description="Provider framework used to calculate metric.",
    )
    weight: float = Field(default=1.0, ge=0.0, le=10.0, description="Metric weight for score calculation.")
    threshold: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Optional minimum threshold score.")

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "metric_type": "faithfulness",
                "provider": "ragas",
                "weight": 1.0,
                "threshold": 0.8,
            }
        },
    )


class ThresholdConfigSchema(BaseModel):
    """Pydantic v2 schema for quality gate threshold rules."""

    metric_type: MetricType = Field(..., description="Target metric for threshold.")
    target_score: float = Field(..., ge=0.0, le=1.0, description="Target score value.")
    operator: ThresholdOperator = Field(
        default=ThresholdOperator.GREATER_THAN_OR_EQUAL,
        description="Comparison operator for evaluation.",
    )
    warning_score: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Warning threshold boundary score."
    )

    model_config = ConfigDict(frozen=True)


class EvaluationSampleSchema(BaseModel):
    """Pydantic v2 schema for a single evaluation test input sample."""

    sample_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique sample identifier UUID.")
    query: str = Field(..., description="User query or prompt input.")
    expected_output: Optional[str] = Field(default=None, description="Golden expected answer.")
    contexts: List[str] = Field(default_factory=list, description="Ground truth or retrieved reference contexts.")
    actual_output: Optional[str] = Field(default=None, description="RAG system response under evaluation.")
    retrieved_contexts: List[str] = Field(
        default_factory=list, description="Context chunks retrieved by system under evaluation."
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata tags.")

    model_config = ConfigDict(frozen=True)


class EvaluationRequest(BaseModel):
    """Pydantic v2 request schema for triggering an evaluation run."""

    evaluation_name: str = Field(..., description="Descriptive name for evaluation job.")
    rag_architecture_id: str = Field(..., description="ID of candidate RAG architecture being evaluated.")
    dataset_id: Optional[str] = Field(default=None, description="Dataset ID if using a pre-loaded dataset.")
    samples: List[EvaluationSampleSchema] = Field(
        default_factory=list, description="List of evaluation samples if inline."
    )
    metrics: List[MetricConfigSchema] = Field(
        default_factory=list, description="Explicit metric settings list."
    )
    weight_preset: WeightPreset = Field(
        default=WeightPreset.BALANCED_RAG, description="Preset weighting profile."
    )
    custom_thresholds: List[ThresholdConfigSchema] = Field(
        default_factory=list, description="Custom quality gate thresholds."
    )
    async_execution: bool = Field(
        default=False, description="Flag indicating async background execution."
    )

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "evaluation_name": "Legal RAG Benchmark Run",
                "rag_architecture_id": "arch_hybrid_rerank_v1",
                "weight_preset": "balanced_rag",
                "async_execution": False,
                "samples": [
                    {
                        "query": "What is the termination notice period?",
                        "actual_output": "The notice period is 30 days.",
                        "contexts": ["Section 4: Termination requires 30 days written notice."],
                    }
                ],
            }
        },
    )


class EvaluationBatchRequest(BaseModel):
    """Pydantic v2 request schema for batch architecture evaluations."""

    evaluation_name: str = Field(..., description="Batch job identifier name.")
    rag_architecture_ids: List[str] = Field(..., description="List of architecture IDs to compare.")
    dataset_id: str = Field(..., description="Benchmark dataset ID.")
    weight_preset: WeightPreset = Field(default=WeightPreset.BALANCED_RAG, description="Preset weights.")

    model_config = ConfigDict(frozen=True)


class MetricResultSchema(BaseModel):
    """Pydantic v2 schema for individual metric execution result."""

    metric_type: MetricType = Field(..., description="Evaluated metric enum.")
    provider: EvaluationProvider = Field(..., description="Provider used.")
    score: float = Field(..., ge=0.0, le=1.0, description="Calculated metric score.")
    status: PassFailStatus = Field(default=PassFailStatus.PASS, description="Pass/Fail status.")
    latency_ms: float = Field(default=0.0, description="Execution time in milliseconds.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic data or error message.")

    model_config = ConfigDict(frozen=True)


class SampleEvaluationResultSchema(BaseModel):
    """Pydantic v2 schema for single sample evaluation result containing metric breakdowns."""

    sample_id: str = Field(..., description="Sample UUID.")
    query: str = Field(..., description="Input prompt query.")
    sample_score: float = Field(..., ge=0.0, le=1.0, description="Weighted composite score for this sample.")
    metric_results: List[MetricResultSchema] = Field(
        default_factory=list, description="Per-metric evaluation details."
    )

    model_config = ConfigDict(frozen=True)


class ThresholdResultSchema(BaseModel):
    """Pydantic v2 schema for threshold check result."""

    metric_type: MetricType = Field(..., description="Evaluated metric.")
    score: float = Field(..., description="Calculated score.")
    target_score: float = Field(..., description="Required threshold score.")
    operator: ThresholdOperator = Field(..., description="Comparison operator.")
    status: PassFailStatus = Field(..., description="Result status.")
    message: str = Field(default="", description="Explanatory text.")

    model_config = ConfigDict(frozen=True)


class EvaluationResponse(BaseModel):
    """Pydantic v2 response schema for evaluation execution endpoint."""

    evaluation_id: str = Field(..., description="Unique evaluation execution UUID.")
    evaluation_name: str = Field(..., description="Name of evaluation job.")
    rag_architecture_id: str = Field(..., description="Evaluated RAG architecture ID.")
    composite_score: float = Field(..., ge=0.0, le=1.0, description="Final weighted composite score.")
    overall_status: PassFailStatus = Field(..., description="Overall Pass/Fail status across quality gates.")
    sample_results: List[SampleEvaluationResultSchema] = Field(
        default_factory=list, description="Per-sample evaluation results."
    )
    metric_summary: Dict[str, float] = Field(
        default_factory=dict, description="Aggregate metric scores summary dictionary."
    )
    threshold_results: List[ThresholdResultSchema] = Field(
        default_factory=list, description="Quality gate threshold audit results."
    )
    execution_time_seconds: float = Field(default=0.0, description="Total execution time in seconds.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp.")

    model_config = ConfigDict(frozen=True)


class EvaluationHistoryFilter(BaseModel):
    """Pydantic v2 schema for querying evaluation history."""

    rag_architecture_id: Optional[str] = Field(default=None, description="Filter by architecture ID.")
    status: Optional[PassFailStatus] = Field(default=None, description="Filter by Pass/Fail status.")
    min_composite_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Min composite score.")
    limit: int = Field(default=50, ge=1, le=500, description="Pagination limit.")
    offset: int = Field(default=0, ge=0, description="Pagination offset.")

    model_config = ConfigDict(frozen=True)


class ReportRequestSchema(BaseModel):
    """Pydantic v2 request schema for generating report."""

    evaluation_id: str = Field(..., description="Evaluation ID to generate report for.")
    include_recommendations: bool = Field(default=True, description="Flag to include AI recommendations.")

    model_config = ConfigDict(frozen=True)


class ReportResponseSchema(BaseModel):
    """Pydantic v2 response schema for evaluation report."""

    report_id: str = Field(..., description="Generated report UUID.")
    evaluation_id: str = Field(..., description="Associated evaluation UUID.")
    title: str = Field(..., description="Report title.")
    summary: str = Field(..., description="Executive summary.")
    overall_status: PassFailStatus = Field(..., description="Evaluation status.")
    composite_score: float = Field(..., description="Composite evaluation score.")
    metric_breakdown: Dict[str, float] = Field(..., description="Per-metric scores.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations list.")

    model_config = ConfigDict(frozen=True)
