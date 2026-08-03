"""Registry for evaluation metric providers."""

from app.metrics import BaseMetricEvaluator


class MetricRegistry:
    """Registry managing all evaluation providers."""

    def __init__(self) -> None:
        self._providers: dict[str, BaseMetricEvaluator] = {}

    def register(self, provider: BaseMetricEvaluator) -> None:
        """
        Register an evaluation provider.

        Raises:
            ValueError: If provider already exists.
        """
        name = provider.provider_name

        if name in self._providers:
            raise ValueError(
                f"Provider '{name}' is already registered."
            )

        self._providers[name] = provider

    # Backward compatibility
    register_provider = register

    def unregister(self, provider_name: str) -> None:
        """Remove a registered provider."""
        if provider_name not in self._providers:
            raise ValueError(
                f"Provider '{provider_name}' is not registered."
            )

        del self._providers[provider_name]

    def get(self, provider_name: str) -> BaseMetricEvaluator:
        """Return a registered provider."""
        try:
            return self._providers[provider_name]
        except KeyError as exc:
            raise ValueError(
                f"Provider '{provider_name}' is not registered."
            ) from exc

    # Backward compatibility
    get_provider = get

    def exists(self, provider_name: str) -> bool:
        """Check if provider exists."""
        return provider_name in self._providers

    def list_providers(self) -> list[str]:
        """Return all registered provider names."""
        return sorted(self._providers.keys())

    def providers(self) -> dict[str, BaseMetricEvaluator]:
        """Return a copy of the registry."""
        return self._providers.copy()