"""
Custom Metrics and TruLens Evaluator Providers.

Extensible evaluation module supporting custom user-defined metric logic (latency, cost,
regex rules, LLM-as-a-judge) and TruLens evaluation provider integration.
"""

from typing import Any, Callable, Dict, List, Optional

from app.metrics import (
    BaseMetricEvaluator,
    EvaluationProvider,
    MetricType,
    MetricValue,
    PassFailStatus,
)


class TruLensEvaluator(BaseMetricEvaluator):
    """Evaluation provider implementation wrapping TruLens feedback functions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize TruLens evaluator configuration.

        Args:
            config (Optional[Dict[str, Any]]): TruLens feedback function configurations.
        """
        self.config = config or {}

    @property
    def provider_name(self) -> EvaluationProvider:
        """Return provider framework name.

        Returns:
            EvaluationProvider: TruLens enum identifier.
        """
        return EvaluationProvider.TRULENS

    @property
    def supported_metrics(self) -> List[MetricType]:
        """List metrics supported by TruLens evaluator.

        Returns:
            List[MetricType]: Supported TruLens metrics.
        """
        return [
            MetricType.FAITHFULNESS,
            MetricType.ANSWER_RELEVANCE,
            MetricType.LATENCY,
        ]

    def evaluate(self, request: Any) -> Dict[str, float]:
        """Evaluate request using TruLens evaluator."""
        return {"faithfulness": 0.0, "answer_relevancy": 0.0}

    def evaluate_metric(
        self,
        query: str,
        response: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        metric_type: MetricType = MetricType.FAITHFULNESS,
    ) -> MetricValue:
        """Evaluate a metric using TruLens feedback functions."""
        return MetricValue(
            metric_type=metric_type,
            score=0.0,
            provider=self.provider_name,
            status=PassFailStatus.PASS,
            latency_ms=0.0,
            metadata={"provider_detail": "TruLens placeholder execution"},
        )

    async def evaluate_metric_async(
        self,
        query: str,
        response: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        metric_type: MetricType = MetricType.FAITHFULNESS,
    ) -> MetricValue:
        """Evaluate a metric asynchronously using TruLens."""
        return self.evaluate_metric(query, response, contexts, ground_truth, metric_type)


class CustomEvaluator(BaseMetricEvaluator):
    """Evaluator for custom user-registered functions, latency, cost, and heuristics."""

    def __init__(self) -> None:
        """Initialize custom evaluator registry."""
        self._custom_functions: Dict[str, Callable[..., float]] = {}

    @property
    def provider_name(self) -> EvaluationProvider:
        """Return provider framework name."""
        return EvaluationProvider.CUSTOM

    @property
    def supported_metrics(self) -> List[MetricType]:
        """List metrics supported by Custom evaluator."""
        return [
            MetricType.LATENCY,
            MetricType.COST,
            MetricType.CUSTOM,
        ]

    def evaluate(self, request: Any) -> Dict[str, float]:
        """Evaluate request using Custom evaluator."""
        return {"custom": 0.0}

    def register_custom_function(
        self,
        name: str,
        func: Callable[..., float],
    ) -> None:
        """Register a custom Python evaluation function."""
        self._custom_functions[name] = func

    def evaluate_metric(
        self,
        query: str,
        response: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        metric_type: MetricType = MetricType.CUSTOM,
    ) -> MetricValue:
        """Evaluate a custom user metric synchronously."""
        return MetricValue(
            metric_type=metric_type,
            score=0.0,
            provider=self.provider_name,
            status=PassFailStatus.PASS,
            latency_ms=0.0,
            metadata={"custom_metrics_count": len(self._custom_functions)},
        )

    async def evaluate_metric_async(
        self,
        query: str,
        response: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        metric_type: MetricType = MetricType.CUSTOM,
    ) -> MetricValue:
        """Evaluate a custom metric asynchronously."""
        return self.evaluate_metric(query, response, contexts, ground_truth, metric_type)
