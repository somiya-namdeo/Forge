"""
Score Calculator Utility Module.

Calculates composite weighted evaluation scores, aggregate statistics, and metric score
summaries for RAG evaluation runs.
"""

from typing import Dict, List

from backend.app.metrics import MetricType, MetricValue
from backend.app.utils.weighting import WeightConfig, WeightingEngine


class ScoreCalculator:
    """Utility class for computing composite scores and summary statistics."""

    def __init__(self, weight_config: WeightConfig) -> None:
        """Initialize ScoreCalculator with weighting configuration.

        Args:
            weight_config (WeightConfig): Weighting configuration instance.
        """
        self.weight_config = weight_config

    def calculate_composite_score(
        self,
        metric_scores: Dict[MetricType, float],
    ) -> float:
        """Compute composite weighted average score across evaluated metrics.

        Args:
            metric_scores (Dict[MetricType, float]): Map of metric types to raw scores.

        Returns:
            float: Composite score value (0.0 to 1.0).
        """
        if not metric_scores:
            return 0.0

        normalized_weights = WeightingEngine.normalize_weights(self.weight_config.weights)
        weighted_sum = 0.0
        total_weight = 0.0

        for metric_type, score in metric_scores.items():
            weight = normalized_weights.get(metric_type, 0.0)
            weighted_sum += score * weight
            total_weight += weight

        if total_weight == 0.0:
            return sum(metric_scores.values()) / len(metric_scores)

        return weighted_sum / total_weight

    def calculate_aggregate_stats(
        self,
        scores: List[float],
    ) -> Dict[str, float]:
        """Calculate statistical metrics (mean, min, max) for a score distribution.

        Args:
            scores (List[float]): List of calculated numerical scores.

        Returns:
            Dict[str, float]: Dictionary containing mean, min, max, and sample count.
        """
        if not scores:
            return {"mean": 0.0, "min": 0.0, "max": 0.0, "count": 0}

        return {
            "mean": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "count": float(len(scores)),
        }

    def summarize_sample_results(
        self,
        sample_metric_values: List[MetricValue],
    ) -> Dict[str, float]:
        """Summarize a collection of MetricValue outputs into metric score dict.

        Args:
            sample_metric_values (List[MetricValue]): List of evaluated metric outputs.

        Returns:
            Dict[str, float]: Mapping of metric names to calculated scores.
        """
        return {
            mv.metric_type.value: mv.score
            for mv in sample_metric_values
        }
