from app.knowledge_builder.models import (
    AdoptionMetadata,
    CapabilityMetadata,
    PerformanceMetadata,
    PricingMetadata,
    RecommendationMetadata,
    TechnologyMetadata,
)


class MetadataValidator:
    @staticmethod
    def _clean_list(values: list[str]) -> list[str]:
        cleaned: list[str] = []
        seen: set[str] = set()

        for value in values:
            value = value.strip()
            if not value:
                continue

            lowered = value.lower()
            if lowered in seen:
                continue

            seen.add(lowered)
            cleaned.append(value)

        return cleaned

    @staticmethod
    def _clamp(score: float | None) -> float | None:
        if score is None:
            return None
        return max(0.0, min(1.0, score))

    @classmethod
    def validate(cls, metadata: TechnologyMetadata) -> TechnologyMetadata:
        cleaned_aliases = cls._clean_list(metadata.aliases)
        cleaned_tags = cls._clean_list(metadata.tags)

        capabilities = CapabilityMetadata(
            supported_deployments=cls._clean_list(metadata.capabilities.supported_deployments),
            supported_languages=cls._clean_list(metadata.capabilities.supported_languages),
            features=cls._clean_list(metadata.capabilities.features),
        )

        performance = PerformanceMetadata(
            quality_score=cls._clamp(metadata.performance.quality_score),
            benchmark_score=cls._clamp(metadata.performance.benchmark_score),
            latency_ms=max(0.0, metadata.performance.latency_ms) if metadata.performance.latency_ms is not None else None,
            throughput=max(0.0, metadata.performance.throughput) if metadata.performance.throughput is not None else None,
        )

        pricing = PricingMetadata(
            open_source=metadata.pricing.open_source,
            free_tier=metadata.pricing.free_tier,
            monthly_cost=max(0.0, metadata.pricing.monthly_cost) if metadata.pricing.monthly_cost is not None else None,
            license=metadata.pricing.license,
        )

        adoption = AdoptionMetadata(
            github_stars=metadata.adoption.github_stars,
            monthly_downloads=metadata.adoption.monthly_downloads,
            active_users=metadata.adoption.active_users,
            enterprise_users=metadata.adoption.enterprise_users,
            community_score=cls._clamp(metadata.adoption.community_score),
        )

        recommendation = RecommendationMetadata(
            score=cls._clamp(metadata.recommendation.score),
            confidence=cls._clamp(metadata.recommendation.confidence),
            reason=metadata.recommendation.reason,
        )

        return TechnologyMetadata(
            technology=metadata.technology,
            category=metadata.category,
            description=metadata.description,
            aliases=cleaned_aliases,
            tags=cleaned_tags,
            performance=performance,
            pricing=pricing,
            adoption=adoption,
            capabilities=capabilities,
            recommendation=recommendation,
        )
