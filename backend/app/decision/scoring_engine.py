"""Candidate scoring engine for AI Architecture Recommendation Engine."""

from typing import Any

from app.schemas.decision import DecisionRequest, Priority

_DEFAULT_NEUTRAL_SCORE = 0.70
_LATENCY_SCALE_MS = 500.0
_COST_SCALE_USD = 100.0
_STARS_SCALE = 5000.0
_DOWNLOADS_SCALE = 100000.0
_USERS_SCALE = 50000.0
_ORGS_SCALE = 1000.0

# Quality field paths (flat + nested)
_QUALITY_PATHS = (
    "quality_score",
    "performance_score",
    "quality",
    "accuracy",
    "benchmark_score",
    "performance.quality_score",
    "performance.score",
    "performance.accuracy",
    "performance.benchmark_score",
    "benchmark.score",
    "benchmark.accuracy",
    "benchmark.quality",
    "recommendation.score",
    "recommendation.quality_score",
    "recommendation.confidence",
)

# Latency field paths (flat + nested)
_LATENCY_PATHS = (
    "latency_ms",
    "latency",
    "p99_latency_ms",
    "performance.latency_ms",
    "performance.inference_latency_ms",
    "performance.p99_latency_ms",
    "performance.latency",
    "benchmark.latency_ms",
    "capabilities.latency_ms",
)

# Cost field paths (flat + nested)
_COST_PATHS = (
    "min_monthly_cost_usd",
    "cost_score",
    "min_cost",
    "monthly_cost",
    "pricing.monthly_cost",
    "pricing.min_monthly_cost_usd",
    "pricing.cost_score",
    "pricing.cost",
    "cost.monthly_cost",
    "cost.min_monthly_cost_usd",
    "cost.score",
    "recommendation.cost_score",
)

_OPEN_SOURCE_PATHS = (
    "open_source",
    "is_open_source",
    "pricing.open_source",
    "pricing.is_open_source",
    "cost.open_source",
)

_FREE_TIER_PATHS = (
    "free_tier",
    "has_free_tier",
    "pricing.free_tier",
    "pricing.has_free_tier",
    "cost.free_tier",
)

# Popularity / Adoption field paths
_POPULARITY_PATHS = (
    "community_score",
    "popularity",
    "adoption.community_score",
    "adoption.popularity",
)

_STARS_PATHS = (
    "stars",
    "github_stars",
    "adoption.stars",
    "adoption.github_stars",
)

_DOWNLOADS_PATHS = (
    "downloads",
    "monthly_downloads",
    "adoption.downloads",
    "adoption.monthly_downloads",
)

_USERS_PATHS = (
    "active_users",
    "adoption.active_users",
)

_ORGS_PATHS = (
    "organizations",
    "enterprise_users",
    "adoption.organizations",
    "adoption.enterprise_users",
)

_PRIORITY_WEIGHTS: dict[Priority, dict[str, float]] = {
    Priority.COST: {"cost": 0.50, "quality": 0.20, "latency": 0.15, "popularity": 0.15},
    Priority.LATENCY: {"latency": 0.50, "quality": 0.25, "cost": 0.15, "popularity": 0.10},
    Priority.QUALITY: {"quality": 0.50, "latency": 0.20, "cost": 0.15, "popularity": 0.15},
    Priority.BALANCED: {"quality": 0.25, "latency": 0.25, "cost": 0.25, "popularity": 0.25},
}


