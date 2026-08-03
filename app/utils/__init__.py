"""
Evaluation Utilities Package.

Provides mathematical score calculation, statistical aggregation, weight normalization,
and preset weighting configurations for RAG evaluation.
"""

from backend.app.utils.score_calculator import ScoreCalculator
from backend.app.utils.weighting import WeightConfig, WeightingEngine

__all__ = [
    "WeightConfig",
    "WeightingEngine",
    "ScoreCalculator",
]
