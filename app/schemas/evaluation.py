"""
Evaluation Pydantic v2 Schemas.

Contains data validation models for single-sample evaluation requests and responses,
metric configurations, quality gate thresholds, and historical filters.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from app.metrics import EvaluationProvider, MetricType, PassFailStatus
from app.thresholds import ThresholdOperator


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


MetricConfig = MetricConfigSchema
ThresholdConfig = ThresholdConfigSchema
EvaluationStatus = PassFailStatus


class EvaluationRequest(BaseModel):
    """Pydantic v2 request schema for evaluating a single RAG response."""

    question: str = Field(..., description="User question or prompt input.")
    answer: str = Field(..., description="RAG system generated response answer.")
    contexts: List[str] = Field(default_factory=list, description="Retrieved context document chunks.")
    ground_truth: Optional[str] = Field(default=None, description="Expected golden reference answer.")
    provider: EvaluationProvider = Field(
        default=EvaluationProvider.RAGAS,
        description="Target evaluation provider framework.",
    )
    metric_config: Optional[List[MetricConfigSchema]] = Field(
        default=None, description="Optional metric configuration list."
    )
    threshold_config: Optional[List[ThresholdConfigSchema]] = Field(
        default=None, description="Optional quality gate threshold rules."
    )

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "question": "What is the termination notice period?",
                "answer": "The notice period for termination is 30 days.",
                "contexts": ["Section 4: Termination requires 30 days written notice."],
                "ground_truth": "30 days written notice.",
                "provider": "ragas",
            }
        },
    )


class MetricResultSchema(BaseModel):
    """Pydantic v2 schema for individual metric execution result."""

    metric_type: MetricType = Field(..., description="Evaluated metric enum.")
    provider: EvaluationProvider = Field(..., description="Provider used.")
    score: float = Field(..., ge=0.0, le=1.0, description="Calculated metric score.")
    status: PassFailStatus = Field(default=PassFailStatus.PASS, description="Pass/Fail status.")
    latency_ms: float = Field(default=0.0, description="Execution time in milliseconds.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Diagnostic data or error message.")

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
    """Pydantic v2 response schema for single RAG evaluation execution."""

    evaluation_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique evaluation execution UUID."
    )
    provider: EvaluationProvider = Field(..., description="Provider framework utilized.")
    overall_score: float = Field(
        ..., ge=0.0, le=1.0, description="Final composite or primary evaluation score."
    )
    status: PassFailStatus = Field(..., description="Pass/Fail/Warning status across quality gates.")
    metrics: Dict[str, float] = Field(
        default_factory=dict, description="Per-metric calculated scores dictionary."
    )
    execution_time_ms: float = Field(default=0.0, description="Total execution duration in milliseconds.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp.")

    model_config = ConfigDict(frozen=True)

    @property
    def composite_score(self) -> float:
        return self.overall_score

    @property
    def overall_status(self) -> PassFailStatus:
        return self.status

    @property
    def metric_summary(self) -> Dict[str, float]:
        return self.metrics

    @property
    def execution_time_seconds(self) -> float:
        return self.execution_time_ms / 1000.0


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