class ScoringEngine:
    """Engine responsible for computing deterministic suitability scores for technology candidates."""

    @staticmethod
    def _get_nested_value(entry: dict[str, Any], path: str) -> Any:
        """Retrieve a value from dictionary using a dot-separated key path."""
        if not isinstance(entry, dict):
            return None
        keys = path.split(".")
        curr: Any = entry
        for k in keys:
            if isinstance(curr, dict) and k in curr:
                curr = curr[k]
            else:
                return None
        return curr

    @classmethod
    def _extract_first_value(cls, entry: dict[str, Any], paths: tuple[str, ...]) -> Any:
        """Retrieve the first non-None value from entry matching flat or nested paths."""
        for path in paths:
            val = cls._get_nested_value(entry, path)
            if val is not None:
                return val
        return None

    @staticmethod
    def _normalize_score(value: Any) -> float | None:
        """Normalize numeric score to [0.0, 1.0], converting percentages (1..100) if needed."""
        if isinstance(value, (int, float)):
            val = float(value)
            if 0.0 <= val <= 1.0:
                return val
            if 1.0 < val <= 100.0:
                return val / 100.0
            if val < 0.0:
                return 0.0
            if val > 100.0:
                return 1.0
        return None

    @classmethod
    def _extract_quality_subscore(cls, entry: dict[str, Any]) -> float | None:
        """Extract quality/performance sub-score normalized to [0.0, 1.0]."""
        quality_val = cls._extract_first_value(entry, _QUALITY_PATHS)
        return cls._normalize_score(quality_val)

    @classmethod
    def _extract_latency_subscore(cls, entry: dict[str, Any]) -> float | None:
        """Extract latency sub-score (lower latency yields higher score)."""
        latency_val = cls._extract_first_value(entry, _LATENCY_PATHS)
        if isinstance(latency_val, (int, float)):
            lat = float(latency_val)
            if lat <= 0:
                return 1.0
            return max(0.0, min(1.0, 1.0 / (1.0 + (lat / _LATENCY_SCALE_MS))))
        return None

    @classmethod
    def _extract_cost_subscore(cls, entry: dict[str, Any]) -> float | None:
        """Extract cost efficiency sub-score (open-source & free-tier yield higher scores)."""
        is_open_source = cls._extract_first_value(entry, _OPEN_SOURCE_PATHS)
        has_free_tier = cls._extract_first_value(entry, _FREE_TIER_PATHS)
        cost_val = cls._extract_first_value(entry, _COST_PATHS)

        subscores: list[float] = []
        if is_open_source is True:
            subscores.append(1.0)
        elif is_open_source is False:
            subscores.append(0.5)

        if has_free_tier is True:
            subscores.append(0.9)

        if isinstance(cost_val, (int, float)):
            cost = float(cost_val)
            if cost <= 0:
                subscores.append(1.0)
            else:
                subscores.append(
                    max(0.0, min(1.0, _COST_SCALE_USD / (_COST_SCALE_USD + cost)))
                )

        if subscores:
            return sum(subscores) / len(subscores)
        return None

    @classmethod
    def _extract_popularity_subscore(cls, entry: dict[str, Any]) -> float | None:
        """Extract community adoption sub-score normalized to [0.0, 1.0]."""
        community_val = cls._extract_first_value(entry, _POPULARITY_PATHS)
        normalized_community = cls._normalize_score(community_val)
        if normalized_community is not None:
            return normalized_community

        stars = cls._extract_first_value(entry, _STARS_PATHS)
        if isinstance(stars, (int, float)):
            return max(0.0, min(1.0, float(stars) / (float(stars) + _STARS_SCALE)))

        downloads = cls._extract_first_value(entry, _DOWNLOADS_PATHS)
        if isinstance(downloads, (int, float)):
            return max(
                0.0, min(1.0, float(downloads) / (float(downloads) + _DOWNLOADS_SCALE))
            )

        users = cls._extract_first_value(entry, _USERS_PATHS)
        if isinstance(users, (int, float)):
            return max(0.0, min(1.0, float(users) / (float(users) + _USERS_SCALE)))

        orgs = cls._extract_first_value(entry, _ORGS_PATHS)
        if isinstance(orgs, (int, float)):
            return max(0.0, min(1.0, float(orgs) / (float(orgs) + _ORGS_SCALE)))

        return None

    @classmethod
    def calculate_score(cls, entry: dict[str, Any], priority: Priority) -> float:
        """Compute a normalized score [0.0, 1.0] for a single candidate entity."""
        weights = _PRIORITY_WEIGHTS.get(priority, _PRIORITY_WEIGHTS[Priority.BALANCED])

        subscores: dict[str, float | None] = {
            "quality": cls._extract_quality_subscore(entry),
            "latency": cls._extract_latency_subscore(entry),
            "cost": cls._extract_cost_subscore(entry),
            "popularity": cls._extract_popularity_subscore(entry),
        }

        weighted_sum = 0.0
        weight_sum = 0.0

        for factor, score in subscores.items():
            if score is not None:
                w = weights[factor]
                weighted_sum += score * w
                weight_sum += w

        if weight_sum > 0:
            final_score = weighted_sum / weight_sum
        else:
            final_score = _DEFAULT_NEUTRAL_SCORE

        return min(1.0, max(0.0, round(final_score, 4)))

    def score_candidates(
        self,
        request: DecisionRequest,
        candidates: dict[str, list[dict[str, Any]]],
    ) -> dict[str, list[dict[str, Any]]]:
        """Score candidate technology entities and return candidates sorted by score descending."""
        scored_candidates: dict[str, list[dict[str, Any]]] = {}

        for category, items in candidates.items():
            scored_items: list[dict[str, Any]] = []

            for item in items:
                item_copy = item.copy()
                item_copy["score"] = self.calculate_score(item_copy, request.priority)
                scored_items.append(item_copy)

            scored_items.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            scored_candidates[category] = scored_items

        return scored_candidates
