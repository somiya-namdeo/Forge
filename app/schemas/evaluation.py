"""Evaluation Pydantic v2 Schemas.

Contains data validation models for single-sample evaluation requests and responses,
metric configurations, quality gate thresholds, and historical filters.
"""

from datetime import datetime, timezone
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


# =====================================================================
# Phase 1 Expanded Evaluation Schemas
# =====================================================================


class RetrievalMetricsSchema(BaseModel):
    """Pydantic v2 schema for retrieval accuracy and ranking metrics."""

    precision_at_k: float = Field(default=0.0, ge=0.0, le=1.0, description="Precision@K score.")
    recall_at_k: float = Field(default=0.0, ge=0.0, le=1.0, description="Recall@K score.")
    hit_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Hit Rate score.")
    mrr: float = Field(default=0.0, ge=0.0, le=1.0, description="Mean Reciprocal Rank score.")
    ndcg: float = Field(default=0.0, ge=0.0, le=1.0, description="Normalized Discounted Cumulative Gain score.")

    model_config = ConfigDict(frozen=True)


class GenerationMetricsSchema(BaseModel):
    """Pydantic v2 schema for RAG generation quality and factual alignment metrics."""

    faithfulness: float = Field(default=0.0, ge=0.0, le=1.0, description="Faithfulness score.")
    answer_relevancy: float = Field(default=0.0, ge=0.0, le=1.0, description="Answer Relevancy score.")

    model_config = ConfigDict(frozen=True)


class OperationalMetricsSchema(BaseModel):
    """Pydantic v2 schema for system performance, latency, and resource utilization metrics."""

    retrieval_latency_ms: float = Field(default=0.0, ge=0.0, description="Retrieval latency in milliseconds.")
    generation_latency_ms: float = Field(default=0.0, ge=0.0, description="Generation latency in milliseconds.")
    total_latency_ms: float = Field(default=0.0, ge=0.0, description="Total execution latency in milliseconds.")
    prompt_tokens: int = Field(default=0, ge=0, description="Input prompt token count.")
    completion_tokens: int = Field(default=0, ge=0, description="Output completion token count.")
    total_tokens: int = Field(default=0, ge=0, description="Total token consumption.")
    estimated_cost_usd: float = Field(default=0.0, ge=0.0, description="Estimated USD cost.")
    throughput_tokens_per_second: float = Field(
        default=0.0, ge=0.0, description="Generation throughput in tokens/sec."
    )

    model_config = ConfigDict(frozen=True)


class EvaluationSummarySchema(BaseModel):
    """Pydantic v2 schema for high-level evaluation summary and diagnostic feedback."""

    overall_score: float = Field(..., ge=0.0, le=1.0, description="Composite evaluation score.")
    status: PassFailStatus = Field(default=PassFailStatus.PASS, description="Pass/Fail status across quality gates.")
    metric_weights: Dict[str, float] = Field(default_factory=dict, description="Weights assigned per metric.")
    strengths: List[str] = Field(default_factory=list, description="Identified architecture strengths.")
    weaknesses: List[str] = Field(default_factory=list, description="Identified architecture weaknesses.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable optimization recommendations.")

    model_config = ConfigDict(frozen=True)


class ComprehensiveEvaluationReport(BaseModel):
    """Pydantic v2 comprehensive evaluation report schema consumable by Benchmark and Comparison modules."""

    evaluation_id: str = Field(
        default_factory=lambda: str(uuid4()), description="Unique evaluation execution UUID."
    )
    evaluation_version: str = Field(default="2.0", description="Evaluation module version identifier.")
    provider: Any = Field(
        default=EvaluationProvider.RAGAS, description="Provider framework utilized."
    )
    overall_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Final composite or primary evaluation score."
    )
    quality_grade: str = Field(
        default="F", description="Letter grade: A+, A, B, C, D, F."
    )
    deployment_readiness: str = Field(
        default="Research Only",
        description="Deployment readiness tier: Production Ready, Pilot Ready, Prototype, Experimental, Research Only.",
    )
    status: PassFailStatus = Field(
        default=PassFailStatus.PASS, description="Pass/Fail/Warning status across quality gates."
    )
    summary: Optional[EvaluationSummarySchema] = Field(
        default=None, description="Detailed diagnostic evaluation summary."
    )
    retrieval: RetrievalMetricsSchema = Field(
        default_factory=RetrievalMetricsSchema, description="Retrieval accuracy and rank metrics."
    )
    generation: GenerationMetricsSchema = Field(
        default_factory=GenerationMetricsSchema, description="Generation quality and alignment metrics."
    )
    operational: OperationalMetricsSchema = Field(
        default_factory=OperationalMetricsSchema, description="Performance and latency metrics."
    )
    metrics: Dict[str, float] = Field(
        default_factory=dict, description="Flat map of metric scores for backward compatibility."
    )
    # Metric execution tracking
    total_metrics: int = Field(default=0, description="Total number of metric calculators executed.")
    successful_metrics: List[str] = Field(default_factory=list, description="Names of successfully computed metrics.")
    failed_metrics: List[str] = Field(default_factory=list, description="Names of failed metric calculations.")
    metric_execution_summary: Dict[str, Any] = Field(
        default_factory=dict, description="Per-metric execution details (provider_used, latency_ms, success)."
    )
    provider_summary: Dict[str, List[str]] = Field(
        default_factory=dict, description="Map of provider name to list of metrics it computed."
    )
    providers_used: List[str] = Field(default_factory=list, description="List of distinct providers used.")
    fallback_metrics: List[str] = Field(
        default_factory=list, description="Metrics that fell back to deterministic calculation."
    )
    average_metric_latency_ms: float = Field(
        default=0.0, description="Average latency in ms across all metric executions."
    )
    execution_time_ms: float = Field(default=0.0, description="Total execution duration in milliseconds.")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="Timezone-aware creation timestamp."
    )

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


# Property aliases & class exports for Phase 1 backward compatibility
RetrievalMetrics = RetrievalMetricsSchema
GenerationMetrics = GenerationMetricsSchema
OperationalMetrics = OperationalMetricsSchema
EvaluationSummary = EvaluationSummarySchema
EvaluationResponse = ComprehensiveEvaluationReport
EvaluationReport = ComprehensiveEvaluationReport


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
