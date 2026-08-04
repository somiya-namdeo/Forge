"""Request-scoped Provider Result Cache for Forge Evaluation Module.

Provides a lightweight, request-bound cache storing provider metric evaluation outputs.
Instantiated at the start of EvaluationEngine.evaluate() and cleared upon completion.
"""

from typing import Dict, Optional


class ProviderResultCache:
    """Request-scoped cache for storing external evaluation provider outputs.

    Ensures that a provider (e.g. RAGAS) is executed at most ONCE per evaluation request.
    Calculators read cached outputs, avoiding redundant HTTP calls and model invocations.
    """

    def __init__(self) -> None:
        """Initialize an empty provider result dictionary."""
        self._cache: Dict[str, Dict[str, float]] = {}
        self.writes_count: int = 0
        self.reads_count: int = 0

    def get(self, provider: str, metric_name: str) -> Optional[float]:
        """Get cached metric score for a provider if available.

        Args:
            provider (str): Provider framework name (e.g., "ragas").
            metric_name (str): Metric name (e.g., "faithfulness").

        Returns:
            Optional[float]: Cached score float if present, otherwise None.
        """
        self.reads_count += 1
        provider_data = self._cache.get(provider.lower().strip())
        if provider_data and metric_name.lower().strip() in provider_data:
            return provider_data[metric_name.lower().strip()]
        return None

    def set_provider_results(self, provider: str, results: Dict[str, float]) -> None:
        """Store a dictionary of metric outputs for a provider.

        Args:
            provider (str): Provider framework name.
            results (Dict[str, float]): Dictionary mapping metric names to scores.
        """
        self.writes_count += 1
        normalized_results = {k.lower().strip(): float(v) for k, v in results.items()}
        self._cache[provider.lower().strip()] = normalized_results

    def has_provider(self, provider: str) -> bool:
        """Check if outputs for provider have already been cached.

        Args:
            provider (str): Provider framework name.

        Returns:
            bool: True if provider results exist in cache.
        """
        return provider.lower().strip() in self._cache

    def clear(self) -> None:
        """Clear cache contents."""
        self._cache.clear()
