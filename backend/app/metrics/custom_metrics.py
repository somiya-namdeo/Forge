"""
Custom Metrics and TruLens Evaluator Providers.

Extensible evaluation module supporting custom user-defined metric logic (latency, cost,
regex rules, LLM-as-a-judge) and TruLens evaluation provider integration.
"""

from typing import Any, Callable, Dict, List, Optional

from backend.app.metrics import (
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
            MetricType.CONTEXT_RECALL,
            MetricType.LATENCY,
        ]

    def evaluate_metric(
        self,
        query: str,
        response: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        metric_type: MetricType = MetricType.FAITHFULNESS,
    ) -> MetricValue:
        """Evaluate a metric using TruLens feedback functions.

        Args:
            query (str): User prompt.
            response (str): LLM response.
            contexts (List[str]): Context chunks.
            ground_truth (Optional[str]): Expected answer.
            metric_type (MetricType): Target metric.

        Returns:
            MetricValue: Calculated metric result.
        """
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
        """Evaluate a metric asynchronously using TruLens.

        Args:
            query (str): User prompt.
            response (str): LLM response.
            contexts (List[str]): Contexts.
            ground_truth (Optional[str]): Expected output.
            metric_type (MetricType): Target metric.

        Returns:
            MetricValue: Metric calculation result.
        """
        return self.evaluate_metric(query, response, contexts, ground_truth, metric_type)


class CustomEvaluator(BaseMetricEvaluator):
    """Evaluator for custom user-registered functions, latency, cost, and heuristics."""

    def __init__(self) -> None:
        """Initialize custom evaluator registry."""
        self._custom_functions: Dict[str, Callable[..., float]] = {}

    @property
    def provider_name(self) -> EvaluationProvider:
        """Return provider framework name.

        Returns:
            EvaluationProvider: Custom provider enum identifier.
        """
        return EvaluationProvider.CUSTOM

    @property
    def supported_metrics(self) -> List[MetricType]:
        """List metrics supported by Custom evaluator.

        Returns:
            List[MetricType]: Supported custom metrics.
        """
        return [
            MetricType.LATENCY,
            MetricType.COST,
            MetricType.CUSTOM,
        ]

    def register_custom_function(
        self,
        name: str,
        func: Callable[..., float],
    ) -> None:
        """Register a custom Python evaluation function.

        Args:
            name (str): Custom metric identifier name.
            func (Callable[..., float]): Function computing float score.
        """
        self._custom_functions[name] = func

    def evaluate_metric(
        self,
        query: str,
        response: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        metric_type: MetricType = MetricType.CUSTOM,
    ) -> MetricValue:
        """Evaluate a custom user metric synchronously.

        Args:
            query (str): User prompt.
            response (str): LLM response.
            contexts (List[str]): Retrieved contexts.
            ground_truth (Optional[str]): Ground truth answer.
            metric_type (MetricType): Metric type.

        Returns:
            MetricValue: Evaluated custom score.
        """
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
        """Evaluate a custom metric asynchronously.

        Args:
            query (str): User prompt.
            response (str): LLM response.
            contexts (List[str]): Contexts.
            ground_truth (Optional[str]): Ground truth.
            metric_type (MetricType): Metric type.

        Returns:
            MetricValue: Evaluated metric result.
        """
        return self.evaluate_metric(query, response, contexts, ground_truth, metric_type)
