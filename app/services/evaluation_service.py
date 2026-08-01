"""Evaluation service orchestrating the evaluation pipeline."""

from datetime import datetime, timezone
import time
from uuid import uuid4

from app.metrics.registry import MetricRegistry
from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse,
    ThresholdConfig,
)
from app.thresholds.threshold_manager import ThresholdManager
from app.utils.weighting import WeightingEngine


class EvaluationService:
    """Service orchestrating evaluation provider resolution, scoring, and thresholds."""

    def __init__(
        self,
        registry: MetricRegistry,
        weighting_engine: WeightingEngine,
        threshold_manager: ThresholdManager,
    ) -> None:
        """Initialize evaluation service with injected dependencies."""
        self.registry = registry
        self.weighting_engine = weighting_engine
        self.threshold_manager = threshold_manager

    def evaluate(self, request: EvaluationRequest) -> EvaluationResponse:
        """Execute the full evaluation pipeline for a given request."""
        start_time = time.perf_counter()

        provider = self.registry.get(request.provider.value)

        try:
            metric_scores: dict[str, float] = provider.evaluate(request)
        except Exception as exc:
            raise ValueError(
                f"Provider '{request.provider.value}' evaluation failed: {exc}"
            ) from exc

        try:
            weight_config = self.weighting_engine.create_config(request.metric_config)
            normalized_config = self.weighting_engine.normalize(weight_config)
            overall_score = self.weighting_engine.calculate(metric_scores, normalized_config)
        except ValueError as exc:
            raise ValueError(f"Weighting calculation failed: {exc}") from exc

        thresholds = request.threshold_config or ThresholdConfig()
        try:
            evaluated_metrics = [
                self.threshold_manager.evaluate_metric(
                    metric_name=metric_name,
                    score=score,
                    thresholds=thresholds,
                )
                for metric_name, score in metric_scores.items()
            ]
        except ValueError as exc:
            raise ValueError(f"Threshold evaluation failed: {exc}") from exc

        overall_status = self.threshold_manager.overall_status(evaluated_metrics)
        execution_time_ms = max(0.001, (time.perf_counter() - start_time) * 1000.0)

        return EvaluationResponse(
            evaluation_id=uuid4(),
            provider=request.provider,
            overall_score=overall_score,
            status=overall_status,
            metrics=evaluated_metrics,
            execution_time_ms=execution_time_ms,
            created_at=datetime.now(timezone.utc),
        )
