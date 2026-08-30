"""Abstract base evaluator interface for Forge evaluation providers."""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    pass


class BaseMetricEvaluator(ABC):
    """Abstract base contract for all evaluation providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique provider identifier (e.g. ragas, trulens, custom)."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Human-readable provider name."""
        return self.provider_name

    @property
    @abstractmethod
    def supported_metrics(self) -> Sequence[str]:
        """Metrics supported by this provider."""
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, request: Any) -> Dict[str, float]:
        """
        Evaluate a single RAG response.

        Returns:
            Dictionary mapping metric names to normalized scores.
        """
        raise NotImplementedError

    async def evaluate_async(
        self,
        request: Any,
    ) -> Dict[str, float]:
        """
        Default asynchronous implementation.

        Providers may override this with a native async implementation.
        """
        return self.evaluate(request)