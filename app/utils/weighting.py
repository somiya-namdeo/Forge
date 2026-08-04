"""
Weighting Engine Module.

Manages metric weight assignments, preset profiles (RAG Standard, Accuracy Heavy,
Retrieval Heavy), and weight validation/normalization.
"""

from enum import Enum
from typing import Dict, Optional

from app.metrics import MetricType


class WeightPreset(str, Enum):
    """Pre-configured weighting profiles for evaluation scenarios."""

    BALANCED_RAG = "balanced_rag"
    ACCURACY_FOCUSED = "accuracy_focused"
    RETRIEVAL_FOCUSED = "retrieval_focused"
    CUSTOM = "custom"


class WeightConfig:
    """Configuration class storing metric weight mapping."""

    def __init__(
        self,
        weights: Optional[Dict[MetricType, float]] = None,
        preset: WeightPreset = WeightPreset.BALANCED_RAG,
    ) -> None:
        """Initialize WeightConfig with weights dictionary or preset.

        Args:
            weights (Optional[Dict[MetricType, float]]): Custom metric weights mapping.
            preset (WeightPreset): Target preset profile.
        """
        self.preset = preset
        self.weights: Dict[MetricType, float] = weights or {}

    def get_weight(self, metric_type: MetricType) -> float:
        """Get weight for a specific metric.

        Args:
            metric_type (MetricType): Metric type enum.

        Returns:
            float: Assigned weight float value.
        """
        return self.weights.get(metric_type, 1.0)


class WeightingEngine:
    """Engine responsible for normalizing weights and generating presets."""

    @staticmethod
    def get_preset_config(preset: WeightPreset) -> WeightConfig:
        """Retrieve default weight configuration for a specified preset profile.

        Args:
            preset (WeightPreset): Desired preset profile.

        Returns:
            WeightConfig: Populated WeightConfig object.
        """
        if preset == WeightPreset.BALANCED_RAG:
            return WeightConfig(
                weights={
                    MetricType.FAITHFULNESS: 0.5,
                    MetricType.ANSWER_RELEVANCE: 0.5,
                },
                preset=preset,
            )
        elif preset == WeightPreset.ACCURACY_FOCUSED:
            return WeightConfig(
                weights={
                    MetricType.FAITHFULNESS: 0.6,
                    MetricType.ANSWER_RELEVANCE: 0.4,
                },
                preset=preset,
            )
        return WeightConfig(weights={}, preset=preset)

    @staticmethod
    def normalize_weights(weights: Dict[MetricType, float]) -> Dict[MetricType, float]:
        """Normalize metric weights so their sum equals 1.0.

        Args:
            weights (Dict[MetricType, float]): Raw metric weight map.

        Returns:
            Dict[MetricType, float]: Normalized weights map summing to 1.0.
        """
        total = sum(weights.values())
        if total == 0:
            return {k: 0.0 for k in weights}
        return {k: v / total for k, v in weights.items()}
