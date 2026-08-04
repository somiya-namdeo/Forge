"""Metric calculator registry for Forge evaluation module.

Provides auto-discovery, registration, and lookup of all MetricCalculator implementations.
"""

import logging
from typing import Dict, List, Optional, Type

from app.evaluation.metrics.base_metric import MetricCalculator, MetricCategory

logger = logging.getLogger(__name__)


class MetricCalculatorRegistry:
    """Thread-safe registry for MetricCalculator instances.

    Supports:
    - Manual registration of calculator instances
    - Auto-discovery of all calculators in the metrics package
    - Lookup by metric name or category
    """

    def __init__(self) -> None:
        self._calculators: Dict[str, MetricCalculator] = {}

    def register(self, calculator: MetricCalculator) -> None:
        """Register a MetricCalculator instance under its metric_name."""
        name = calculator.metric_name
        if name in self._calculators:
            logger.debug("MetricCalculatorRegistry: overwriting existing calculator for '%s'", name)
        self._calculators[name] = calculator
        logger.debug("MetricCalculatorRegistry: registered '%s' (%s)", name, type(calculator).__name__)

    def get(self, metric_name: str) -> Optional[MetricCalculator]:
        """Return a registered calculator by name, or None if not found."""
        return self._calculators.get(metric_name)

    def all(self) -> List[MetricCalculator]:
        """Return all registered calculator instances."""
        return list(self._calculators.values())

    def by_category(self, category: MetricCategory) -> List[MetricCalculator]:
        """Return all calculators in the given category."""
        return [c for c in self._calculators.values() if c.metric_category == category]

    @property
    def metric_names(self) -> List[str]:
        """Return all registered metric names."""
        return list(self._calculators.keys())

    def __len__(self) -> int:
        return len(self._calculators)


def build_default_registry() -> MetricCalculatorRegistry:
    """Instantiate and register all default MetricCalculator implementations.

    Imports are deferred so that individual import failures (e.g., optional packages)
    do not block registry construction.
    """
    registry = MetricCalculatorRegistry()

    _candidates = [
        # Generation metrics (RAGAS)
        ("app.evaluation.metrics.faithfulness", "FaithfulnessCalculator"),
        ("app.evaluation.metrics.answer_relevancy", "AnswerRelevancyCalculator"),
        # Retrieval ranking metrics (Deterministic)
        ("app.evaluation.metrics.precision_at_k", "PrecisionAtKCalculator"),
        ("app.evaluation.metrics.recall_at_k", "RecallAtKCalculator"),
        ("app.evaluation.metrics.hit_rate", "HitRateCalculator"),
        ("app.evaluation.metrics.mrr", "MRRCalculator"),
        ("app.evaluation.metrics.ndcg", "NDCGCalculator"),
        # Operational metrics
        ("app.evaluation.metrics.operational", "LatencyCalculator"),
        ("app.evaluation.metrics.operational", "TokenUsageCalculator"),
        ("app.evaluation.metrics.operational", "CostEstimationCalculator"),
        ("app.evaluation.metrics.operational", "ThroughputCalculator"),
    ]

    for module_path, class_name in _candidates:
        try:
            import importlib
            module = importlib.import_module(module_path)
            cls: Type[MetricCalculator] = getattr(module, class_name)
            instance = cls()
            registry.register(instance)
        except Exception as exc:
            logger.warning("MetricCalculatorRegistry: skipping '%s.%s' — %s", module_path, class_name, exc)

    logger.info("MetricCalculatorRegistry built with %d calculators: %s", len(registry), registry.metric_names)
    return registry
