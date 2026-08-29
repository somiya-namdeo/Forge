"""Benchmark data models for Forge evaluation framework."""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

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


class ArchitectureRecord(BaseModel):
    """Pre-recorded benchmark generation results for a specific architecture."""
    generated_answer: str
    contexts: List[str] = Field(default_factory=list)
    execution_time_ms: Optional[float] = None

class BenchmarkSample(BaseModel):
    """Single evaluation sample within a benchmark dataset."""

    sample_id: str = Field(default="sample_01", description="Unique identifier for the benchmark sample.")
    category: str = Field(default="general", description="Domain category or subject area of the sample.")
    difficulty: Literal["easy", "medium", "hard"] = Field(default="medium", description="Difficulty level of the evaluation prompt.")
    question: str = Field(..., description="Question or prompt for evaluation.")
    contexts: List[str] = Field(default_factory=list, description="Retrieved context document chunks (legacy/default).")
    ground_truth: str = Field(default="", description="Reference ground truth answer.")
    expected_answer: Optional[str] = Field(default=None, description="Optional expected reference output.")
    
    architectures: Dict[str, ArchitectureRecord] = Field(
        default_factory=dict,
        description="Architecture-specific pre-recorded generated outputs and contexts."
    )

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
                        "contexts": [
                            "Section 4: Termination requires 30 days written notice."
                        ],
                        "ground_truth": "30 days written notice."
                    }
                ],
                "provider": "ragas"
            }
        },
    )


BenchmarkRequest = BenchmarkRunConfig


class BenchmarkSampleResult(BaseModel):
    """Evaluation result for an individual benchmark sample."""

    sample_id: str = Field(..., description="Identifier matching the evaluated sample.")
    evaluation_response: EvaluationResponse = Field(..., description="Evaluation output response payload.")
    execution_time_ms: NonNegativeFloat = Field(..., description="Total execution duration in milliseconds.")

    model_config = ConfigDict(frozen=True)


class MetricStatistics(BaseModel):
    """Detailed statistical summary for an individual evaluation metric."""

    average: float = Field(..., ge=0.0, le=1.0, description="Average metric score.")
    median: float = Field(..., ge=0.0, le=1.0, description="Median metric score.")
    minimum: float = Field(..., ge=0.0, le=1.0, description="Minimum metric score.")
    maximum: float = Field(..., ge=0.0, le=1.0, description="Maximum metric score.")
    standard_deviation: NonNegativeFloat = Field(..., description="Standard deviation of metric scores.")

    model_config = ConfigDict(frozen=True)


class BenchmarkStatistics(BaseModel):
    """Aggregated statistical summary across benchmark sample runs (v2.0)."""

    # ─── Existing fields (unchanged) ───────────────────────────────────────
    total_samples: NonNegativeInt = Field(..., description="Total number of evaluated samples.")
    passed_samples: NonNegativeInt = Field(..., description="Number of samples passing quality gates.")
    warning_samples: NonNegativeInt = Field(default=0, description="Number of samples with warning status.")
    failed_samples: NonNegativeInt = Field(..., description="Number of samples failing quality gates.")
    average_score: float = Field(..., ge=0.0, le=1.0, description="Average overall score.")
    median_score: float = Field(..., ge=0.0, le=1.0, description="Median overall score.")
    minimum_score: float = Field(..., ge=0.0, le=1.0, description="Minimum overall score.")
    maximum_score: float = Field(..., ge=0.0, le=1.0, description="Maximum overall score.")
    score_standard_deviation: NonNegativeFloat = Field(..., description="Standard deviation of overall scores.")
    average_execution_time_ms: NonNegativeFloat = Field(..., description="Average execution time.")
    median_execution_time_ms: NonNegativeFloat = Field(..., description="Median execution time.")
    minimum_execution_time_ms: NonNegativeFloat = Field(..., description="Minimum execution time.")
    maximum_execution_time_ms: NonNegativeFloat = Field(..., description="Maximum execution time.")
    p95_execution_time_ms: NonNegativeFloat = Field(..., description="95th percentile execution time.")
    success_rate: float = Field(..., ge=0.0, le=1.0, description="Ratio of passed samples.")
    failure_rate: float = Field(..., ge=0.0, le=1.0, description="Ratio of failed samples.")
    metric_averages: Dict[str, float] = Field(
        default_factory=dict,
        description="Average score for each metric.",
    )
    metric_statistics: Dict[str, MetricStatistics] = Field(
        default_factory=dict,
        description="Detailed statistics for every evaluation metric.",
    )
    status_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of evaluation statuses.",
    )

    # ─── New v2.0 fields ───────────────────────────────────────────────────
    grade_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of quality grades across samples (A+, A, B, C, D, F).",
    )
    deployment_readiness_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of deployment readiness tiers across samples.",
    )
    generation_metric_averages: Dict[str, float] = Field(
        default_factory=dict,
        description="Average scores for generation metrics (faithfulness, answer_relevancy, etc.).",
    )
    retrieval_metric_averages: Dict[str, float] = Field(
        default_factory=dict,
        description="Average scores for retrieval metrics (precision_at_k, recall_at_k, mrr, ndcg, etc.).",
    )
    operational_metric_averages: Dict[str, float] = Field(
        default_factory=dict,
        description="Average scores for operational metrics (latency_ms, token_usage, etc.).",
    )
    provider_summary: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Map of provider name to list of metrics it most frequently computed.",
    )
    fallback_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of metric executions that used deterministic fallback.",
    )
    top_strengths: List[str] = Field(
        default_factory=list,
        description="Most frequently observed strengths across all evaluation samples.",
    )
    top_weaknesses: List[str] = Field(
        default_factory=list,
        description="Most frequently observed weaknesses across all evaluation samples.",
    )
    top_recommendations: List[str] = Field(
        default_factory=list,
        description="Most frequently generated recommendations across all evaluation samples.",
    )

    model_config = ConfigDict(frozen=True)


