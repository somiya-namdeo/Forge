"""
Comparison data models for Forge architecture comparison engine (v2.0).
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.benchmark.benchmark_models import BenchmarkReport


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# NEW v2.0 models
# ─────────────────────────────────────────────────────────────────────────────

class ArchitectureMetadata(BaseModel):
    """Descriptive metadata about a RAG architecture candidate."""

    llm: str = Field(default="", description="LLM model name or identifier.")
    embedding_model: str = Field(default="", description="Embedding model name.")
    vector_database: str = Field(default="", description="Vector database name (e.g., Qdrant, Pinecone).")
    retriever: str = Field(default="", description="Retriever strategy (e.g., dense, hybrid, sparse).")
    reranker: str = Field(default="", description="Reranker model or 'none'.")
    framework: str = Field(default="", description="RAG framework (e.g., LangChain, LlamaIndex).")
    deployment_target: str = Field(default="", description="Target deployment environment.")
    evaluation_provider: str = Field(default="", description="Primary evaluation provider used.")

    model_config = ConfigDict(frozen=True)


class MetricWinner(BaseModel):
    """Per-metric winner across compared architectures."""

    metric: str = Field(..., description="Metric name (e.g., 'faithfulness', 'mrr').")
    winner: str = Field(..., description="Architecture name that scored highest on this metric.")
    winner_score: float = Field(..., description="Winner's score.")
    runner_up: Optional[str] = Field(default=None, description="Runner-up architecture name.")
    runner_up_score: Optional[float] = Field(default=None, description="Runner-up score.")
    score_difference: float = Field(default=0.0, description="Score gap (winner - runner_up).")
    reason: str = Field(default="", description="Explanation of why this architecture won this metric.")

    model_config = ConfigDict(frozen=True)


class TradeOff(BaseModel):
    """Structured trade-off analysis between two quality dimensions."""

    dimension: str = Field(..., description="Trade-off dimension (e.g., 'quality_vs_latency').")
    winner: str = Field(..., description="Architecture name that performs better on this dimension.")
    loser: str = Field(..., description="Architecture name that performs worse on this dimension.")
    analysis: str = Field(..., description="Narrative explanation of the trade-off.")
    recommendation: str = Field(..., description="Actionable recommendation based on this trade-off.")

    model_config = ConfigDict(frozen=True)


class ComparisonExecutiveSummary(BaseModel):
    """Structured executive-level summary of a multi-architecture comparison."""

    overall_winner: str = Field(default="", description="Name of the winning architecture.")
    overall_verdict: str = Field(default="", description="One-paragraph overall verdict.")
    best_architecture: str = Field(default="", description="Name of the best-performing architecture.")
    runner_up: Optional[str] = Field(default=None, description="Name of the runner-up architecture.")
    primary_reason: str = Field(default="", description="Primary reason the winner was selected.")
    major_tradeoff: str = Field(default="", description="Most significant trade-off identified.")
    deployment_recommendation: str = Field(default="", description="Deployment recommendation.")
    risk_analysis: str = Field(default="", description="Migration and deployment risk summary.")
    migration_recommendation: str = Field(default="", description="Migration recommendation from runner-up to winner.")

    model_config = ConfigDict(frozen=True)


# ─────────────────────────────────────────────────────────────────────────────
# Core request/response models (backward-compatible extension)
# ─────────────────────────────────────────────────────────────────────────────

class ArchitectureCandidate(BaseModel):
    """Architecture participating in comparison."""

    architecture_id: str = Field(..., description="Unique architecture identifier.")
    architecture_name: str = Field(..., description="Human-readable architecture name.")
    benchmark_report: BenchmarkReport = Field(..., description="Benchmark report for this architecture.")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Optional architecture metadata.")
    architecture_metadata: ArchitectureMetadata = Field(
        default_factory=ArchitectureMetadata,
        description="Structured architecture metadata (v2.0).",
    )

    model_config = ConfigDict(frozen=True)


class RankedArchitecture(BaseModel):
    """Ranked architecture returned by comparison engine (v2.0 extended)."""

    # ── Existing fields (unchanged) ──────────────────────────────────────────
    rank: int = Field(..., ge=1, description="Ranking position (1-based).")
    architecture_id: str = Field(..., description="Architecture identifier.")
    architecture_name: str = Field(..., description="Architecture name.")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Final comparison score.")
    benchmark_score: float = Field(..., ge=0.0, le=1.0, description="Average benchmark score.")
    average_latency_ms: float = Field(..., ge=0.0, description="Average execution latency in milliseconds.")
    faithfulness: float = Field(default=0.0, ge=0.0, le=1.0, description="Faithfulness score.")
    answer_relevancy: float = Field(default=0.0, ge=0.0, le=1.0, description="Answer relevancy score.")
    context_precision: float = Field(default=0.0, ge=0.0, le=1.0, description="Context precision score.")
    context_recall: float = Field(default=0.0, ge=0.0, le=1.0, description="Context recall score.")
    success_rate: float = Field(default=1.0, ge=0.0, le=1.0, description="Quality gate success rate ratio.")
    strengths: List[str] = Field(default_factory=list, description="Key strengths of this architecture.")
    weaknesses: List[str] = Field(default_factory=list, description="Key weaknesses or areas for improvement.")
    explanation: str = Field(default="", description="Detailed explanation of rank assignment.")
    reason: str = Field(..., description="Reason for assigned ranking.")

    # ── v2.0 new fields (all with defaults) ─────────────────────────────────
    quality_grade: str = Field(default="", description="Quality grade (A+, A, B, C, D, F) from BenchmarkReport.")
    deployment_readiness: str = Field(default="", description="Deployment readiness tier from BenchmarkReport.")
    grade_distribution: Dict[str, int] = Field(
        default_factory=dict, description="Distribution of sample grades across the benchmark run."
    )
    metric_averages: Dict[str, float] = Field(
        default_factory=dict, description="Full map of metric name → average score (all 17 metrics)."
    )
    recommendations: List[str] = Field(
        default_factory=list, description="Top improvement recommendations for this architecture."
    )
    architecture_metadata: ArchitectureMetadata = Field(
        default_factory=ArchitectureMetadata, description="Structured architecture metadata."
    )
    fallback_rate: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Fraction of metrics using deterministic fallback."
    )

    model_config = ConfigDict(frozen=True)


class MetricDifference(BaseModel):
    """Metric difference between winner and runner-up (backward compatible)."""

    metric_name: str = Field(..., description="Evaluated metric name.")
    winner_score: float = Field(..., description="Winner score.")
    runner_up_score: float = Field(..., description="Runner-up score.")
    difference: float = Field(..., description="Score difference (winner - runner-up).")

    model_config = ConfigDict(frozen=True)


class ComparisonSummaryDetails(BaseModel):
    """Structured summary detailing comparative metric gaps (v2.0 extended)."""

    # ── Existing fields (unchanged) ──────────────────────────────────────────
    best_architecture: str = Field(..., description="Name of winning architecture.")
    runner_up: Optional[str] = Field(default=None, description="Name of second-placed architecture.")
    score_difference: float = Field(..., description="Overall score gap between 1st and 2nd place.")
    metric_differences: Dict[str, float] = Field(
        default_factory=dict, description="Per-metric score differences (winner vs runner-up)."
    )
    latency_difference_ms: float = Field(..., description="Latency difference (runner-up - winner) in ms.")
    recommendation: str = Field(..., description="Executive recommendation summary.")

    # ── v2.0 new fields ──────────────────────────────────────────────────────
    metric_winners: Dict[str, str] = Field(
        default_factory=dict, description="Map of metric_name → winning architecture name."
    )
    production_readiness_comparison: Dict[str, str] = Field(
        default_factory=dict, description="Map of architecture_name → deployment readiness tier."
    )
    fallback_rate_comparison: Dict[str, float] = Field(
        default_factory=dict, description="Map of architecture_name → fallback rate."
    )

    model_config = ConfigDict(frozen=True)


class ComparisonMetadata(BaseModel):
    """Metadata describing the comparison run session."""

    comparison_id: str = Field(..., description="Unique comparison execution UUID.")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="UTC creation timestamp.")
    ranking_strategy: str = Field(..., description="Ranking strategy utilized.")
    optimization_goal: str = Field(..., description="Optimization goal target.")
    number_of_architectures: int = Field(..., description="Total architectures compared.")

    model_config = ConfigDict(frozen=True)


class ComparisonRequest(BaseModel):
    """Request payload for comparing benchmarked architectures."""

    comparison_name: str = Field(default="Architecture Comparison", description="Comparison session name.")
    optimization_goal: OptimizationGoal = Field(
        default=OptimizationGoal.BALANCED, description="Optimization objective."
    )
    ranking_strategy: RankingStrategy = Field(
        default=RankingStrategy.WEIGHTED_SCORE, description="Ranking algorithm strategy."
    )
    architectures: List[ArchitectureCandidate] = Field(
        ..., min_length=2, description="Architectures to compare."
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
    """Response returned after architecture comparison (v2.0 extended)."""

    # ── Existing fields (unchanged) ──────────────────────────────────────────
    comparison_id: str = Field(..., description="Unique comparison identifier.")
    comparison_name: str = Field(..., description="Comparison session name.")
    winner: RankedArchitecture = Field(..., description="Highest-ranked winning architecture.")
    runner_up: Optional[RankedArchitecture] = Field(default=None, description="Runner-up architecture.")
    rankings: List[RankedArchitecture] = Field(..., description="Ordered ranking of architectures.")
    summary: str = Field(..., description="Overall comparison summary text.")
    comparison_summary: Optional[ComparisonSummaryDetails] = Field(
        default=None, description="Structured comparison summary breakdown."
    )
    recommendation_paragraph: str = Field(default="", description="Short recommendation paragraph.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations list.")
    metadata: Optional[ComparisonMetadata] = Field(default=None, description="Comparison execution metadata.")
    compared_at: datetime = Field(default_factory=datetime.utcnow, description="UTC timestamp of comparison.")

    # ── v2.0 new fields (all with defaults) ─────────────────────────────────
    comparison_version: str = Field(default="2.0", description="Comparison module version.")
    overall_winner: str = Field(default="", description="Name of the overall winning architecture.")
    overall_winner_reason: str = Field(default="", description="Reason why the overall winner was selected.")
    ranked_architectures: List[RankedArchitecture] = Field(
        default_factory=list, description="Full ranked list with v2.0 enriched fields (alias for rankings)."
    )
    metric_winners: List[MetricWinner] = Field(
        default_factory=list, description="Per-metric winner across all compared architectures."
    )
    trade_off_analysis: List[TradeOff] = Field(
        default_factory=list, description="Identified quality/latency/cost trade-offs."
    )
    strength_comparison: Dict[str, List[str]] = Field(
        default_factory=dict, description="Map of architecture_name → list of strengths."
    )
    weakness_comparison: Dict[str, List[str]] = Field(
        default_factory=dict, description="Map of architecture_name → list of weaknesses."
    )
    recommendation_comparison: Dict[str, List[str]] = Field(
        default_factory=dict, description="Map of architecture_name → top improvement recommendations."
    )
    deployment_recommendation: str = Field(
        default="", description="Structured deployment recommendation narrative."
    )
    production_readiness_comparison: Dict[str, str] = Field(
        default_factory=dict, description="Map of architecture_name → deployment readiness tier."
    )
    cost_vs_quality_analysis: str = Field(
        default="", description="Analysis of cost vs quality trade-off across architectures."
    )
    latency_vs_quality_analysis: str = Field(
        default="", description="Analysis of latency vs quality trade-off across architectures."
    )
    radar_metrics: Dict[str, Dict[str, float]] = Field(
        default_factory=dict,
        description="Radar-chart-ready structure: {arch_name → {metric_name → score}}.",
    )
    executive_summary: Optional[ComparisonExecutiveSummary] = Field(
        default=None, description="Structured executive summary of the comparison."
    )

    model_config = ConfigDict()


# ─────────────────────────────────────────────────────────────────────────────
# Typed ComparisonReport (replaces raw dict from ReportBuilder)
# ─────────────────────────────────────────────────────────────────────────────

class ComparisonReport(BaseModel):
    """Typed structured comparison report (v2.0)."""

    comparison_id: str = Field(..., description="Unique comparison identifier.")
    comparison_name: str = Field(..., description="Comparison session name.")
    comparison_version: str = Field(default="2.0", description="Comparison module version.")
    best_architecture: str = Field(..., description="Name of the overall winning architecture.")
    runner_up: Optional[str] = Field(default=None, description="Name of runner-up architecture.")
    winner_details: Dict = Field(default_factory=dict, description="Detailed winner fields.")
    summary: str = Field(..., description="Overall comparison summary.")
    recommendation_paragraph: str = Field(default="", description="Recommendation narrative.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations.")
    strengths: List[str] = Field(default_factory=list, description="Winner strengths.")
    weaknesses: List[str] = Field(default_factory=list, description="Winner weaknesses.")
    comparison_summary: Dict = Field(default_factory=dict, description="Structured summary breakdown.")
    rankings: List[Dict] = Field(default_factory=list, description="Full architecture rankings.")
    metric_winners: List[Dict] = Field(default_factory=list, description="Per-metric winners.")
    trade_off_analysis: List[Dict] = Field(default_factory=list, description="Trade-off analysis list.")
    strength_comparison: Dict[str, List[str]] = Field(default_factory=dict, description="Per-arch strengths.")
    weakness_comparison: Dict[str, List[str]] = Field(default_factory=dict, description="Per-arch weaknesses.")
    production_readiness_comparison: Dict[str, str] = Field(
        default_factory=dict, description="Deployment readiness per architecture."
    )
    radar_metrics: Dict[str, Dict[str, float]] = Field(
        default_factory=dict, description="Radar-chart-ready metric structure."
    )
    executive_summary: Dict = Field(default_factory=dict, description="Executive summary fields.")
    metadata: Dict = Field(default_factory=dict, description="Comparison execution metadata.")
    compared_at: datetime = Field(default_factory=datetime.utcnow, description="UTC comparison timestamp.")

    model_config = ConfigDict()