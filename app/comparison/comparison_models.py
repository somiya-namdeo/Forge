"""
Comparison data models for Forge architecture comparison engine.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.benchmark.benchmark_models import BenchmarkReport


class OptimizationGoal(str, Enum):
    """Optimization objectives for architecture comparison."""

    QUALITY = "quality"
    LATENCY = "latency"
    COST = "cost"
    BALANCED = "balanced"


class RankingStrategy(str, Enum):
    """Supported ranking strategies."""

    WEIGHTED_SCORE = "weighted_score"
    HIGHEST_ACCURACY = "highest_accuracy"
    LOWEST_LATENCY = "lowest_latency"
    BALANCED = "balanced"
    PARETO = "pareto"


class ArchitectureCandidate(BaseModel):
    """Architecture participating in comparison."""

    architecture_id: str = Field(
        ...,
        description="Unique architecture identifier.",
    )
    architecture_name: str = Field(
        ...,
        description="Human-readable architecture name.",
    )
    benchmark_report: BenchmarkReport = Field(
        ...,
        description="Benchmark report for this architecture.",
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Optional architecture metadata.",
    )

    model_config = ConfigDict(frozen=True)


class RankedArchitecture(BaseModel):
    """Ranked architecture returned by comparison engine."""

    rank: int = Field(
        ...,
        ge=1,
        description="Ranking position (1-based).",
    )
    architecture_id: str = Field(
        ...,
        description="Architecture identifier.",
    )
    architecture_name: str = Field(
        ...,
        description="Architecture name.",
    )
    overall_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Final comparison score.",
    )
    benchmark_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Average benchmark score.",
    )
    average_latency_ms: float = Field(
        ...,
        ge=0.0,
        description="Average execution latency in milliseconds.",
    )
    faithfulness: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Faithfulness score.",
    )
    answer_relevancy: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Answer relevancy score.",
    )
    context_precision: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Context precision score.",
    )
    context_recall: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Context recall score.",
    )
    success_rate: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Quality gate success rate ratio.",
    )
    strengths: List[str] = Field(
        default_factory=list,
        description="Key strengths of this architecture.",
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="Key weaknesses or areas for improvement.",
    )
    explanation: str = Field(
        default="",
        description="Detailed explanation of rank assignment.",
    )
    reason: str = Field(
        ...,
        description="Reason for assigned ranking.",
    )

    model_config = ConfigDict(frozen=True)


class MetricDifference(BaseModel):
    """Metric difference between winner and runner-up."""

    metric_name: str = Field(..., description="Evaluated metric name.")
    winner_score: float = Field(..., description="Winner score.")
    runner_up_score: float = Field(..., description="Runner-up score.")
    difference: float = Field(..., description="Score difference (winner - runner-up).")

    model_config = ConfigDict(frozen=True)


class ComparisonSummaryDetails(BaseModel):
    """Structured summary detailing comparative metric gaps."""

    best_architecture: str = Field(..., description="Name of winning architecture.")
    runner_up: Optional[str] = Field(default=None, description="Name of second-placed architecture.")
    score_difference: float = Field(..., description="Overall score gap between 1st and 2nd place.")
    metric_differences: Dict[str, float] = Field(
        default_factory=dict,
        description="Per-metric score differences (winner vs runner-up).",
    )
    latency_difference_ms: float = Field(
        ...,
        description="Latency difference in milliseconds (runner-up latency - winner latency).",
    )
    recommendation: str = Field(..., description="Executive recommendation summary.")

    model_config = ConfigDict(frozen=True)


class ComparisonMetadata(BaseModel):
    """Metadata describing the comparison run session."""

    comparison_id: str = Field(..., description="Unique comparison execution UUID.")
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC creation timestamp.",
    )
    ranking_strategy: str = Field(..., description="Ranking strategy utilized.")
    optimization_goal: str = Field(..., description="Optimization goal target.")
    number_of_architectures: int = Field(..., description="Total architectures compared.")

    model_config = ConfigDict(frozen=True)


class ComparisonRequest(BaseModel):
    """Request payload for comparing benchmarked architectures."""

    comparison_name: str = Field(
        default="Architecture Comparison",
        description="Comparison session name.",
    )
    optimization_goal: OptimizationGoal = Field(
        default=OptimizationGoal.BALANCED,
        description="Optimization objective.",
    )
    ranking_strategy: RankingStrategy = Field(
        default=RankingStrategy.WEIGHTED_SCORE,
        description="Ranking algorithm strategy.",
    )
    architectures: List[ArchitectureCandidate] = Field(
        ...,
        min_length=2,
        description="Architectures to compare.",
    )

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "comparison_name": "Hybrid vs Naive RAG Comparison",
                "optimization_goal": "balanced",
                "ranking_strategy": "weighted_score",
                "architectures": [],
            }
        },
    )


class ComparisonResponse(BaseModel):
    """Response returned after architecture comparison."""

    comparison_id: str = Field(
        ...,
        description="Unique comparison identifier.",
    )
    comparison_name: str = Field(
        ...,
        description="Comparison session name.",
    )
    winner: RankedArchitecture = Field(
        ...,
        description="Highest-ranked winning architecture.",
    )
    runner_up: Optional[RankedArchitecture] = Field(
        default=None,
        description="Runner-up architecture (2nd place).",
    )
    rankings: List[RankedArchitecture] = Field(
        ...,
        description="Ordered ranking of architectures.",
    )
    summary: str = Field(
        ...,
        description="Overall comparison summary text.",
    )
    comparison_summary: Optional[ComparisonSummaryDetails] = Field(
        default=None,
        description="Structured comparison summary breakdown.",
    )
    recommendation_paragraph: str = Field(
        default="",
        description="Short recommendation paragraph.",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="Actionable recommendations list.",
    )
    metadata: Optional[ComparisonMetadata] = Field(
        default=None,
        description="Comparison execution metadata.",
    )
    compared_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of comparison.",
    )

    model_config = ConfigDict()