"""Architecture Comparison Package (v2.0)."""

from app.comparison.comparison_engine import ComparisonEngine
from app.comparison.comparison_models import (
    ArchitectureCandidate,
    ArchitectureMetadata,
    ComparisonExecutiveSummary,
    ComparisonMetadata,
    ComparisonReport,
    ComparisonRequest,
    ComparisonResponse,
    ComparisonSummaryDetails,
    MetricWinner,
    OptimizationGoal,
    RankedArchitecture,
    RankingStrategy,
    TradeOff,
)
from app.comparison.comparison_report import ComparisonReportBuilder
from app.comparison.ranking import RankingEngine

__all__ = [
    "ComparisonEngine",
    "ComparisonReportBuilder",
    "RankingEngine",
    "ArchitectureCandidate",
    "ArchitectureMetadata",
    "RankedArchitecture",
    "MetricWinner",
    "TradeOff",
    "ComparisonExecutiveSummary",
    "ComparisonRequest",
    "ComparisonResponse",
    "ComparisonSummaryDetails",
    "ComparisonMetadata",
    "ComparisonReport",
    "OptimizationGoal",
    "RankingStrategy",
]
