"""
Request schemas for the Forge API.
"""

from pydantic import BaseModel, ConfigDict, Field


class DecisionRequest(BaseModel):
    project_description: str = Field(
        ...,
        description=(
            "High-level requirements and specifications for the desired AI"
            " system."
        ),
        examples=[
            "Design an AI-powered legal document question answering system with"
            " high precision retrieval, open-weights reasoning LLM, and high"
            " performance vector search."
        ],
    )

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "project_description": (
                    "Design an AI-powered legal document question answering"
                    " system with high precision retrieval, open-weights"
                    " reasoning LLM, and high performance vector search."
                )
            }
        },
    )
