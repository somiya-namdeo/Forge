"""Constraint matcher module for filtering AI architecture candidates."""

from typing import Any

from app.schemas.decision import DecisionRequest

_DEPLOYMENT_FIELDS = (
    "supported_deployments",
    "deployments",
    "supported_platforms",
    "platforms",
)
_OPEN_SOURCE_FIELDS = ("open_source", "is_open_source")
_GPU_FIELDS = ("gpu_required", "requires_gpu")
_BUDGET_FIELDS = ("min_monthly_cost_usd", "minimum_budget_usd", "min_cost")
_INCOMPATIBLE_FIELDS = (
    "excluded_constraints",
    "incompatible_with",
    "unsupported_constraints",
)

_OPEN_SOURCE_FLAGS = {"open_source", "open-source", "opensource"}
_NO_GPU_FLAGS = {"no_gpu", "no-gpu", "cpu_only", "cpu-only"}


class ConstraintMatcher:
    """Matcher responsible for filtering technology candidates against explicit constraints."""

    @staticmethod
    def _first_available(entry: dict[str, Any], keys: tuple[str, ...]) -> Any:
        """Retrieve the first non-None value from entry matching any key in keys."""
        for key in keys:
            val = entry.get(key)
            if val is not None:
                return val
        return None

    @classmethod
    def _is_deployment_compatible(
        cls, entry: dict[str, Any], target_deployment: str
    ) -> bool:
        """Check if candidate supports the target deployment environment."""
        deployments = cls._first_available(entry, _DEPLOYMENT_FIELDS)
        if deployments is None:
            return True

        if isinstance(deployments, str):
            deployments = [deployments]

        if isinstance(deployments, list):
            lowered = {str(d).strip().lower() for d in deployments}
            return (
                target_deployment in lowered
                or "all" in lowered
                or "any" in lowered
            )

        return True

    @classmethod
    def _is_constraint_compatible(
        cls, entry: dict[str, Any], normalized_constraints: set[str]
    ) -> bool:
        """Check if candidate complies with user-specified constraint flags."""
        if not normalized_constraints:
            return True

        # Open source constraint check
        if normalized_constraints & _OPEN_SOURCE_FLAGS:
            is_open_source = cls._first_available(entry, _OPEN_SOURCE_FIELDS)
            if is_open_source is False:
                return False

        # No GPU constraint check
        if normalized_constraints & _NO_GPU_FLAGS:
            gpu_required = cls._first_available(entry, _GPU_FIELDS)
            if gpu_required is True:
                return False

        # Excluded / incompatible list check
        incompatible = cls._first_available(entry, _INCOMPATIBLE_FIELDS)
        if incompatible and isinstance(incompatible, list):
            lowered_incompatible = {str(item).strip().lower() for item in incompatible}
            if normalized_constraints & lowered_incompatible:
                return False

        return True

    @classmethod
    def _is_budget_compatible(
        cls, entry: dict[str, Any], budget_usd: float | None
    ) -> bool:
        """Check if candidate estimated cost fits within budget constraints."""
        if budget_usd is None:
            return True

        min_cost = cls._first_available(entry, _BUDGET_FIELDS)
        if isinstance(min_cost, (int, float)):
            if min_cost > budget_usd:
                return False

        return True

    @classmethod
    def is_candidate_valid(
        cls, entry: dict[str, Any], request: DecisionRequest
    ) -> bool:
        """Evaluate whether a single candidate entity satisfies all request constraints."""
        target_deployment = request.deployment_target.value.strip().lower()
        if not cls._is_deployment_compatible(entry, target_deployment):
            return False

        normalized_constraints = {
            c.strip().lower() for c in request.constraints if c and c.strip()
        }
        if not cls._is_constraint_compatible(entry, normalized_constraints):
            return False

        if not cls._is_budget_compatible(entry, request.budget_usd):
            return False

        return True

    def apply_constraints(
        self,
        request: DecisionRequest,
        candidates: dict[str, list[dict[str, Any]]],
    ) -> dict[str, list[dict[str, Any]]]:
        """Filter candidate entities according to request deployment, budget, and constraint flags."""
        filtered_candidates: dict[str, list[dict[str, Any]]] = {}

        for category, items in candidates.items():
            valid_items = [
                item.copy()
                for item in items
                if self.is_candidate_valid(item, request)
            ]
            filtered_candidates[category] = valid_items

        return filtered_candidates
