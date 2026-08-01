"""Evaluation score weighting configuration and engine."""

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.evaluation import MetricConfig


class WeightConfig(BaseModel):
    """Configuration model storing weights for evaluation metrics."""

    faithfulness: float = Field(default=0.25, ge=0.0, le=1.0, description="Weight for faithfulness metric.")
    answer_relevancy: float = Field(default=0.25, ge=0.0, le=1.0, description="Weight for answer relevancy metric.")
    context_precision: float = Field(default=0.25, ge=0.0, le=1.0, description="Weight for context precision metric.")
    context_recall: float = Field(default=0.25, ge=0.0, le=1.0, description="Weight for context recall metric.")

    model_config = ConfigDict(frozen=True)


class WeightingEngine:
    """Engine responsible for normalizing metric weights and computing composite scores."""

    def create_config(self, metric_config: list[MetricConfig] | None = None) -> WeightConfig:
        """Build WeightConfig applying custom metric weights and disabled flags."""
        if not metric_config:
            return WeightConfig()

        supported_fields = set(WeightConfig.model_fields.keys())
        custom_weights = {}
        for mc in metric_config:
            if mc.metric_name in supported_fields:
                custom_weights[mc.metric_name] = mc.weight if mc.enabled else 0.0

        return WeightConfig(**custom_weights)

    def normalize(self, config: WeightConfig) -> WeightConfig:
        """Normalize configuration weights so their sum equals 1.0."""
        field_values = {field: getattr(config, field) for field in WeightConfig.model_fields}
        total = sum(field_values.values())
        if total == 0.0:
            raise ValueError("Total weight cannot be zero.")
        normalized_values = {field: val / total for field, val in field_values.items()}
        return WeightConfig(**normalized_values)

    def calculate(
        self,
        metric_scores: dict[str, float],
        config: WeightConfig,
    ) -> float:
        """Compute weighted average score for supported metric scores."""
        supported_fields = set(WeightConfig.model_fields.keys())
        valid_scores = {k: v for k, v in metric_scores.items() if k in supported_fields}

        if not valid_scores:
            raise ValueError("No supported metric scores provided for calculation.")

        weighted_sum = sum(valid_scores[m] * getattr(config, m) for m in valid_scores)
        total_weight = sum(getattr(config, m) for m in valid_scores)

        if total_weight == 0.0:
            raise ValueError("Total weight for provided metrics cannot be zero.")

        score = weighted_sum / total_weight
        return min(1.0, max(0.0, float(score)))
