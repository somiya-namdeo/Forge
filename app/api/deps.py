"""FastAPI dependency providers for Forge application."""

from functools import lru_cache

from fastapi import Depends

from app.metrics.ragas_metrics import RagasEvaluator
from app.metrics.registry import MetricRegistry
from app.services.evaluation_service import EvaluationService
from app.thresholds.threshold_manager import ThresholdManager
from app.utils.weighting import WeightingEngine


@lru_cache
def get_metric_registry() -> MetricRegistry:
    """Provide a singleton MetricRegistry populated with default evaluation providers."""
    registry = MetricRegistry()
    registry.register(RagasEvaluator())
    return registry


@lru_cache
def get_weighting_engine() -> WeightingEngine:
    """Provide a singleton WeightingEngine instance."""
    return WeightingEngine()


@lru_cache
def get_threshold_manager() -> ThresholdManager:
    """Provide a singleton ThresholdManager instance."""
    return ThresholdManager()


def get_evaluation_service(
    registry: MetricRegistry | None = Depends(get_metric_registry),
    weighting_engine: WeightingEngine | None = Depends(get_weighting_engine),
    threshold_manager: ThresholdManager | None = Depends(get_threshold_manager),
) -> EvaluationService:
    """Inject dependencies into EvaluationService for route handlers or direct calls."""
    if hasattr(registry, "dependency") or registry is None:
        registry = get_metric_registry()
    if hasattr(weighting_engine, "dependency") or weighting_engine is None:
        weighting_engine = get_weighting_engine()
    if hasattr(threshold_manager, "dependency") or threshold_manager is None:
        threshold_manager = get_threshold_manager()

    return EvaluationService(
        registry=registry,
        weighting_engine=weighting_engine,
        threshold_manager=threshold_manager,
    )
