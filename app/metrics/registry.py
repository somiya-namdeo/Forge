"""Metric registry for managing evaluation provider instances."""

from typing import Any, Dict, List, Optional
from app.metrics import BaseMetricEvaluator, EvaluationProvider


class MetricRegistry:
    """Registry managing evaluation provider instances."""

    def __init__(self) -> None:
        """Initialize empty metric registry."""
        self._providers: Dict[Any, BaseMetricEvaluator] = {}

    def register_provider(self, evaluator: BaseMetricEvaluator) -> None:
        """Register a new metric evaluation provider."""
        name = evaluator.provider_name() if callable(evaluator.provider_name) else evaluator.provider_name
        self._providers[name] = evaluator

    def register(self, provider: BaseMetricEvaluator) -> None:
        """Alias for register_provider."""
        self.register_provider(provider)

    def unregister(self, provider_name: Any) -> None:
        """Unregister an evaluation provider by name."""
        if provider_name not in self._providers:
            raise ValueError(f"Provider '{provider_name}' is not registered.")
        del self._providers[provider_name]

    def get_provider(self, provider: Any) -> Optional[BaseMetricEvaluator]:
        """Retrieve registered metric evaluator by provider enum or name."""
        return self._providers.get(provider)

    def get(self, provider_name: Any) -> BaseMetricEvaluator:
        """Retrieve a registered evaluation provider by name."""
        res = self.get_provider(provider_name)
        if res is None:
            raise ValueError(f"Provider '{provider_name}' is not registered.")
        return res

    def exists(self, provider_name: Any) -> bool:
        """Check whether a provider is registered."""
        return provider_name in self._providers

    def list_providers(self) -> List[Any]:
        """Return list of registered provider names."""
        return list(self._providers.keys())

    def providers(self) -> Dict[Any, BaseMetricEvaluator]:
        """Return a shallow copy of the provider registry."""
        return self._providers.copy()
