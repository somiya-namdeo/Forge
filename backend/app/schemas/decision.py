"""Schemas for AI Architecture Recommendation Engine."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat, NonNegativeInt


class DeploymentTarget(str, Enum):
    """Supported deployment target environments."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    ON_PREM = "on_prem"
    LOCAL = "local"


class Priority(str, Enum):
    """Supported architectural optimization priorities."""

    COST = "cost"
    QUALITY = "quality"
    LATENCY = "latency"
    BALANCED = "balanced"


class DecisionRequest(BaseModel):
    """User input payload requesting architectural recommendation."""

    project_name: str = Field(..., min_length=1, description="Name of the software project or initiative.")
    project_description: str = Field(..., min_length=1, description="Detailed description of project requirements.")
    expected_users: NonNegativeInt | None = Field(default=None, description="Estimated active user count.")
    document_count: NonNegativeInt | None = Field(default=None, description="Estimated total document count for indexing.")
    budget_usd: NonNegativeFloat | None = Field(default=None, description="Monthly budget limit in USD.")
    deployment_target: DeploymentTarget = Field(..., description="Target hosting infrastructure environment.")
    priority: Priority = Field(..., description="Primary architectural optimization goal.")
    preferred_llm: str | None = Field(default=None, description="Optional preferred foundation model.")
    constraints: list[str] = Field(default_factory=list, description="List of technical or regulatory constraints.")

    model_config = ConfigDict(frozen=True)


class RecommendationItem(BaseModel):
    """Recommendation item for a specific architectural component category."""

    category: str = Field(..., min_length=1, description="Architectural category (e.g. Vector DB, LLM, Reranker).")
    recommended: str = Field(..., min_length=1, description="Recommended technology or model choice.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0.")
    reason: str = Field(..., min_length=1, description="Explanation justifying the recommendation.")
    alternatives: list[str] = Field(default_factory=list, description="Alternative technology choices considered.")

    model_config = ConfigDict(frozen=True)


class DecisionResponse(BaseModel):
    """Output payload containing AI architecture recommendations."""

    recommendations: list[RecommendationItem] = Field(..., description="List of recommended architectural components.")
    summary: str = Field(..., min_length=1, description="Summary overview of recommended architecture.")
    overall_confidence: float = Field(..., ge=0.0, le=1.0, description="Aggregate confidence score between 0.0 and 1.0.")
    generated_at: datetime = Field(..., description="UTC timestamp marking when recommendations were generated.")
    metadata: dict[str, str] = Field(default_factory=dict, description="Additional recommendation metadata.")

    model_config = ConfigDict(frozen=True)
