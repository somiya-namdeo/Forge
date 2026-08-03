"""Benchmark data models for Forge evaluation framework."""

from datetime import datetime
from typing import List, Literal, Optional

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

    sample_id: str = Field(default="sample_01", description="Unique identifier for the benchmark sample.")
    category: str = Field(default="general", description="Domain category or subject area of the sample.")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium", description="Difficulty level of the evaluation prompt.")
    question: str = Field(..., description="Question or prompt for evaluation.")
    contexts: List[str] = Field(default_factory=list, description="Retrieved context document chunks.")
    ground_truth: str = Field(default="", description="Reference ground truth answer.")
    expected_answer: Optional[str] = Field(default=None, description="Optional expected reference output.")

    model_config = ConfigDict(frozen=True)


class BenchmarkRunConfig(BaseModel):
    """Configuration parameters and request payload for executing a benchmark run."""

    benchmark_name: str = Field(default="Forge Benchmark Suite", description="Name of the benchmark suite.")
    rag_architecture_id: Optional[str] = Field(default="arch_v1", description="ID of RAG architecture being benchmarked.")
    dataset_id: Optional[str] = Field(default=None, description="Dataset ID if using a pre-loaded dataset.")
    samples: List[BenchmarkSample] = Field(default_factory=list, description="Inline list of evaluation benchmark samples.")
    provider: EvaluationProvider = Field(default=EvaluationProvider.RAGAS, description="Evaluation provider framework.")
    metric_config: Optional[List[MetricConfig]] = Field(default=None, description="Optional metric configuration overrides.")
    threshold_config: Optional[List[ThresholdConfig]] = Field(default=None, description="Optional quality gate threshold overrides.")
    weight_preset: Optional[str] = Field(default="balanced_rag", description="Preset weighting profile.")
    async_execution: bool = Field(default=False, description="Flag indicating async background execution.")
    parallel_workers: PositiveInt = Field(default=4, description="Number of parallel worker execution threads.")
    shuffle: bool = Field(default=False, description="Flag to shuffle evaluation sample ordering.")
    max_samples: Optional[PositiveInt] = Field(default=None, description="Maximum number of samples to execute.")
    limit_samples: Optional[PositiveInt] = Field(default=None, description="Alias limit for max samples.")

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "benchmark_name": "RAG Quality Benchmark",
                "rag_architecture_id": "arch_hybrid_v1",
                "samples": [
                    {
                        "sample_id": "s1",
                        "category": "legal",
                        "difficulty": "medium",
                        "question": "What is the notice period for contract termination?",
                        "contexts": ["Section 4: Termination requires 30 days written notice."],
                        "ground_truth": "30 days written notice."
                    }
                ],
                "provider": "ragas"
            }
        }
    )


BenchmarkRequest = BenchmarkRunConfig


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
    results: List[BenchmarkSampleResult] = Field(..., description="Detailed sample evaluation results list.")
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional benchmark metadata.")

    model_config = ConfigDict(frozen=True)
