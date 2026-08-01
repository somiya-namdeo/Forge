"""Metric registry for managing evaluation provider instances."""

from app.metrics.base import BaseMetricEvaluator


class MetricRegistry:
    """Registry managing evaluation provider instances."""

    def __init__(self) -> None:
        """Initialize empty metric registry."""
        self._providers: dict[str, BaseMetricEvaluator] = {}

    def register(self, provider: BaseMetricEvaluator) -> None:
        """Register an evaluation provider instance."""
        name = provider.provider_name()
        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered.")
        self._providers[name] = provider

    def unregister(self, provider_name: str) -> None:
        """Unregister an evaluation provider by name."""
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' is not registered.")
        del self._providers[provider_name]

    def get(self, provider_name: str) -> BaseMetricEvaluator:
        """Retrieve a registered evaluation provider by name."""
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' is not registered.")
        return self._providers[provider_name]

    def exists(self, provider_name: str) -> bool:
        """Check whether a provider is registered."""
        return provider_name in self._providers

    def list_providers(self) -> list[str]:
        """Return list of registered provider names sorted alphabetically."""
        return sorted(self._providers.keys())

    def providers(self) -> dict[str, BaseMetricEvaluator]:
        """Return a shallow copy of the provider registry."""
        return self._providers.copy()
