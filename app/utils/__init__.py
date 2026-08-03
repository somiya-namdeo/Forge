"""
Evaluation Utilities Package.

Provides mathematical score calculation, statistical aggregation, weight normalization,
and preset weighting configurations for RAG evaluation.
"""

from app.utils.score_calculator import ScoreCalculator
from app.utils.weighting import WeightConfig, WeightingEngine

__all__ = [
    "WeightConfig",
    "WeightingEngine",
    "ScoreCalculator",
]
