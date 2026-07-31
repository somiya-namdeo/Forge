"""
Response schemas for the Forge API.
"""

from pydantic import BaseModel, ConfigDict, Field


class DecisionResponse(BaseModel):
    architecture: str = Field(
        ...,
        description=(
            "Recommended technical architecture and component selection for"
            " the system."
        ),
        examples=[
            "Recommended Architecture:\n- LLM: Qwen-3-32B\n- Embeddings:"
            " BAAI/bge-base-en-v1.5\n- Vector Database: Qdrant\n- Chunking:"
            " Recursive Character Chunking"
        ],
    )
    tradeoffs: str = Field(
        ...,
        description=(
            "Analysis of key technical tradeoffs and risks for the proposed"
            " architecture."
        ),
        examples=[
            "Technical Tradeoffs:\n- Qwen-3-32B offers state-of-the-art"
            " reasoning but requires dedicated GPU infrastructure.\n- Qdrant"
            " provides sub-millisecond retrieval with hybrid search support."
        ],
    )
    recommendation: str = Field(
        ...,
        description="Final executive summary and deployment recommendations.",
        examples=[
            "Executive Summary:\nDeploy the legal document QA pipeline using"
            " Qwen-3-32B orchestrated via LangChain and exposed via FastAPI."
        ],
    )
    confidence: float = Field(
        ...,
        description=(
            "Confidence score (between 0.0 and 1.0) indicating system"
            " certainty."
        ),
        ge=0.0,
        le=1.0,
        examples=[0.95],
    )

    model_config = ConfigDict(
        frozen=True,
        json_schema_extra={
            "example": {
                "architecture": (
                    "Recommended Architecture:\n- LLM: Qwen-3-32B\n-"
                    " Embeddings: BAAI/bge-base-en-v1.5\n- Vector Database:"
                    " Qdrant\n- Chunking: Recursive Character Chunking"
                ),
                "tradeoffs": (
                    "Technical Tradeoffs:\n- Qwen-3-32B offers"
                    " state-of-the-art reasoning but requires GPU"
                    " hosting.\n- Qdrant provides sub-millisecond retrieval."
                ),
                "recommendation": (
                    "Executive Summary:\nDeploy the legal QA pipeline using"
                    " Qwen-3-32B orchestrated via LangChain."
                ),
                "confidence": 0.95,
            }
        },
    )
