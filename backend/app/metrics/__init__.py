"""
Evaluation Metrics Package.

Defines pluggable evaluator interfaces, provider registries, metric types,
and score value containers supporting RAGAS, DeepEval, TruLens, and Custom evaluators.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class EvaluationProvider(str, Enum):
    """Supported evaluation provider frameworks."""

    RAGAS = "ragas"
    DEEPEVAL = "deepeval"
    TRULENS = "trulens"
    CUSTOM = "custom"


class MetricType(str, Enum):
    """Core RAG evaluation metrics supported across providers."""

    FAITHFULNESS = "faithfulness"
    ANSWER_RELEVANCE = "answer_relevance"
    CONTEXT_RECALL = "context_recall"
    CONTEXT_PRECISION = "context_precision"
    HALLUCINATION = "hallucination"
    TOXICITY = "toxicity"
    LATENCY = "latency"
    COST = "cost"
    CUSTOM = "custom"


class PassFailStatus(str, Enum):
    """Quality gate threshold evaluation status."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"


@dataclass
class MetricValue:
    """Dataclass encapsulating single metric evaluation output.

    Attributes:
        metric_type (MetricType): The type of metric evaluated.
        score (float): Calculated raw score (typically 0.0 to 1.0).
        provider (EvaluationProvider): The provider framework used for calculation.
        status (PassFailStatus): Pass/Fail/Warning status relative to defined thresholds.
        latency_ms (float): Time taken to evaluate the metric in milliseconds.
        metadata (Dict[str, Any]): Additional evaluation context or explanation text.
        error (Optional[str]): Error message if evaluation failed.
    """

    metric_type: MetricType
    score: float
    provider: EvaluationProvider
    status: PassFailStatus = PassFailStatus.PASS
    latency_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class BaseMetricEvaluator(ABC):
    """Abstract Base Class for pluggable evaluation metric providers.

    All metric providers (RAGAS, DeepEval, TruLens, Custom) must inherit from
    this interface to maintain plug-and-play architectural flexibility.
    """

    @property
    @abstractmethod
    def provider_name(self) -> EvaluationProvider:
        """Return the unique provider name.

        Returns:
            EvaluationProvider: Provider framework enum identifier.
        """
        pass

    @property
    @abstractmethod
    def supported_metrics(self) -> List[MetricType]:
        """List metrics supported by this evaluator provider.

        Returns:
            List[MetricType]: List of supported MetricType enums.
        """
        pass

    @abstractmethod
    def evaluate_metric(
        self,
        query: str,
        response: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        metric_type: MetricType = MetricType.FAITHFULNESS,
    ) -> MetricValue:
        """Evaluate a single metric synchronously.

        Args:
            query (str): User prompt or query.
            response (str): LLM generated response.
            contexts (List[str]): Retrieved context documents/chunks.
            ground_truth (Optional[str]): Expected golden response.
            metric_type (MetricType): Target metric to compute.

        Returns:
            MetricValue: Evaluated metric result.
        """
        pass

    @abstractmethod
    async def evaluate_metric_async(
        self,
        query: str,
        response: str,
        contexts: List[str],
        ground_truth: Optional[str] = None,
        metric_type: MetricType = MetricType.FAITHFULNESS,
    ) -> MetricValue:
        """Evaluate a single metric asynchronously for scalable non-blocking execution.

        Args:
            query (str): User prompt or query.
            response (str): LLM generated response.
            contexts (List[str]): Retrieved context documents/chunks.
            ground_truth (Optional[str]): Expected golden response.
            metric_type (MetricType): Target metric to compute.

        Returns:
            MetricValue: Evaluated metric result.
        """
        pass


class MetricRegistry:
    """Registry pattern implementation for managing active evaluation providers."""

    def __init__(self) -> None:
        """Initialize empty provider registry."""
        self._providers: Dict[EvaluationProvider, BaseMetricEvaluator] = {}

    def register_provider(self, evaluator: BaseMetricEvaluator) -> None:
        """Register a new metric evaluation provider.

        Args:
            evaluator (BaseMetricEvaluator): Instance of a BaseMetricEvaluator subclass.
        """
        self._providers[evaluator.provider_name] = evaluator

    def get_provider(self, provider: EvaluationProvider) -> Optional[BaseMetricEvaluator]:
        """Retrieve registered metric evaluator by provider enum.

        Args:
            provider (EvaluationProvider): Target provider enum.

        Returns:
            Optional[BaseMetricEvaluator]: Evaluator instance if registered, else None.
        """
        return self._providers.get(provider)

    def list_providers(self) -> List[EvaluationProvider]:
        """List all currently registered provider framework names.

        Returns:
            List[EvaluationProvider]: List of registered provider enums.
        """
        return list(self._providers.keys())


__all__ = [
    "EvaluationProvider",
    "MetricType",
    "PassFailStatus",
    "MetricValue",
    "BaseMetricEvaluator",
    "MetricRegistry",
]
