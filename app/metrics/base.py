"""Abstract base evaluator interface for Forge evaluation providers."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.schemas.evaluation import EvaluationRequest


class BaseMetricEvaluator(ABC):
    """Abstract base contract for evaluation metric providers."""

    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Return the provider name."""
        return self.provider_name()

    @abstractmethod
    def supported_metrics(self) -> Sequence[str]:
        """Return the sequence of metrics supported by the provider."""
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, request: EvaluationRequest) -> dict[str, float]:
        """Execute synchronous evaluation returning raw metric scores dict."""
        raise NotImplementedError

    @abstractmethod
    async def evaluate_async(self, request: EvaluationRequest) -> dict[str, float]:
        """Execute asynchronous evaluation returning raw metric scores dict."""
        raise NotImplementedError
