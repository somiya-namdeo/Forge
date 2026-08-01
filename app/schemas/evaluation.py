"""Evaluation Pydantic v2 schemas and API contracts for Forge."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EvaluationStatus(str, Enum):
    """Evaluation status relative to quality gate thresholds."""

    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


class EvaluationProvider(str, Enum):
    """Supported evaluation provider frameworks."""

    RAGAS = "ragas"
    DEEPEVAL = "deepeval"
    TRULENS = "trulens"
    CUSTOM = "custom"


class MetricResult(BaseModel):
    """Single evaluation metric result against its threshold."""

    name: str = Field(..., description="Name of the evaluated metric.")
    score: float = Field(..., ge=0.0, le=1.0, description="Calculated numerical score for the metric.")
    threshold: float = Field(..., ge=0.0, le=1.0, description="Target threshold value configured for the metric.")
    status: EvaluationStatus = Field(..., description="Evaluation status relative to the target threshold.")
    description: str | None = Field(default=None, description="Optional detailed description or rationale for the metric result.")

    model_config = ConfigDict(frozen=True)


class MetricConfig(BaseModel):
    """Configuration settings for an evaluation metric."""

    metric_name: str = Field(..., description="Unique identifier name of the metric to configure.")
    enabled: bool = Field(default=True, description="Flag indicating whether the metric calculation is enabled.")
    weight: float = Field(default=1.0, ge=0.0, description="Relative weight assigned to the metric for composite score calculation.")

    model_config = ConfigDict(frozen=True)


class ThresholdConfig(BaseModel):
    """Threshold configuration values for supported RAG metrics."""

    faithfulness: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum acceptable threshold score for faithfulness.")
    context_precision: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum acceptable threshold score for context precision.")
    context_recall: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum acceptable threshold score for context recall.")
    answer_relevancy: float = Field(default=0.8, ge=0.0, le=1.0, description="Minimum acceptable threshold score for answer relevancy.")

    model_config = ConfigDict(frozen=True)


class EvaluationRequest(BaseModel):
    """Request payload to evaluate a RAG query execution."""

    question: str = Field(..., min_length=1, description="The original user question or prompt being evaluated.")
    answer: str = Field(..., min_length=1, description="The generated answer or response output from the RAG system.")
    contexts: list[str] = Field(..., min_length=1, description="List of context document chunks retrieved for answer generation.")
    ground_truth: str | None = Field(default=None, description="Optional expected reference answer for factual comparison.")
    provider: EvaluationProvider = Field(
        default=EvaluationProvider.RAGAS,
        description="Evaluation provider framework identifier.",
    )
    metric_config: list[MetricConfig] | None = Field(
        default=None,
        description="Optional list of custom metric configuration overrides.",
    )
    threshold_config: ThresholdConfig | None = Field(
        default=None,
        description="Optional threshold configuration overrides for evaluation quality gates.",
    )

    model_config = ConfigDict(frozen=True)


class EvaluationResponse(BaseModel):
    """Complete output payload of an evaluation run."""

    evaluation_id: UUID = Field(..., description="Unique UUID tracking identifier for the evaluation execution.")
    provider: EvaluationProvider = Field(..., description="Name of the evaluation provider framework utilized.")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Calculated composite overall score across evaluated metrics.")
    status: EvaluationStatus = Field(..., description="Aggregated evaluation status outcome across quality gates.")
    metrics: list[MetricResult] = Field(..., description="List of individual metric evaluation results.")
    execution_time_ms: float = Field(..., gt=0, description="Total duration taken to compute evaluation in milliseconds.")
    created_at: datetime = Field(..., description="UTC timestamp marking when the evaluation run completed.")

    model_config = ConfigDict(frozen=True)


class EvaluationReport(BaseModel):
    """Comprehensive evaluation report with actionable recommendations."""

    summary: str = Field(..., description="Executive summary text highlighting key evaluation findings.")
    response: EvaluationResponse = Field(..., description="Detailed evaluation result payload associated with the report.")
    recommendations: list[str] = Field(..., description="List of actionable engineering recommendations to improve RAG performance.")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata dictionary containing supplemental context.",
    )

    model_config = ConfigDict(frozen=True)