class BenchmarkExecutiveSummary(BaseModel):
    """Concise executive-level summary of a benchmark run."""

    overall_verdict: str = Field(
        default="",
        description="One-sentence overall assessment of the RAG system's quality.",
    )
    best_metric: str = Field(
        default="",
        description="Name of the highest-performing metric.",
    )
    weakest_metric: str = Field(
        default="",
        description="Name of the lowest-performing metric.",
    )
    primary_bottleneck: str = Field(
        default="",
        description="Identified primary bottleneck affecting overall RAG quality.",
    )
    recommended_next_action: str = Field(
        default="",
        description="Most impactful single improvement action for the benchmarked RAG system.",
    )

    model_config = ConfigDict(frozen=True)


class BenchmarkReport(BaseModel):
    """Complete summary report detailing benchmark execution and results (v2.0)."""

    # ─── Existing fields (unchanged) ───────────────────────────────────────
    benchmark_name: str = Field(..., description="Name of the benchmark suite.")
    benchmark_version: str = Field(default="2.0.0", description="Version of the benchmark suite.")
    provider: EvaluationProvider = Field(..., description="Evaluation provider utilized for the run.")
    started_at: datetime = Field(..., description="UTC timestamp marking when benchmark execution started.")
    completed_at: datetime = Field(..., description="UTC timestamp marking when benchmark execution completed.")
    statistics: BenchmarkStatistics = Field(..., description="Aggregated benchmark statistics summary.")
    results: List[BenchmarkSampleResult] = Field(..., description="Detailed sample evaluation results list.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional benchmark metadata.")

    # ─── New v2.0 fields ───────────────────────────────────────────────────
    quality_grade: str = Field(
        default="F",
        description="Overall benchmark quality grade (A+, A, B, C, D, F) derived from average_score.",
    )
    deployment_readiness: str = Field(
        default="Research Only",
        description="Deployment readiness verdict for the benchmarked RAG architecture.",
    )
    metric_rankings: Dict[str, float] = Field(
        default_factory=dict,
        description="Leaderboard of metric names sorted by average score descending.",
    )
    best_performing_samples: List[str] = Field(
        default_factory=list,
        description="Top 3 sample_ids ranked by overall_score descending.",
    )
    worst_performing_samples: List[str] = Field(
        default_factory=list,
        description="Bottom 3 sample_ids ranked by overall_score ascending.",
    )
    overall_strengths: List[str] = Field(
        default_factory=list,
        description="Most frequently observed strengths across all samples.",
    )
    overall_weaknesses: List[str] = Field(
        default_factory=list,
        description="Most frequently observed weaknesses across all samples.",
    )
    overall_recommendations: List[str] = Field(
        default_factory=list,
        description="Most frequently generated recommendations across all samples.",
    )
    provider_summary: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Providers used in the benchmark run and which metrics they computed.",
    )
    fallback_rate: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Fraction of metric executions that used deterministic fallback.",
    )
    executive_summary: BenchmarkExecutiveSummary = Field(
        default_factory=BenchmarkExecutiveSummary,
        description="Concise executive-level summary of the benchmark run.",
    )

    model_config = ConfigDict(frozen=True)