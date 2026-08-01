"""Benchmark data models for Forge evaluation framework."""

from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    PositiveInt,
)

from app.schemas.evaluation import (
    EvaluationProvider,
    EvaluationResponse,
    MetricConfig,
    ThresholdConfig,
)


class BenchmarkSample(BaseModel):
    """Single evaluation sample within a benchmark dataset."""

    sample_id: str = Field(..., description="Unique identifier for the benchmark sample.")
    category: str = Field(..., description="Domain category or subject area of the sample.")
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Difficulty level of the evaluation prompt.")
    question: str = Field(..., description="Question or prompt for evaluation.")
    contexts: list[str] = Field(..., description="Retrieved context document chunks.")
    ground_truth: str = Field(..., description="Reference ground truth answer.")
    expected_answer: str | None = Field(default=None, description="Optional expected reference output.")

    model_config = ConfigDict(frozen=True)


class BenchmarkRunConfig(BaseModel):
    """Configuration parameters for executing a benchmark run."""

    provider: EvaluationProvider = Field(default=EvaluationProvider.RAGAS, description="Evaluation provider framework.")
    metric_config: list[MetricConfig] | None = Field(default=None, description="Optional metric configuration overrides.")
    threshold_config: ThresholdConfig | None = Field(default=None, description="Optional quality gate threshold overrides.")
    parallel_workers: PositiveInt = Field(default=4, description="Number of parallel worker execution threads.")
    shuffle: bool = Field(default=False, description="Flag to shuffle evaluation sample ordering.")
    max_samples: PositiveInt | None = Field(default=None, description="Maximum number of samples to execute.")

    model_config = ConfigDict(frozen=True)


class BenchmarkSampleResult(BaseModel):
    """Evaluation result for an individual benchmark sample."""

    sample_id: str = Field(..., description="Identifier matching the evaluated sample.")
    evaluation_response: EvaluationResponse = Field(..., description="Evaluation output response payload.")
    execution_time_ms: NonNegativeFloat = Field(..., description="Total execution duration in milliseconds.")

    model_config = ConfigDict(frozen=True)


class BenchmarkStatistics(BaseModel):
    """Aggregated statistical summary across benchmark sample runs."""

    total_samples: NonNegativeInt = Field(..., description="Total number of evaluated samples.")
    passed_samples: NonNegativeInt = Field(..., description="Number of samples passing quality gates.")
    warning_samples: NonNegativeInt = Field(default=0, description="Number of samples with warning status.")
    failed_samples: NonNegativeInt = Field(..., description="Number of samples failing quality gates.")
    average_score: float = Field(..., ge=0.0, le=1.0, description="Mean overall score across samples.")
    average_execution_time_ms: NonNegativeFloat = Field(..., description="Mean sample execution time in milliseconds.")
    metric_averages: dict[str, float] = Field(default_factory=dict, description="Mean score breakdown per metric.")
    status_distribution: dict[str, int] = Field(default_factory=dict, description="Count distribution per evaluation status.")

    model_config = ConfigDict(frozen=True)


class BenchmarkReport(BaseModel):
    """Complete summary report detailing benchmark execution and results."""

    benchmark_name: str = Field(..., description="Name of the benchmark suite.")
    benchmark_version: str = Field(default="1.0.0", description="Version of the benchmark suite.")
    provider: EvaluationProvider = Field(..., description="Evaluation provider utilized for the run.")
    started_at: datetime = Field(..., description="UTC timestamp marking when benchmark execution started.")
    completed_at: datetime = Field(..., description="UTC timestamp marking when benchmark execution completed.")
    statistics: BenchmarkStatistics = Field(..., description="Aggregated benchmark statistics summary.")
    results: list[BenchmarkSampleResult] = Field(..., description="Detailed sample evaluation results list.")
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional benchmark metadata.")

    model_config = ConfigDict(frozen=True)
