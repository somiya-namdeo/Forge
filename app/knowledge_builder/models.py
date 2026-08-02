from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat, NonNegativeInt


class PerformanceMetadata(BaseModel):
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0, description="Normalized overall quality score.")
    benchmark_score: float | None = Field(default=None, ge=0.0, le=1.0, description="Normalized benchmark performance score.")
    latency_ms: NonNegativeFloat | None = Field(default=None, description="Typical inference latency in milliseconds.")
    throughput: NonNegativeFloat | None = Field(default=None, description="Approximate throughput (requests per second or equivalent).")

    model_config = ConfigDict(frozen=True)


class PricingMetadata(BaseModel):
    open_source: bool | None = Field(default=None, description="Whether the technology is open source.")
    free_tier: bool | None = Field(default=None, description="Whether a free tier is available.")
    monthly_cost: NonNegativeFloat | None = Field(default=None, description="Estimated monthly operational cost in USD.")
    license: str | None = Field(default=None, description="Primary software license.")

    model_config = ConfigDict(frozen=True)


class AdoptionMetadata(BaseModel):
    github_stars: NonNegativeInt | None = Field(default=None, description="Approximate GitHub star count.")
    monthly_downloads: NonNegativeInt | None = Field(default=None, description="Estimated monthly download count.")
    active_users: NonNegativeInt | None = Field(default=None, description="Estimated active users.")
    enterprise_users: NonNegativeInt | None = Field(default=None, description="Estimated enterprise customers or organizations.")
    community_score: float | None = Field(default=None, ge=0.0, le=1.0, description="Normalized community adoption score.")

    model_config = ConfigDict(frozen=True)


class CapabilityMetadata(BaseModel):
    supported_deployments: list[str] = Field(default_factory=list, description="Supported deployment environments.")
    supported_languages: list[str] = Field(default_factory=list, description="Supported programming languages.")
    features: list[str] = Field(default_factory=list, description="Major supported features or capabilities.")

    model_config = ConfigDict(frozen=True)


class RecommendationMetadata(BaseModel):
    score: float | None = Field(default=None, ge=0.0, le=1.0, description="Overall recommendation score.")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0, description="Confidence associated with the recommendation.")
    reason: str | None = Field(default=None, description="Human-readable recommendation rationale.")

    model_config = ConfigDict(frozen=True)


class TechnologyMetadata(BaseModel):
    technology: str = Field(..., description="Canonical technology identifier.")
    category: str = Field(..., description="Technology category (LLM, Vector DB, Embedding, etc.).")
    description: str | None = Field(default=None, description="Short technology description.")
    aliases: list[str] = Field(default_factory=list, description="Alternative names or aliases.")
    tags: list[str] = Field(default_factory=list, description="Technology tags.")

    performance: PerformanceMetadata = Field(default_factory=PerformanceMetadata, description="Performance characteristics.")
    pricing: PricingMetadata = Field(default_factory=PricingMetadata, description="Pricing and licensing information.")
    adoption: AdoptionMetadata = Field(default_factory=AdoptionMetadata, description="Community adoption statistics.")
    capabilities: CapabilityMetadata = Field(default_factory=CapabilityMetadata, description="Capability metadata.")
    recommendation: RecommendationMetadata = Field(default_factory=RecommendationMetadata, description="Recommendation metadata.")

    model_config = ConfigDict(frozen=True)
